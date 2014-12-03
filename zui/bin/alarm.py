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

class alarm(object):
    def __init__(self):
        self.input = web.input()

    def POST(self):
        if self.input['oper'] == 'del':
            return self.delete()
        elif self.input['oper'] == 'edit':
            return self.edit()
        elif self.input['oper'] == 'add':
            return self.add()
       
    def GET(self):
        logging.debug(self.input)
        userName = auth.uuap_sso()
        products = auth.getProcByName(userName)
        if products==None or len(products)==0:
            web.config.session.kill()
            return render.forbidden(userName)
        if self.input == None or self.input.get('oper') == None:
            return render.alarm(userName, products, web.ctx.homedomain)
        elif self.input['oper'] == 'search':
            return self.search()
            
    def delete(self):
        id = int(self.input.get('id'))
        sql = ''
        if self.input['from'] == 'threshold_list':
            sql = 'delete from threshold where THRESHOLD_ID=%d' % id
        elif self.input['from'] == 'whitelist_list':
            sql = 'delete from whitelist where WHITELIST_ID=%d' % id
        elif self.input['from'] == 'receiver_list':
            sql = 'delete from receiver where RECEIVER_ID=%d' % id
        record = zmonlib.ExecSql(sql)
        self.reloadMonflow()
        return record
        
    def edit(self):
        id = int(self.input.get('id'))
        if self.input['from'] == 'threshold_list':
            self.editThreshold(id)
        elif self.input['from'] == 'whitelist_list':
            self.editWhitelist(id)
        elif self.input['from'] == 'receiver_list':
            self.editReceiver(id)
        self.reloadMonflow()
        return True

    def add(self):
        pId = self.getProductId(self.input.get('product'))
        if self.input['from'] == 'threshold_list':
            self.addThreshold(pId)
        elif self.input['from'] == 'whitelist_list':
            self.addWhitelist(pId)
        elif self.input['from'] == 'receiver_list':
            self.addReceiver(pId)
        self.reloadMonflow()
        return True

        
    def search(self):
        pId = self.getProductId(self.input.get('product'))
        if self.input['from'] == 'threshold_list':
            return self.searchThreshold(pId)
        elif self.input['from'] == 'whitelist_list':
            return self.searchWhitelist(pId)
        elif self.input['from'] == 'receiver_list':
            return self.searchReceiver(pId)

    #----------添加接口--------
    def addReceiver(self,pId):
        key = self.input['key']
        mobile = self.input['mobile']
        mail = self.input['mail']
        sql = 'INSERT INTO receiver(PRODUCT_ID,ZCMKEY,MOBILE,MAIL) values(%d,"%s","%s","%s")' % (pId,key,mobile,mail)
        ret = zmonlib.ExecSql(sql)
        return ret
		
    def addThreshold(self,pId):
        change_rate_down = self.input.get('change_rate_down',0)
        change_rate_up = self.input.get('change_rate_up',0)
        key = self.input['key']
        qps_floor = self.input.get('qps_floor',0)
        qps_upper = self.input.get('qps_upper',0)
        shield_time = self.input.get('shield_time')
        sql = 'INSERT INTO threshold(PRODUCT_ID,ZCMKEY,QPS_UPPER,QPS_FLOOR,CHANGE_RATE_UP,CHANGE_RATE_DOWN,SHIELD_TIME) values(%d,"%s","%s","%s","%s","%s","%s")' % (pId,key,qps_upper,qps_floor,change_rate_up,change_rate_down,shield_time)
        ret = zmonlib.ExecSql(sql)
        logging.debug("%s,%s" % (sql,ret))
        return ret

    def addWhitelist(self,pId):
        key = self.input['key']
        sql = 'INSERT INTO whitelist(PRODUCT_ID,ZCMKEY) values(%d,"%s")' % (pId, key)
        ret = zmonlib.ExecSql(sql)
        return ret

    #----------更新接口--------
    def editReceiver(self,id):
        key = self.input['key']
        mobile = self.input.get('mobile')
        mail = self.input.get('mail')
        sql = 'update receiver set ZCMKEY="%s",MOBILE="%s",MAIL="%s" where RECEIVER_ID=%d' % (key,mobile,mail,id)
        ret = zmonlib.ExecSql(sql)
        return ret
        
    def editThreshold(self,id):
        change_rate_down = self.input.get('change_rate_down',0)
        change_rate_up = self.input.get('change_rate_up',0)
        key = self.input['key']
        qps_floor = self.input.get('qps_floor',0)
        qps_upper = self.input.get('qps_upper',0)
        shield_time = self.input.get('shield_time')
        if int(change_rate_down) > 100:
            raise web.internalerror('"下降变化率阈值"不能超过100')
            return
        sql = 'update threshold set ZCMKEY="%s",QPS_UPPER="%s",QPS_FLOOR="%s",CHANGE_RATE_UP="%s",CHANGE_RATE_DOWN="%s",SHIELD_TIME="%s" where THRESHOLD_ID=%d' % (key,qps_upper,qps_floor,change_rate_up,change_rate_down,shield_time,id)
        ret = zmonlib.ExecSql(sql)
        return ret

    def editWhitelist(self,id):
        key = self.input['key']
        sql = 'update whitelist set ZCMKEY="%s" where WHITELIST_ID=%d' % (key,id)
        ret = zmonlib.ExecSql(sql)
        return ret

    #---------查询接口----------        
    def searchReceiver(self, pId):
        sql = 'select RECEIVER_ID,ZCMKEY,MOBILE,MAIL from receiver where PRODUCT_ID=%d' % pId
        record = zmonlib.ExecSql(sql)
        return self.change2json(record)

    def searchThreshold(self, pId):
        sql = 'select THRESHOLD_ID,ZCMKEY,QPS_UPPER,QPS_FLOOR,CHANGE_RATE_UP,CHANGE_RATE_DOWN,SHIELD_TIME from threshold where PRODUCT_ID=%d' % pId
        record = zmonlib.ExecSql(sql)
        return self.change2json(record)

    def searchWhitelist(self, pId):
        sql = 'select WHITELIST_ID,ZCMKEY from whitelist where PRODUCT_ID=%d' % pId
        record = zmonlib.ExecSql(sql)
        return self.change2json(record)

    def getProductId(self, productName):
        sql = 'select REDIS_ID from redis where TYPE="%s"' % productName
        pId = zmonlib.ExecSql(sql)
        try:
            return int(pId[0][0])
        except:
            return None

    def change2json(self,record):
        responce = {}
        responce['page'] = 1
        responce['total'] = 1
        responce['records'] = len(record)
        responce['rows'] = []
        for rec in record: 
            row = {'id':rec[0],'cell':rec}
            responce['rows'].append(row)
        logging.debug(responce)
        return json.dumps(responce)

    def reloadMonflow(self):
        product = self.input.get('product')
        ip = zmonlib.getZcmIp(product, '')
        if ip == None:
            return
        port = 7333
        cmd = ['ZMON_RELOAD', '', str(product)]
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                s.connect((ip,port))  #'*.*.*.*'写上你要接入的IP地址
                s.close()
            except Exception, e:
                logging.exception('send cmd %s to ip: %s, port: %s error: %s' % (cmd, ip, port, e))
                s.close()
                return
            ctx = zmq.Context()
            pub = ctx.socket(zmq.PUB) 
            pub.connect('tcp://%s:%s' % (ip, port))
            pub.setsockopt(zmq.HWM, 1024)
            pub.send_multipart(cmd)
            logging.debug('send reload Monflow')
        except Exception,e:
            logging.exception(e)

if __name__ == '__main__':
    pass
