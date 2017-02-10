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

__author__ = 'pzhang'

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

from customer_handler import *
from db_util import mysql_utils
import datetime


class customer_app(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', ms_customer_handler)
        ]
        tornado.web.Application.__init__(self, handlers)
        self.ip_cust_map = {}
        self.db = mysql_utils('customer')
        self.split_bits = 8
        tornado.ioloop.IOLoop.instance().add_timeout(
                        datetime.timedelta(milliseconds=500),
                        self.load_ip_cust_map)

        pass


    def split_subnet(self, subnet_int, mask_bit, mask_int):
        step_bits = (32 - self.split_bits)
        if mask_bit >= step_bits:
            return [subnet_int & mask_int]

        nets = []
        net_num = 1 << step_bits - mask_bit
        step = 1 << self.split_bits
        subnet = subnet_int & mask_int
        while net_num > 0:
            nets.append(subnet)
            # print num2ip(subnet)
            subnet += step
            net_num -= 1
            pass

        return nets

    def load_ip_cust_map(self):
        ' Load netip&mask:customer into memory for performance improvement'
        sql_str = 'SELECT * FROM t_customer_ip join t_customer on t_customer_ip.customer_id = t_customer.id'
        res = self.db.exec_sql(sql_str)
        ic_map = {}
        for ip in res:
            nets = self.split_subnet(ip[2], ip[4], ip[5])
            cust = {'cust_uid':str(ip[6]), 'name':ip[7]}

            for n in nets:
                ic_map[n] = cust
            pass

        self.ip_cust_map = ic_map
        tornado.ioloop.IOLoop.instance().add_timeout(
                        datetime.timedelta(milliseconds=1000*60*5),
                        self.load_ip_cust_map)

        pass
