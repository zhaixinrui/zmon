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
from create import create
from manage import manage
from modify import modify
from alarm import alarm
import auth
from zmonjs import JsGenerate
from flowstat import flowstat
import testre
import queryRedis
from monitorid import MonitorId

zmonlib.Init()

conf = yaml.load(open('conf/zui.yaml'))
default_push_time = conf['default_push_time']
push_time_dict = conf['push_time']

urls = (
    '/zmon/', 'index',
    '/zmon/zlist', 'zlist',
    '/zmon/ztable', 'ztable',
    '/zmon/zrange', 'zrange',
    '/zmon/create', 'create',
    '/zmon/modify', 'modify',
    '/zmon/manage', 'manage',
    '/zmon/alarm', 'alarm',
    '/zmon/testre', 'testre.TestRegular',
    '/zmon/flowstat', 'flowstat',
    '/zmon/auth', 'auth.auth',
    '/zmon/logout', 'auth.logout',
    '/zmon/query', 'queryRedis.query',
    '/zmon/monitorid', 'MonitorId',
)

app = web.application(urls, globals())
web.config.session = web.session.Session(app, web.session.DiskStore('data/sessions'))
render = web.template.render('templates')

pickle_cache = {}
def load_pickle_with_cache(pickle_file):
    try:
        stat_result = os.stat(pickle_file)
    except:
        logging.exception('stat error: %s', pickle_file)
        pickle_cache.pop(pickle_file, None)
        return None
    some_stat_result = (stat_result.st_dev, stat_result.st_ino, stat_result.st_size, stat_result.st_mtime)
    if pickle_file in pickle_cache and pickle_cache[pickle_file]['stat'] == some_stat_result:
        logging.debug('hit cache: %s', pickle_file)
        return pickle_cache[pickle_file]['pickle']
    logging.debug('miss cache and try to reload: %s', pickle_file)
    try:
        pickle_loaded = cPickle.load(open(pickle_file))
    except:
        logging.exception('pickle load error: %s', pickle_file)
        pickle_cache.pop(pickle_file, None)
        return None
    pickle_cache[pickle_file] = {}
    pickle_cache[pickle_file]['stat'] = some_stat_result
    pickle_cache[pickle_file]['pickle'] = pickle_loaded
    return pickle_loaded


class index:
    def GET(self):
        userName = auth.uuap_sso()
        products = auth.getProcByName(userName)
        if products==None or len(products)==0:
            web.config.session.kill()
            return render.forbidden(userName)
            #raise web.forbidden()
        logging.debug('render index.html for %s,products: %s' % (userName,products))
        logging.info("req_header:%s:%s" % (web.ctx.env.get('REMOTE_ADDR'), web.ctx.env.get('REMOTE_PORT')))
        jg = JsGenerate(userName, products)
        jg.jsGenerate()
        return render.index(userName, products, web.ctx.homedomain)
        
        
def getProdutByKey(key):
    try:
        return key.split('/')[3]
    except:
        return None

class zlist:
    def POST(self):
        return self.handle_request()

    def GET(self):
        return self.handle_request()

    def handle_request(self):
        input = web.input('list_key', 'where', _unicode=False)
        logging.info('zlist: input=%s', input)
        product = getProdutByKey(input['list_key'])
        logging.info('product = %s', product)
        data = load_pickle_with_cache('data/zlist.%s.pickle' % product)
        try:
            return json.dumps(data[input['list_key']][input['where']])
        except:
            return None

class ztable:
    def GET(self):
        input = web.input('product', 'monitor', _unicode=False)
        product = input['product']
        monitor = input['monitor']
        sql = 'select UICHART from monitor where product="%s" and name="%s"' % (product, monitor)
        ret = zmonlib.ExecSql(sql)
        #try:
        return ret[0][0]
        #except:
        #    return None

class zrange:
    def POST(self):
        return self.handle_request()

    def GET(self):
        return self.handle_request()

    def handle_request(self):
        input = web.input('key', 'where', 'value_names', 'time_begin', 'time_end', 'sum_interval', _unicode=False)
        logging.info('zrange: input=%s', input)
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
                    for j in xrange(1,5): 
                        try:
                            productname = key.split('/')[-2]
                            monitor = key.split('/')[-1]
                            logging.debug("productname: %s, monitor: %s" % (productname, monitor))
                            redisip,redisport = zmonlib.GetRedis(productname, monitor)
                            logging.debug('%s,%s' % (redisip,redisport))
                            break
                        except Exception,e:
                            logging.debug("Get No redis ip,so i sleep 1, Exception: %s" % e)
                            time.sleep(1)
                    db = redis.Redis(redisip, int(redisport), socket_timeout=1)
                    length, next = db.cainfo(db_key)
                    time_begin_db = next - 1 - length
                    time_end_db = next - 1
                    #if interval != push_time[0][0]:
                    #    time_end_db -= 1
                    time_begin_cnt = max(time_begin, time_begin_db)
                    time_end_cnt = min(time_end, time_end_db)
                    
                    if time_end_cnt > time_begin:
                        data = [0] * (time_begin_cnt - time_begin)
                        data_db = db.carange(db_key, time_begin_cnt, time_end_cnt - 1)
                        logging.debug('time_begin_cnt: %s,time_end_cnt :%s',time_begin_cnt,time_end_cnt)
                        if sum_interval == 0:
                            data_db = [x / interval for x in data_db]
                        logging.debug('data_db: %s',data_db)
                        data.extend(data_db)
                        data.append(data_db[-1])
                        data.extend([None] * (time_end - time_end_cnt))
                    else:
                        data = [None] * (time_end + 1 - time_begin)
#                except redis.RedisError:
                except :
                    logging.debug(str(sys.exc_info()))
                    data = [None] * (time_end + 1 - time_begin)
                try:
                    ret['data'][i].append(data)
#        	    logging.info('zrange: return=%s', json.dumps(ret))
                except:
                    logging.debug(str(sys.exc_info()))
#        logging.info(str(json.dumps(ret)))
        return json.dumps(ret)

application = app.wsgifunc()

#if __name__ == "__main__":
#    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
#    app.run()
