#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'tan'

import base64
import re
from base_crawler import BaseCrawler
from base_crawler import ErrorTimeout
from base_crawler import ErrorPassword

class Crawler(BaseCrawler):
    """crawler for Mecury WM serial routers"""
    def __init__(self, addr, port, username, password, session):
        BaseCrawler.__init__(self, addr, port, username, password, session)
        self.res['dns'] = ['/userRpm/StatusRpm.htm', 'var wanPara = new Array(.+?)"([\d\.]+? , [\d\.]+?)"', 2]
        self.res['firmware'] = ['/userRpm/StatusRpm.htm', 'var statusPara = new Array.+?"(.+?)"', 1]
        self.res['hardware'] = ['/userRpm/StatusRpm.htm', 'var statusPara = new Array.+?".+?".+?"(.+?)"', 1]

        auth_cookie = base64.b64encode(self.try_username + ':' + self.try_passwd)
        self.headers = {
            b'Cookie': 'tLargeScreenP=1; subType=pcSub; Authorization=Basic ' + auth_cookie,
            b'User-Agent': b'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
            b'Accept-Language': b'en-US',
            b'Referer': '',
                        }
        self.url = 'http://' + self.addr + ':' + str(port)

    def get_info(self):
        dns_info = ''
        firmware = ''
        hardware = ''
        r = self.connect_auth_with_headers(self.url, 1)

        if r.status_code == 403:
            raise ErrorPassword

        dns_url = 'http://' + self.addr + ':' + str(self.port) + self.res['dns'][0]
        self.headers['Referer'] = self.url
        try:
            r = self.connect_auth_with_headers(dns_url, 1)
        except ErrorTimeout, e:
            pass
        else:
            dns_pattern = re.compile(self.res['dns'][1], re.I | re.S)
            dns_match = dns_pattern.search(r.content)
            if dns_match:
                dns_info = dns_match.group(self.res['dns'][2])

        firmware_url = 'http://' + self.addr + ':' + str(self.port) + self.res['firmware'][0]
        if firmware_url == dns_url:
            firmware_pattern = re.compile(self.res['firmware'][1], re.I | re.S)
            firmware_match = firmware_pattern.search(r.content)
            if firmware_match:
                firmware = firmware_match.group(self.res['firmware'][2])
        else:
            try:
                r = self.connect_auth_with_headers(firmware_url, 1)
            except ErrorTimeout, e:
                pass
            else:
                firmware_pattern = re.compile(self.res['firmware'][1], re.I | re.S)
                firmware_match = firmware_pattern.search(r.content)
                if firmware_match:
                    firmware = firmware_match.group(self.res['firmware'][2])

        hardware_url = 'http://' + self.addr + ':' + str(self.port) + self.res['hardware'][0]
        if hardware_url == firmware_url:
            hardware_pattern = re.compile(self.res['hardware'][1], re.I | re.S)
            hardware_match = hardware_pattern.search(r.content)
            if hardware_match:
                hardware = hardware_match.group(self.res['hardware'][2])
        else:
            try:
                r = self.connect_auth_with_headers(hardware_url, 1)
            except ErrorTimeout, e:
                pass
            else:
                hardware_pattern = re.compile(self.res['hardware'][1], re.I | re.S)
                hardware_match = hardware_pattern.search(r.content)
                if hardware_match:
                    hardware = hardware_match.group(self.res['hardware'][2])

        return dns_info, firmware, hardware

if __name__ == '__main__':
    """Test this unit"""
    req = __import__('requests')
    crawler = Crawler('192.168.0.1', 80, 'admin', 'admin', req.session, True)
    crawler.get_info()