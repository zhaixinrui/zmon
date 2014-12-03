#!/home/zxr/zmon/python/bin/python
#-*- coding:UTF-8 -*-
import redis
import json
import web
import time
import cPickle
import yaml
import os,sys
import logging
import imp
import zmq
import MySQLdb
import socket
import zmonlib
import auth
render = web.template.render('templates')

class MonitorId(object):
    def __init__(self):
        self.input = web.input()
        self.result = {'code':200, 'MONITOR_ID':None, 'msg':''}

    def GET(self):
        logging.debug(self.input)
        product = self.input.get('product')
        monitorname = self.input.get('monitorname')
        if monitorname and product:
            sql = 'select MONITOR_ID from monitor where NAME="%s" and PRODUCT="%s"' % (monitorname, product)
            ret = zmonlib.ExecSql(sql)
            try:
                self.result['MONITOR_ID'] = ret[0][0]
            except:
                self.result['MONITOR_ID'] = None
        else:
            self.result['code'] = 400
            self.result['msg']  = 'Missing Parameters'
        return json.dumps(self.result)


if __name__ == '__main__':
    pass
