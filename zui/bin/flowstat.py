#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import redis
import json
import web
import time
import cPickle
import yaml
import os,sys
import logging
import imp
import zmonlib
import auth
from zmonjs_flowstat import JsGenerate
        
conf = yaml.load(open('conf/zui.yaml'))
default_push_time = conf['default_push_time']
push_time_dict = conf['push_time']
render = web.template.render('templates')
class flowstat:
    def GET(self):
        userName = auth.uuap_sso()
        products = auth.getProcByName(userName)
        if products==None or len(products)==0:
            web.config.session.kill()
            return render.forbidden(userName)
        logging.debug('render flowstat.html for %s,products: %s' % (userName,products))
        jg = JsGenerate(userName, products)
        jg.jsGenerate()
        return render.flowstat(userName, products, web.ctx.homedomain)

    def POST1(self):
        input = web.input('key', 'where', 'value_names', 'time_begin', 'time_end', 'sum_interval', _unicode=False)
        logging.info('flowstat: input=%s', input)
        key = input['key']
        wheres = input['where'].split('\x00')
        push_time = push_time_dict.get(key, default_push_time)
        value_names = input['value_names'].split(',')
        time_begin = int(input['time_begin']) + 8 * 3600
        time_end = int(input['time_end']) + 8 * 3600
        sum_interval = int(input['sum_interval'])
        now = int(time.time()) + 8 * 3600

        for i, j in push_time:
            if sum_interval == i:
                interval, ca_size = i, j
                break
            if sum_interval == 0 and time_begin > now - i * j:
                #interval, ca_size = i, j
                interval, ca_size = i, j
                break
        time_begin //= interval
        time_end //= interval
        if time_begin > time_end:
            raise web.internalerror('time_begin > time_end')
        ret = {'time_begin': time_begin * interval - 8 * 3600, 'interval': interval, 'data': []}
        logging.debug('ret: %s' ,ret)
        for i, value_name in enumerate(value_names):
            logging.debug('value_name: %s' ,value_name)
            ret['data'].append([])
            for where in wheres:
                try:
                    db_key = '%s\x01%s\x01%s\x01%d\x02%d' % (key, where, value_name, interval, ca_size)
                    logging.debug('db_key: %s' % repr(db_key))
                    #取redis的地址和端口
                    redisip,redisport = self.getRedis(key)
                    db = redis.Redis(redisip, int(redisport), socket_timeout=1)
                    length, next = db.cainfo(db_key)
                    #根据redis中存储的时间段计算开始时间和结束时间
                    time_begin_cnt,time_end_cnt = self.caculateTime(length, next)
                    
                    if time_end_cnt > time_begin:
                        data = [0] * (time_begin_cnt - time_begin)
                        data_db = db.carange(db_key, time_begin_cnt, time_end_cnt - 1)
                        logging.debug('time_begin_cnt: %s,time_end_cnt :%s',time_begin_cnt,time_end_cnt)
                        if sum_interval == 0:
                            data_db = [x / interval for x in data_db]
                        logging.debug('data_db: %s',data_db)
                        data.extend(data_db)
                        data.append(data_db[-1])
                        data.extend([0] * (time_end - time_end_cnt))
                    else:
                        data = [0] * (time_end + 1 - time_begin)
                except :
                    logging.debug(str(sys.exc_info()))
                    data = [0] * (time_end + 1 - time_begin)
                try:
                    ret['data'][i].append(data)
        	    logging.info('flowstat: return=%s', json.dumps(ret))
                except:
                    logging.debug(str(sys.exc_info()))
        logging.info(str(json.dumps(ret)))
        return json.dumps(ret)
    

    def POST(self):
        self.getInput()
        self.setSumInterval()
        ret = {'time_begin': self.time_begin * self.interval - 8 * 3600, 'interval': self.interval, 'data': [], 'sum': []}
        logging.debug('ret: %s' ,ret)
        value_name = 'flow'
        ret['data'].append([])
        for where in self.wheres:
            data,s = self.getData(where, value_name, self.time_begin, self.time_end)
            try:
                ret['data'][0].append(data)
                ret['sum'].append(int(s))
                logging.info('flowstat: return=%s', json.dumps(ret))
            except:
                logging.debug(str(sys.exc_info()))
        logging.info(str(json.dumps(ret)))
        return json.dumps(ret)

#                try:
#                    db_key = '%s\x01%s\x01%s\x01%d\x02%d' % (self.key, where, value_name, self.interval, self.ca_size)
#                    logging.debug('db_key: %s' % repr(db_key))
#                    #取redis的地址和端口
#                    redisip,redisport = self.getRedis(self.key)
#                    db = redis.Redis(redisip, int(redisport), socket_timeout=1)
#                    length, next = db.cainfo(db_key)
#                    #根据redis中存储的时间段计算开始时间和结束时间
#                    time_begin_cnt,time_end_cnt = self.caculateTime(length, next)
#                    
#                    if time_end_cnt > self.time_begin:
#                        data = [0] * (time_begin_cnt - self.time_begin)
#                        data_db = db.carange(db_key, time_begin_cnt, time_end_cnt - 1)
#                        logging.debug('time_begin_cnt: %s,time_end_cnt :%s',time_begin_cnt,time_end_cnt)
#                        if self.sum_interval == 0:
#                            data_db = [x / self.interval for x in data_db]
#                        logging.debug('data_db: %s',data_db)
#                        data.extend(data_db)
#                        data.append(data_db[-1])
#                        data.extend([0] * (self.time_end - time_end_cnt))
#                    else:
#                        data = [0] * (self.time_end + 1 - self.time_begin)
#                except :
#                    logging.debug(str(sys.exc_info()))
#                    data = [0] * (self.time_end + 1 - self.time_begin)

    def getData(self, where, value_name, time_begin, time_end):
        try:
            db_key = '%s\x01%s\x01%s\x01%d\x02%d' % (self.key, where, value_name, self.interval, self.ca_size)
            logging.debug('db_key: %s' % repr(db_key))
            #取redis的地址和端口
            redisip,redisport = self.getRedis(self.key)
            db = redis.Redis(redisip, int(redisport), socket_timeout=1)
            length, next = db.cainfo(db_key)
            #根据redis中存储的时间段计算开始时间和结束时间
            time_begin_cnt,time_end_cnt = self.caculateTime(length, next, time_begin, time_end)
            
            if time_end_cnt > time_begin:
                data = [0] * (time_begin_cnt - time_begin)
                data_db = db.carange(db_key, time_begin_cnt, time_end_cnt - 1)
                logging.debug('time_begin_cnt: %s,time_end_cnt :%s',time_begin_cnt,time_end_cnt)
                if self.sum_interval == 0:
                    data_db = [x / self.interval for x in data_db]
                logging.debug('data_db: %s',data_db)
                data.extend(data_db)
                data.append(data_db[-1])
                data.extend([0] * (time_end - time_end_cnt))
            else:
                data = [0] * (time_end + 1 - time_begin)
        except :
            logging.debug(str(sys.exc_info()))
            data = [0] * (time_end + 1 - time_begin)
        s = sum(data)*self.interval
        if data[-1] == 0:
            data[-1] = data[-2]
        return data,s

    #取redis的地址和端口
    def getRedis(self, key):
        for j in xrange(1,5): 
            try:
                productname = key.split('/')[-2]
                monitor = key.split('/')[-1]
                logging.debug("productname: %s, monitor: %s" % (productname, monitor))
                redisip,redisport = zmonlib.GetRedis(productname, monitor)
                logging.debug('%s,%s' % (redisip,redisport))
                return redisip,redisport
                break
            except Exception,e:
                logging.debug("Get No redis ip,so i sleep 1, Exception: %s" % e)
                time.sleep(1)

    #根据redis中存储的时间段计算开始时间和结束时间
    def caculateTime(self, length, next, time_begin, time_end):
        time_begin_db = next - 1 - length
        time_end_db = next - 1
        #if interval != push_time[0][0]:
        #    time_end_db -= 1
        time_begin_cnt = max(time_begin, time_begin_db)
        time_end_cnt = min(time_end, time_end_db)
        return time_begin_cnt,time_end_cnt

    def getInput(self):
        input = web.input('key', 'where', 'value_names', 'time_begin', 'time_end', 'sum_interval', _unicode=False)
        logging.info('flowstat: input=%s', input)
        self.key = input['key']
        self.wheres = input['where'].split('\x00')
        self.push_time = [[10, 4000], [180, 4000], [3600, 4000], [86400, 4000]]
        self.value_names = input['value_names'].split(',')
        self.time_begin = int(input['time_begin']) + 8 * 3600
        self.time_end = int(input['time_end']) + 8 * 3600
        if self.time_begin > self.time_end:
            raise web.internalerror('time_begin > time_end')
        self.sum_interval = int(input['sum_interval'])

    def setSumInterval(self):
        now = int(time.time()) + 8 * 3600
        for i, j in self.push_time:
            if self.sum_interval == i:
                self.interval, self.ca_size = i, j
                break
            if self.sum_interval == 0 and self.time_begin > now - i * j:
                self.interval, self.ca_size = i, j
                break
        self.time_begin //= self.interval
        self.time_end //= self.interval
        
