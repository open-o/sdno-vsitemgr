#!/usr/bin/python
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

from tornado.testing import *
from base_handler import *
from microsrvurl import  *
import customer_serv
import customer_server
import multiprocessing
import time
import os
import subprocess
import threading
cus_serv_cmd = 'coverage run --parallel-mode customer_serv.py'
cus_server_cmd = 'coverage run --parallel-mode customer_server.py'
fake_openo_serv_cmd = 'coverage run --parallel-mode fake_openo.py'
# os.system(command)

vsitemgr_prefix_vsite_uri = r'http://127.0.0.1:8600/openoapi/sdnovsitemgr/v1/vsite'
#vsite ids
vsitemgr_vsite_uri_param = '0'
vsitemgr_prefix_flow_uri = r'http://127.0.0.1:8600/openoapi/sdnovsitemgr/v1/flow'
#flow ids
vsitemgr_flow_uri_param = '0'

class Test_Vsitemgr(AsyncTestCase):
    def setUp(self):
        super(Test_Vsitemgr,self).setUp()
        pass

    def tearDown(self):
        super(Test_Vsitemgr,self).tearDown()

    @tornado.testing.gen_test
    def test_i_delete_vsite(self):
        print('test_delete_vsite:')
        code, resp = yield base_handler.do_json_get(vsitemgr_prefix_vsite_uri + '/' + vsitemgr_vsite_uri_param, metd='DELETE')
        self.assertEqual(200, code, 'FAIL:test_delete_vsite, vsite deleted not 200')

    @tornado.testing.gen_test
    def test_h_delete_flow(self):
        print('test_delete_flow:')
        code, resp = yield base_handler.do_json_get(vsitemgr_prefix_flow_uri + '/' + vsitemgr_flow_uri_param, metd='DELETE')
        self.assertEqual(200, code, 'FAIL:test_delete_flow, flow deleted not 200')

    @tornado.testing.gen_test
    def test_g_get_vsite(self):
        code, resp = yield base_handler.do_json_get(vsitemgr_prefix_vsite_uri + '/' + vsitemgr_vsite_uri_param)
        print('test_get_vsite:')
        self.assertIn('vsites', resp, 'FAIL:test_get_vsite, key \'vsites\' not found')

    @tornado.testing.gen_test
    def test_f_put_flow(self):
        print('test_put_flow:')
        #req:{"src_ip": "222.222.111.0/24", "dst_ip":"","vsite_uid": "19","uid": "107"}
        req_body = {"src_ip": "222.222.111.0/24", "dst_ip":"","vsite_uid": vsitemgr_vsite_uri_param,"uid": vsitemgr_flow_uri_param}
        code, resp = yield base_handler.do_json_post(vsitemgr_prefix_flow_uri, req_body, metd='PUT')
        self.assertEqual(200, code, 'FAIL:test_put_flow, flow updated not 200')

    @tornado.testing.gen_test
    def test_e_post_flow(self):
        print('test_post_flow:')
        #req:   {"src_ip": "222.222.222.0/24", "dst_ip":"","vsite_uid": "19"}
        #resp:  {"flow_uid": "107"}
        req_body = {"src_ip": "222.222.222.0/24", "dst_ip":"","vsite_uid": vsitemgr_vsite_uri_param}
        code, resp = yield base_handler.do_json_post(vsitemgr_prefix_flow_uri, req_body)
        if 'flow_uid' in resp:
            global vsitemgr_flow_uri_param
            vsitemgr_flow_uri_param = resp['flow_uid']
        self.assertIn('flow_uid', resp, 'FAIL:test_post_flow, key \'flow_uid\' not found')

    @tornado.testing.gen_test
    def test_d_get_vsite(self):
        code, resp = yield base_handler.do_json_get(vsitemgr_prefix_vsite_uri + '/' + vsitemgr_vsite_uri_param)
        print('test_get_vsite:')
        self.assertIn('vsites', resp, 'FAIL:test_get_vsite, key \'vsites\' not found')

    @tornado.testing.gen_test
    def test_c_put_vsite(self):
        print('test_put_vsite:')
        req_body = {"uid":vsitemgr_vsite_uri_param,"name": "vsite_test_sample2"}
        code, resp = yield base_handler.do_json_post(vsitemgr_prefix_vsite_uri, req_body, metd='PUT')
        self.assertEqual(200, code, 'FAIL:test_put_vsite, vsite updated not 200')

    @tornado.testing.gen_test
    def test_b_get_vsite(self):
        code, resp = yield base_handler.do_json_get(vsitemgr_prefix_vsite_uri + '/' + vsitemgr_vsite_uri_param)
        print('test_get_vsite:')
        self.assertIn('vsites', resp, 'FAIL:test_get_vsite, key \'vsites\' not found')

    @tornado.testing.gen_test
    def test_a_post_vsite(self):
        print('test_post_vsite:')
        #req:   {"ips": [{"src": "10.0.218.0/24"}], "name": "vsite_sample"}
        #resp:  {"vsite_uid": 43}
        req_body = {"ips": [{"src": "10.0.218.0/24"}], "name": "vsite_test_sample"}
        code, resp = yield base_handler.do_json_post(vsitemgr_prefix_vsite_uri, req_body)
        if 'vsite_uid' in resp:
            global vsitemgr_vsite_uri_param
            vsitemgr_vsite_uri_param = str(resp['vsite_uid'])
        self.assertIn('vsite_uid', resp, 'FAIL:test_post_vsite, key \'vsite_uid\' not found')

class start_test_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self): #Overwrite run() method, put what you want the thread do here
        print '----'
        os.system(cus_serv_cmd)
        time.sleep(3)
        os.system(cus_server_cmd)
        time.sleep(3)
        suite = unittest.TestLoader().loadTestsFromTestCase(Test_Vsitemgr)
        unittest.TextTestRunner(verbosity=2).run(suite)
        print '++++'
        exit()
        print '@@@@'

def stat_serv():
    # os.system(cus_serv_cmd)
    # os.popen.(cus_serv_cmd)
    subprocess.Popen(cus_serv_cmd, shell=True)
    pass

def stat_server():
    subprocess.Popen(cus_server_cmd, shell=True)
    pass

if __name__ == '__main__':
    print '---Service Started....'
    # os.system('coverage erase')
    p_serv = subprocess.Popen(cus_serv_cmd, shell=True)
    p_server = subprocess.Popen(cus_server_cmd, shell=True)
    fake_serv = subprocess.Popen(fake_openo_serv_cmd, shell=True)
    time.sleep(3)
    # my = start_test_thread()
    # my.start()
    print(p_server.pid)
    print(p_serv.pid)
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Vsitemgr)
    unittest.TextTestRunner(verbosity=2).run(suite)
    try:
        print '---Service Terminated...'
        p_server.send_signal(2)#signal.SIGINT
        p_serv.send_signal(2)#signal.SIGINT
        fake_serv.send_signal(2)
        print '@@@Service Terminated...'
        pass
    except:
        print '*****Service Terminated...'
        traceback.print_exc()
        pass
    print(p_server.pid)
    print(p_serv.pid)
    # print '@@@Service Terminated...'
    # os.system('tskill python')
    # print '$$$Service Terminated...'
    # subprocess.Popen('tskill python & tskill python', shell=True)
    # os.system('coverage combine & coverage html')
    # p_server.terminate()
    # p_serv.terminate()
    print '+++Service Terminated...'
