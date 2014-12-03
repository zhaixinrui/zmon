#!/usr/bin/env python #-*- coding: UTF-8 -*-
import redis
import time
import yaml
import zmonlib
import logging
import web
from collections import defaultdict

#根据key从数据库中查到对应redis的ip和port，建立redis连接并返回一个redis连接对象
def getRedisDb(key):
    db = None
    for j in xrange(1,5): 
        try:
            productname = key.split('/')[-2]
            monitor = key.split('/')[-1]
            logging.debug("productname: %s, monitor: %s" % (productname, monitor))
            redisip,redisport = zmonlib.GetRedis(productname, monitor)
            logging.debug('%s,%s' % (redisip,redisport))
            db = redis.Redis(redisip, int(redisport), socket_timeout=1)
            break
        except Exception,e:
            logging.debug("Get No redis ip,so i sleep 1, Exception: %s" % e)
            time.sleep(1)
    return db

#从redis中取到所有的key，包含zcmkey+where
def getKeys(redisDb):
    keys = defaultdict(set)
    for db_key in redisDb.keys():
        zcmkey, where = db_key.split('\x01')[:2]
        keys[zcmkey].add(filter(lambda x: ord(x) < 128, where))
    #logging.debug('get %s keys from redis' % len(keys))
#    return keys
#    pprint.pprint( redisDb.keys())

#根据查询的开始和结束时间返回对应的interval和ca_size
def getInterval(time_begin, time_end):
    time_begin = int(time_begin) + 8 * 3600
    time_end = int(time_end) + 8 * 3600
    now = int(time.time()) + 8 * 3600
    conf = yaml.load(open('conf/zui.yaml'))
    push_time = conf['default_push_time']
    for i, j in push_time:
        if time_begin > now - i * j:
            interval, ca_size = i, j
            break
    return interval,ca_size

#根据指定参数查询redis，并返回数组形式的结果
def getData(redisDb, key, where, value_name, time_begin, time_end):
    interval,ca_size = getInterval(time_begin, time_end)
    time_begin = int(time_begin) + 8 * 3600
    time_end = int(time_end) + 8 * 3600
    now = int(time.time()) + 8 * 3600
    time_begin //= interval
    time_end //= interval
    if time_begin > time_end:
        return None
    try:
        db_key = '%s\x01%s\x01%s\x01%d\x02%d' % (key, where, value_name, interval, ca_size)
        logging.debug('[db_key:%s]' % repr(db_key))
        length, next = redisDb.cainfo(db_key)
        time_begin_db = next - 1 - length
        time_end_db = next - 1
        time_begin_cnt = max(time_begin, time_begin_db)
        time_end_cnt = min(time_end, time_end_db)
        
        if time_end_cnt > time_begin:
            data = [0] * (time_begin_cnt - time_begin)
            data_db = redisDb.carange(db_key, time_begin_cnt, time_end_cnt - 1)
            #logging.debug('time_begin_cnt: %s,time_end_cnt :%s',time_begin_cnt,time_end_cnt)
            data_db = [10*x / interval for x in data_db]
            #logging.debug('data_db: %s',data_db)
            data.extend(data_db)
            data.append(data_db[-1])
            data.extend([0] * (time_end - time_end_cnt))
        else:
            data = [0] * (time_end + 1 - time_begin)
    except :
        #print str(sys.exc_info())
        data = [0] * (time_end + 1 - time_begin)
    #如果最后时刻的值是0，则替换成前一个时刻的值，防止展示的曲线有陡降
    if data[-1] == 0:
        try:
            data[-1] = data[-2]
        except:
            pass
    return interval,data

class query:
    def GET(self):
        self.input = web.input()
        logging.debug(self.input)
        product = self.input.get('product')
        monitor = self.input.get('monitor')
        key = self.input.get('where','')
        value = self.input.get('value')
        time_begin = self.input.get('time_begin')
        time_end = self.input.get('time_end')
        zcmkey = '/zmon/monflow/%s/%s' % (product, monitor)
        db = getRedisDb(zcmkey)
        logging.debug(repr(key))
        interval,data = getData(db, zcmkey, key, value, time_begin, time_end)
        logging.debug('[product:%s] [monitor:%s] [key:%s] [value:%s] [time_begin:%s] [time_end:%s] [interval:%s] [data:%s]'\
                     % (product, monitor, repr(key), value, time_begin, time_end, interval, data))
        return {'interval':interval, 'data':data}
    

if __name__ == "__main__":
    db = getRedisDb('/zmon/monflow/ors/ResourceStat')
    print db
    print getData(db, '/zmon/monflow/ors/ResourceStat', 'App\x03frsui', 'CpuUsed', 1365746997, 1365750597)
    print getData(db, '/zmon/monflow/ors/ResourceStat', 'App\x03frsui', 'CpuQuota', 1365744810, 1365748410)
    print getData(db, '/zmon/monflow/ors/ResourceStat', '', 'CpuUsed', 1365742217, 1365745817)
    print getKeys(db)
