#!/home/zxr/zmon/python/bin/python
import redis
import re
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

class Update(object):
    def __init__(self, input):
        self.input = input
        self.result = {'code':300,'txt':u'未知错误'}

    def update(self):
        if self.input['from'] == 'monitor':
            self.updateMonitor()
        elif self.input['from'] == 'hostlist':
            self.updateHost()
        elif self.input['from'] == 'regularlist':
            self.updateRegular()
        return json.dumps(self.result)

    def updateHost(self):
        pass

    def updateMonitor(self):
        #读用户提交的数据
        monitorId = self.input.get('id', None)
        logPath = self.input.get('LOGPATH', None)
        grep = self.input.get('GREP', None)
        grepv = self.input.get('GREPV', None)
        if monitorId == None or logPath==None or grep==None or grepv==None:
            self.result = {'code':400,'txt':u'未知监控项'}
            return 
        #更新monitor
        sql = "update monitor set LOGPATH='%s',GREP='%s',GREPV='%s' where MONITOR_ID = '%s'" % (logPath, grep.replace('\\','\\\\'), grepv.replace('\\','\\\\'), monitorId)
        zmonlib.ExecSql(sql)
        #重启后端
        ret = zmonlib.controlBackend(monitorId)
        if ret:
            self.result = {'code':200,'txt':u'修改成功'}
        else:
            self.result = {'code':400,'txt':u'重启后端失败'}

    def updateRegular(self):
        #读用户提交的数据
        monitorId = self.input.get('monitorid', None)
        if monitorId == None:
            self.result = {'code':400,'txt':u'未知监控项'}
            return 
        regularId = self.input.get('id', None)
        if regularId == None:
            self.result = {'code':400,'txt':u'未知正则表达式ID'}
            return 
        regularEx = self.input.get('regularex', None)
        if regularEx == None:
            self.result = {'code':400,'txt':u'未知正则表达式'}
            return 
        #正则表达式是否正确
        try:
            r = re.compile(regularEx)
        except Exception,e:
            raise web.internalerror(u'正则表达式有误，请注意检查，错误信息：[%s]'%e)
            return
        #更新正则
        sql = "update regular set EXPRESSION='%s' where REGULAR_ID = '%s'" % (regularEx.replace('\\','\\\\'), regularId)
        zmonlib.ExecSql(sql)
        #重启后端
        ret = zmonlib.controlBackend(monitorId)
        if ret:
            self.result = {'code':200,'txt':u'修改成功'}
        else:
            self.result = {'code':400,'txt':u'重启后端失败'}


if __name__ == '__main__':
   pass 
