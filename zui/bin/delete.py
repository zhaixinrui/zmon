#!/home/zxr/zmon/python/bin/python
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

class Delete(object):
    def __init__(self, input):
        self.input = input
        self.result = {'code':300,'txt':'unknown error'}
        zmonlib.Init()

    def delete(self):
        if self.input['from'] == 'monitor':
            self.deleteMonitor()
        elif self.input['from'] == 'hostlist':
            #self.deleteHost()
            pass
        elif self.input['from'] == 'regularlist':
            pass
        return json.dumps(self.result)

    def deleteMonitor(self):
        monitorId = self.input['id']
        sql = "select NAME,PRODUCT from monitor where MONITOR_ID = '%s'" % monitorId
        result = zmonlib.ExecSql(sql)
        try:
            self.monitorName = result[0][0]
            self.product = result[0][1]
        except:
            self.result = {'code':400,'txt':'get monitor faile'}
        cmd = ['ZMON_DELETE',str(self.monitorName),str(self.product)]
        #停掉采集进程
        zmonlib.controlBackend(monitorId,'ZMON_DELETE')
        #删除关联的正则
        regularIds = zmonlib.getRegularIds(monitorId)
        for regularId in regularIds:
            self.deleteRegular(regularId)
        #删除监控和机器名的关联
        result = self.deleteHostMonitor(monitorId)
        #删除监控项
        sql = "delete from monitor where MONITOR_ID = '%s'" % monitorId
        zmonlib.ExecSql(sql)
        #删除redis中的数据
        zmonlib.deleteRedis(str(self.product), str(self.monitorName))
        self.result = {'code':200,'txt':u'删除成功'}   
    
    #删除正则表达式
    def deleteRegular(self, regularId):
        sql = 'delete from regular where REGULAR_ID = "%s"' % regularId
        zmonlib.ExecSql(sql)

    #删除监控和机器名的关联
    def deleteHostMonitor(self, monitorId, hostId = None):
        if hostId == None:
            sql = 'delete from host_monitor where MONITOR_ID = "%s"' % monitorId
            zmonlib.ExecSql(sql)
        else:
            sql = 'delete from host_monitor where MONITOR_ID = "%s" and HOST_ID = "%s"' % (monitorId,hostId)
            zmonlib.ExecSql(sql)


if __name__ == '__main__':
   pass 
