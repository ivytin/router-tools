#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'tan'

import requests
import threading
from type_recognition import TypeRecognition
from base_crawler import ErrorTimeout
from base_crawler import ErrorPassword

class CrawlerFactory(object):
    """product specifical type crawler"""
    printLock = threading.Lock()

    def __init__(self, addr, port, username, password, debug):
        self.try_username = username
        self.try_password = password
        self.addr = addr

        self.session = requests.session()
        self.router_info = dict()
        self.router_info['addr'] = addr
        self.router_info['port'] = port
        self.router_info['status'] = ''
        self.router_info['server'] = ''
        self.router_info['realm'] = ''
        self.router_info['username'] = ''
        self.router_info['password'] = ''
        self.router_info['firmware'] = ''
        self.router_info['hardware'] = ''
        self.router_info['dns'] = ''
        self.router_info['type'] = ''

        self.debug = debug

    def print_with_lock(self, str):
        self.printLock.acquire()
        print str
        self.printLock.release()

    def produce(self):
        recognition = TypeRecognition()
        try:
            router_type, server, realm = recognition.type_recognition(self.router_info['addr'],
                                                               self.router_info['port'], self.session)
        except ErrorTimeout, e:
            self.print_with_lock(self.addr + ': fail, connect timeout at type recognition')
            self.router_info['status'] = 'offline'
            return self.router_info
        else:
            if server:
                self.router_info['server'] = server
            if realm:
                self.router_info['realm'] = realm

        if self.debug:
            print "router type: " + router_type

        if not router_type:
            self.print_with_lock(self.addr + ': fail, unknown type')
            self.router_info['status'] = 'unknown type'
            if self.debug:
                print self.router_info
            return self.router_info

        self.router_info['type'] = router_type
        crawler_module = __import__(router_type)

        try:
            crawler = crawler_module.Crawler(self.router_info['addr'], self.router_info['port'],
                                             self.try_username, self.try_password, self.session)
        except ErrorTimeout, e:
            self.print_with_lock(self.addr + ': fail, connect timeout at crawler try connect')
            self.router_info['status'] = 'offline'
            return self.router_info

        try:
            dns_info, firmware, hardware = crawler.get_info()
        except ErrorPassword, e:
            self.print_with_lock(self.addr + ': fail, wrong password')
            self.router_info['status'] = 'wrong password'
        except ErrorTimeout, e:
            self.print_with_lock(self.addr + ': fail, timeout during crawling')
            self.router_info['status'] = 'incomplete'
        else:
            self.router_info['username'] = self.try_username
            self.router_info['password'] = self.try_password
            self.router_info['dns'] = dns_info
            self.router_info['firmware'] = firmware
            self.router_info['hardware'] = hardware
            if dns_info or firmware or hardware:
                self.print_with_lock(self.addr + ': success')
                self.router_info['status'] = 'success'

            if self.debug:
                print 'router info:\n', self.router_info
                print '\n\n'
        finally:
            return self.router_info

if __name__ == '__main__':
    crawler_factory = CrawlerFactory('192.168.0.1', 80, 'admin', 'admin', True)
    crawler_factory.produce()
