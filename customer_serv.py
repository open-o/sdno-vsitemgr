#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'liyiqun'

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen
import json
import threading
import traceback

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
            http_req = tornado.httpclient.HTTPRequest(microsrv_cust_url ,method='POST', body = req_body)
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
            @in vsite_uids: query
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
        if input:
            args = {'uids':[x for x in vsite_uids.split(',')]}
        else:
            args = {}
        vsites = {}
        resp = yield self.do_query(microsrv_cust_url,'ms_cust_get_customer', args )
        try:
            resp = json.loads(resp)
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
            @in vsite_uids: query
            @required vsite_uids: True


            @description: Delete a vsite.
            @notes: DELETE vsite/abc
        """
        args = {'uids':[x for x in vsite_uids.split(',')]}
        resp = yield self.do_query(microsrv_cust_url,'ms_cust_del_customer', args)
        self.write('')
        self.finish()

@swagger.model()
class vsite(object):
    def __init__(self, name, ips):
        self.name = name
        self.ips = ips



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
        """
        uid = {}
        try:
            vsite = json.loads(self.request.body)
        except:
            pass

        resp = yield  self.do_query(microsrv_cust_url, 'ms_cust_add_customer', vsite)
        resp = json.loads(resp)
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
        '''
        try:
            vsite = json.loads(self.request.body)
        except:
            pass

        resp = yield  self.do_query(microsrv_cust_url, 'ms_cust_update_customer', vsite)
        self.write('')
        self.finish()


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
        handlers = [(r'/openoapi/sdno-vsite-mgr/v1/vsite/(.+)', vsite_get_handler),
                    (r'/openoapi/sdno-vsite-mgr/v1/vsite', vsite_post_handler)]
                    # (r'/openoapi/sdno-link_flow_monitor/v1/flows/(.+)', flow_rest_handler)]

        super(swagger_app, self).__init__(handlers)
        self.topo_app = topo_app
        self.vlink_attrib_map = {'dequip':'ingress_node_uid', 'sequip':'egress_node_uid',
                                 'dport':'ingress_port_uid', 'sport':'egress_port_uid', 'bandwidth':'bandwidth',
                                 'percentage':'util_ratio'}

        tornado.ioloop.IOLoop.instance().add_timeout(
                        datetime.timedelta(milliseconds=500),
                        openo_register, 'vsite_mgr', 'v1', '/openoapi/sdno-vsite-mgr/v1',
                        '127.0.0.1', te_cust_rest_port )



if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = customer_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(32771)
    swag = swagger_app(app)    # For REST interface
    server_swag = tornado.httpserver.HTTPServer(swag)
    server_swag.listen(te_cust_rest_port)

    tornado.ioloop.IOLoop.instance().start()