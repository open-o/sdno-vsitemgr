#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2016, China Telecommunication Co., Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from _mysql import result
from MySQLdb.constants.CR import IPSOCK_ERROR

__author__ = 'pzhang'

import tornado.web
import json
import time
from db_util import mysql_utils

ip2num = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])

num2ip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])

def get_mask_int(mask):
    sum=0
    for i in range(mask):
        sum = sum*2+1
    sum = sum << (32-mask)
    return sum

class ms_customer_handler(tornado.web.RequestHandler):
    def initialize(self):
        super(ms_customer_handler, self).initialize()
        self.resp_func = {'ms_cust_get_customer':self.get_customer, 
                          'ms_cust_add_customer':self.add_customer,
                          'ms_cust_del_customer':self.del_customer, 
                          'ms_cust_update_customer':self.update_customer,
                          'ms_cust_get_customer_by_ip':self.get_customer_by_ip,
                          'ms_cust_add_flow':self.add_flow,
                          'ms_cust_del_flow':self.del_flow,
                          'ms_cust_update_flow':self.update_flow,
                          'ms_cust_set_flow_speed':self.set_flow_speed
                          }
        self.log = 0
        self.ip_cust_map = {}
        pass


    def form_response(self, req):
        resp = {}
        resp['response'] = req['request']
        #resp['ts'] = req['ts']
        resp['ts'] = time.strftime("%Y%m%d%H%M%S")
        resp['trans_id'] = req['trans_id']
        resp['err_code'] = 0
        resp['msg'] = ''
        self.set_header('Content-Type', 'application/json')
        return resp
    
    def post(self):
        ctnt = self.request.body
        if self.log == 1:
            print 'The request:'
            print  str(ctnt)

        req = json.loads(str(ctnt))
        resp = self.form_response(req)

        result = self.resp_func[req['request']](req['args'])
        resp['result'] = result

        if self.log == 1:
            print 'response:'
            print json.dumps(resp)
        self.write(json.dumps(resp))
        pass

    def array_to_inlist(self, arr):
        lst = '(' + ",".join(arr) + ')'
        return lst

    def get_customer(self, args):

        customers = {}
        sql_str = 'select * from t_customer join t_customer_ip on t_customer_ip.customer_id = t_customer.id'
        if 'uids' in args:
            uids = args['uids']
            lst = self.array_to_inlist(uids)
            sql_str += ' where t_customer.id in' + lst
        db = mysql_utils('customer')
        results = db.exec_sql(sql_str)
        db.close()

        if results is None:
            return {'customers':[]}
        cs_map = {}
        cs = []
        for c in results:
            uid = str(c[0])
            if uid in cs_map:
                one_c = cs_map[uid]
            else:
                one_c = {'uid':str(c[0]), 'name':c[1] }
                cs_map[uid] = one_c
            ip = str(c[6]) + '/' + str(c[7])
            if 'ips' in one_c:
                one_c['ips'].append({'src':ip, 'uid':str(c[3])})
            else:
                one_c['ips'] = [{'src':ip,  'uid':str(c[3])}]
            pass

        cs = [cs_map[c] for c in cs_map]

        customers['customers'] = cs
        return customers

    def del_customer(self, args):
        uids = args['uids']
        lst = self.array_to_inlist(uids)
        sql_str = 'delete from t_customer where t_customer.id in %s' % lst
        # print sql_str

        db = mysql_utils('customer')
        result = db.exec_sql(sql_str)
        if not result:
            db.commit()
        db.close()
        return result
    
    def add_customer(self, args):
        customer = {}
        customer['name'] = args['name']
        #customer['uid'] = args['uid']
        #print customer

        #insert into t_customer values (1, 'Google');
        #sql_str = 'insert into t_customer(id,name) values (%s, \'%s\')' % (customer['uid'], customer['name'])
        sql_str = 'insert into t_customer(name) values (\'%s\')' % customer['name']
        #print sql_str
        db = mysql_utils('customer')
        result = db.exec_sql(sql_str)
        if not result:
            db.commit()
        customer_id = db.exec_sql('SELECT LAST_INSERT_ID()')[0][0]
        #print customer_id
        #insert into t_customer_ip values (1, 1, 16843009, '1.1.1.0', 4294967040, '255.255.255.0');
        if args.has_key('ips'):
            ips = args['ips']
            for ip in ips:
                ip_addr = ip['src'].split('/')[0]
                ip_mask = int(ip['src'].split('/')[1])
                sql_str = 'insert into t_customer_ip(customer_id,netip,netip_str,mask_bit,mask_int) values (%s, %s, \'%s\', %s, %s)' \
                    % (customer_id, ip2num(ip_addr), ip_addr, ip_mask, get_mask_int(ip_mask))
                print sql_str
                result = db.exec_sql(sql_str)
                if not result:
                    db.commit()
        db.close()
        return {"cust_uid": customer_id}
    
    def update_customer(self,args):
        customer = {}
        name = args['name']
        uid = args['uid']
        if args.has_key('ips'):
            ips = args['ips']
            
        #check if customer exist
        sql_str = 'select * from t_customer where id = %s' % uid

        db = mysql_utils('customer')
        result = db.exec_sql(sql_str)
        #print result
        #if not exist
        if not result:
            sql_str = 'insert into t_customer (id, name) VALUES (%s, \'%s\')' % (uid, name)
            ret = db.exec_sql(sql_str)
            db.commit()
        #if exist
        else:
           sql_str = 'update t_customer set name = \'%s\' where id = %s' % (name, uid)
           print sql_str
           db.exec_sql(sql_str)
           db.commit()
           pass
        db.close()
        # To pzhang: Are you crazy?
        # self.del_customer(args)
        # self.add_customer(args)
        
        pass
    
    def get_customer_by_ip(self, args):
        ips = args['ips']
        cs = {}

        for ip in ips:
            # sql_str = 'select * from t_customer_ip inner join t_customer on t_customer_ip.customer_id = t_customer.id ' + \
            #     'and t_customer_ip.netip & t_customer_ip.mask_int = %s & t_customer_ip.mask_int' % ip2num(ip)
            # results = self.db.exec_sql(sql_str)
            # if results:
            #     # print results
            #     cs[ip] = {'name':results[0][7], 'cust_uid':results[8]}
            times = self.application.split_bits
            mask = 0xFFFFFFFF
            match = 0
            nets = self.application.ip_cust_map
            sub_ip = ip2num(ip)
            while times > 0:
                if sub_ip in nets:
                    match = 1
                    break
                mask <<= 1
                sub_ip &= mask
                times -= 1

            if match:
                cs[ip] = nets[sub_ip]
            pass

        return cs


    def add_flow(self,args):
        customer = {}
        customer_id = args['cust_uid']

        #check if customer exist
        sql_str = 'select * from t_customer where id=%s' % customer_id
        db = mysql_utils('customer')
        result = db.exec_sql(sql_str)
        if not result:
            return 

        #insert into t_customer_ip values (1, 1, 16843009, '1.1.1.0', 4294967040, '255.255.255.0');
        flows = []
        if args.has_key('flows'):
            ips = args['flows']
            for ip in ips:
                one_flow = {}
                one_flow['src'] = ip['src']
                ip_addr = ip['src'].split('/')[0]
                ip_mask = int(ip['src'].split('/')[1])
                sql_str = 'insert into t_customer_ip(customer_id,netip,netip_str,mask_bit,mask_int) values (%s, %s, \'%s\', %s, %s)' \
                    % (customer_id, ip2num(ip_addr), ip_addr, ip_mask, get_mask_int(ip_mask))
                print sql_str
                result = db.exec_sql(sql_str)
                if not result:
                    db.commit()
                    flow_id = db.exec_sql('SELECT LAST_INSERT_ID()')[0][0]
                    ip['uid'] = str(flow_id)

        db.close()
        #return the request object. the only difference is each added flow has 'uid' attrib
        return args

    def del_flow(self,args):
        uids = args['flow_uids']
        lst = self.array_to_inlist(uids)
        sql_str = 'delete from t_customer_ip where t_customer_ip.id in %s' % lst
        # print sql_str
        db = mysql_utils('customer')
        result = db.exec_sql(sql_str)
        if not result:
            db.commit()
        db.close()
        return result
    
    def update_flow(self,args):
        flows = args['flows']
        db = mysql_utils('customer')
        for flow in flows:
            flow_id = flow['uid']
            if 'src' in flow:
                ip_addr = flow['src'].split('/')[0]
                ip_mask = int(flow['src'].split('/')[1])
                sql_str = 'update t_customer_ip set netip=%s,netip_str=\'%s\',mask_bit=%s,mask_int=%s where t_customer_ip.id=%s' \
                % (ip2num(ip_addr), ip_addr, ip_mask, get_mask_int(ip_mask), flow_id)
                print sql_str
                result = db.exec_sql(sql_str)
                if not result:
                    db.commit()
            pass
        db.close()
        pass
    
    def set_flow_speed(self,args):
        pass