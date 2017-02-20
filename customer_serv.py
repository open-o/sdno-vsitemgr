#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2016-2017 China Telecommunication Co., Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

__author__ = 'liyiqun'

import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options
import tornado.web
import tornado.httpclient
import tornado.gen
import json
import threading
import traceback
import os
import os.path
from topofetch import *
from jsonrpc import *
from microsrvurl import *
from test import *
import datetime
from common import *
from tornado_swagger import swagger
from base_handler import base_handler

swagger.docs()

class customer_handler(tornado.web.RequestHandler):
    def initialize(self):
        super(customer_handler, self).initialize()
        self.subreq_map = {'customer_man_get_customer': 'ms_cust_get_customer',
                           'customer_man_del_customer': 'ms_cust_del_customer',
                           'customer_man_add_customer': 'ms_cust_add_customer',
                           'customer_man_update_customer': 'ms_cust_update_customer',
                           'customer_man_add_flow':'ms_cust_add_flow',
                           'customer_man_del_flow': 'ms_cust_del_flow',
                           'customer_man_update_flow': 'ms_cust_update_flow'}

        self.log = 0
        pass

    def form_response(self, req):
        resp = {}
        resp['response'] = req['request']
        resp['ts'] = req['ts']
        resp['trans_id'] = req['trans_id']
        resp['err_code'] = 0
        resp['msg'] = ''
        return resp

    def cust_subreq(self, req, method):
        rpc = base_rpc('')
        rpc.form_request(method, req['args'])
        return json.dumps(rpc.request_body)

    def cb_get_customer(self, ms_resp):
        try:
            resp = self.form_response(self.req)
            ms_resp = json.loads(ms_resp.body)
            resp['err_code'] = ms_resp['err_code']
            resp['msg'] = ms_resp['msg']
            resp['result'] = ms_resp['result']

            self.write(json.dumps(resp))
            self.finish()

        except Exception, data:
            print 'Fetch customer error'
            print str(Exception) + ':' + str(data)
            traceback.print_exc()
            self.write('Internal Server Error')
            self.finish()

    def get(self):
        self.write('You Fuck Off')
        return

    @tornado.web.asynchronous
    def post(self):
        try:
            ctnt = self.request.body
            req = json.loads(str(ctnt))
            self.req = req
            resp = self.form_response(req)
            res = None
            if 'request' not in req or req['request'] not in self.subreq_map:
                resp['err_code'] = -1
                resp['msg'] = 'Unrecognised method'
                self.write(json.dumps(resp))
                self.finish()
                return

            req_body = self.cust_subreq(req, self.subreq_map[req['request']])
            http_req = tornado.httpclient.HTTPRequest(microsrvurl_dict['microsrv_cust_url'] ,method='POST', body = req_body)
            client = tornado.httpclient.AsyncHTTPClient()
            client.fetch(http_req, callback = self.cb_get_customer)
        except Exception, data:
            print str(Exception) + str(data)
            self.write('Internal Server Error')
            self.finish()
            traceback.print_exc()

    pass

class vsite_get_handler(base_handler):
    def initialize(self):
        super(vsite_get_handler, self).initialize()
        pass


    @tornado.gen.coroutine
    @swagger.operation(nickname='get_vsite')
    def get(self, vsite_uids):
        """
            @param vsite_uids:
            @type vsite_uids: L{string}
            @in vsite_uids: path
            @required vsite_uids: False

            @rtype: list of vsites
            Example:<br />
            {"vsites": [{"ips": [{"src": "123.10.88.0/24", "dst": "10.10.20.0/24"}, {"src": "123.11.88.0/24", "dst": "10.11.20.0/24"}], "name": "CT_BJ", "uid": "abc123"}]}
            <br /> <br />
            name: The name of a virtual site (collection of IP subnets)  <br />
            ips: list of IP flow characteristics. only source and destination IP pattern are supported in current version.  <br />
            uid: universal id of the vsite <br />


            @description: Get vsite information. If the vsite_uids exists, return the desired vsites, otherwise return all
            the available vsites.
            @notes: GET vsite/abc,def or  GET vsite/
        """
        if vsite_uids:
            args = {'uids':[x for x in vsite_uids.split(',')]}
        else:
            args = {}
        vsites = {}
        resp = yield self.do_query(microsrvurl_dict['microsrv_cust_url'],'ms_cust_get_customer', args )
        try:
            result = resp['result']
            vsites = {'vsites':result['customers']} if 'customers' in result else {}
        except:
            pass

        self.write(json.dumps(vsites))
        self.finish()

    @tornado.gen.coroutine
    @swagger.operation(nickname='delete_vsite')
    def delete(self, vsite_uids):
        """
            @param vsite_uids:
            @type vsite_uids: L{string}
            @in vsite_uids: path
            @required vsite_uids: True


            @description: Delete a vsite.
            @notes: DELETE vsite/abc
            @return 200: deleted ok.
        """
        args = {'uids':[x for x in vsite_uids.split(',')]}
        resp = yield self.do_query(microsrvurl_dict['microsrv_cust_url'],'ms_cust_del_customer', args)
        self.write('')
        self.finish()

@swagger.model()
class vsite(object):
    def __init__(self, name, ips):
        self.name = name
        self.ips = ips

@swagger.model()
class flow(object):
    def __init__(self, vsite_uid, src_ip, dst_ip = '', uid = None):
        self.vsite_uid = vsite_uid
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.uid = uid

class vsite_post_handler(base_handler):
    def initialize(self):
        super(vsite_post_handler, self).initialize()
        pass


    @tornado.gen.coroutine
    @swagger.operation(nickname='add_vsite')
    def post(self):
        """
            @param body: create a vsite
            @type body: L{vsite}
            @in body: body

            @rtype: {"vsite_uid":""}
            The unique id of the new added vsite  <br />


            @description: Add a new vsite
            @notes: POST vsite/
            <br /> request body sample <br />
            {"ips": [{"src": "10.0.218.0/24"}], "name": "vsite_sample"}
        """
        vsite = {}
        uid = {}
        try:
            vsite = json.loads(self.request.body)
        except:
            pass

        resp = yield  self.do_query(microsrvurl_dict['microsrv_cust_url'], 'ms_cust_add_customer', vsite)
        result = resp['result']
        if 'cust_uid' in result:
            uid['vsite_uid'] = result['cust_uid']
        self.write(json.dumps(uid))
        self.finish()

    @tornado.gen.coroutine
    @swagger.operation(nickname='update_vsite')
    def put(self):
        '''
            @param body: update a vsite
            @type body: L{vsite}
            @in body: body
            @return 200: vsite was updated.
            @raise 500: invalid input
            @description: update a vsite
            @notes: PUT vsite/
            <br /> request body sample <br />
            {"ips": [{"src": "10.0.218.0/24"}], "uid":"19","name": "vsite_sample_2"}
        '''
        try:
            vsite = json.loads(self.request.body)
        except:
            pass

        resp = yield  self.do_query(microsrvurl_dict['microsrv_cust_url'], 'ms_cust_update_customer', vsite)
        self.write('')
        self.finish()

class flow_get_handler(base_handler):
    @tornado.gen.coroutine
    @swagger.operation(nickname='delete_flow')
    def delete(self, flow_uids):
        """
            @param flow_uids:
            @type flow_uids: L{string}
            @in flow_uids: path
            @required flow_uids: True

            @rtype:

            @description: Delete flow spec from a vsite.
            @notes: DELETE flow/xxx,yyy
            @return 200: deleted ok.
        """
        fids = flow_uids.split(',')
        resp = self.do_query(microsrvurl_dict['microsrv_cust_url'], 'ms_cust_del_flow', {'flow_uids':fids})
        self.write('')
        self.finish()
    pass

class flow_post_handler(base_handler):
    @tornado.gen.coroutine
    @swagger.operation(nickname='add_flow')
    def post(self):
        """
            @param body: create flow spec for a vsite
            @type body: L{flow}
            @in body: body

            @rtype: {"flow_uid":""}
            The unique id of the new added flow spec  <br />


            @description: Add a new flow spec
            @notes: POST flow/
            @notes:
            <br /> request body sample <br />
            {"src_ip": "192.168.212.0/24", "dst_ip":"","vsite_uid": "19"}
        """
        rpc_flow = None
        try:
            flow = json.loads(self.request.body)
            rpc_flow = {'cust_uid':flow['vsite_uid'], 'flows':[{'src':flow['src_ip'],
                                'dst':flow['dst_ip'] if 'dst_ip' in flow else ''}]}
        except:
            pass

        uid = {}
        if rpc_flow:
            resp = yield  self.do_query(microsrvurl_dict['microsrv_cust_url'], 'ms_cust_add_flow', rpc_flow)
            result = resp['result']
            if result is not None and 'flows' in result:
                uid['flow_uid'] = result['flows'][0]['uid']
        self.write(json.dumps(uid))
        self.finish()

    @tornado.gen.coroutine
    @swagger.operation(nickname='update_flow')
    def put(self):
        '''
            @param body: update a flow
            @type body: L{flow}
            @in body: body
            @return 200: flow was updated.
            @raise 500: invalid input
            @description: update a flow. Note that the 'uid' attribute of the flow is mandatory for this API.
            @notes:
            <br /> request body sample <br />
            {"src_ip": "192.111.218.0/24", "dst_ip":"", "uid": 9, "vsite_uid": "19"}
        '''
        rpc_flow = {}
        try:
            flow = json.loads(self.request.body)
            rpc_flow = {'cust_uid':flow['vsite_uid'], 'flows':[{'src':flow['src_ip'],
                                'dst':flow['dst_ip'] if 'dst_ip' in flow else '', 'uid':flow['uid']}]}
        except:
            pass

        resp = yield  self.do_query(microsrvurl_dict['microsrv_cust_url'], 'ms_cust_update_flow', rpc_flow)
        self.write('')
        self.finish()

    pass

class customer_app(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', customer_handler),
        ]

        settings = {
            'template_path': 'templates',
            'static_path': 'static'
        }

        tornado.web.Application.__init__(self, handlers, **settings)
        pass


class swagger_app(swagger.Application):
    def __init__(self, topo_app):
        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'sdnovsitemgr.swagger')
        }

        handlers = [(r'/openoapi/sdnovsitemgr/v1/vsite/(.*)', vsite_get_handler),
                    (r'/openoapi/sdnovsitemgr/v1/vsite', vsite_post_handler),
                    (r'/openoapi/sdnovsitemgr/v1/flow/(.+)', flow_get_handler),
                    (r'/openoapi/sdnovsitemgr/v1/flow', flow_post_handler),
                    (r'/openoapi/sdnovsitemgr/v1/(swagger.json)', tornado.web.StaticFileHandler, dict(path=settings['static_path']))
                    ]

        super(swagger_app, self).__init__(handlers, **settings)
        self.topo_app = topo_app
        self.vlink_attrib_map = {'dequip':'ingress_node_uid', 'sequip':'egress_node_uid',
                                 'dport':'ingress_port_uid', 'sport':'egress_port_uid', 'bandwidth':'bandwidth',
                                 'percentage':'util_ratio'}

        tornado.ioloop.IOLoop.instance().add_timeout(
                        datetime.timedelta(milliseconds=500),
                        openo_register, 'vsite_mgr', 'v1', '/openoapi/sdnovsitemgr/v1',
                        microsrvurl_dict['te_cust_rest_host'], microsrvurl_dict['te_cust_rest_port'] )


def launch():
    app = customer_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(32771)
    swag = swagger_app(app)    # For REST interface
    server_swag = tornado.httpserver.HTTPServer(swag)
    server_swag.listen(microsrvurl_dict['te_cust_rest_port'])

    tornado.ioloop.IOLoop.instance().start()


def strip_parse_from_argv():
    options.define("uniq", default="2837492392992771", help="service unique id")
    options.define("localurl", default=microsrvurl_dict['te_cust_rest_host'] + te_host_port_divider + str(microsrvurl_dict['te_cust_rest_port']), help="service host:port")
    options.define("msburl", default=microsrvurl_dict['te_msb_rest_host'] + te_host_port_divider + str(microsrvurl_dict['te_msb_rest_port']), help="micro service bus host:port")
    tornado.options.parse_command_line()
    microsrvurl_dict['te_cust_rest_host'] = options.localurl.split(':')[0]
    microsrvurl_dict['te_cust_rest_port'] = int(options.localurl.split(':')[1])
    microsrvurl_dict['openo_ms_url'] = te_protocol + options.msburl + openo_ms_url_prefix
    microsrvurl_dict['openo_dm_url'] = te_protocol + options.msburl + openo_dm_url_prefix
    microsrvurl_dict['openo_esr_url'] = te_protocol + options.msburl + openo_esr_url_prefix
    microsrvurl_dict['openo_brs_url'] = te_protocol + options.msburl + openo_brs_url_prefix

    pass

if __name__ == '__main__':
    strip_parse_from_argv()
    launch()
