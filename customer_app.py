#!/usr/bin/python
# -*- coding: utf-8 -*-

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
            cust = {'uid':str(ip[6]), 'name':ip[7]}

            for n in nets:
                ic_map[n] = cust
            pass

        self.ip_cust_map = ic_map
        tornado.ioloop.IOLoop.instance().add_timeout(
                        datetime.timedelta(milliseconds=100000),
                        self.load_ip_cust_map)

        pass
