#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'pzhang'

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

from customer_app import customer_app


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = customer_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(33771)
    tornado.ioloop.IOLoop.instance().start()