#!/usr/bin/env python2.7
import os, sys, socket, time, yaml, cPickle, re, string,logging
from collections import defaultdict
import redis
import MySQLdb
import zmonlib

def filter_value(name):
    host_cache = {}
    ip_regex = re.compile(r'^10\.(\d+\.){2}\d+$')
    if name.isdigit():
        return int(name)
    if ip_regex.match(name):
        if name in host_cache:
            return host_cache[name]
        try:
            host = socket.gethostbyaddr(name)[0]
            if host.endswith('.baidu.com'):
                host = host[:-10]
            host_cache[name] = host
            return host
        except socket.herror:
            pass
    return filter(lambda x: x in string.printable, name)

class ZList(object):
    def __init__(self, product):
        self.product = product
        zmonlib.Init()
        self.initConf()
        self.pickleName = 'data/zlist.%s.pickle' % product

    def initConf(self):    
        conf = {}
        sql = "SELECT IP,PORT FROM redis where TYPE = '%s'" % self.product
        result = zmonlib.ExecSql(sql)
        try:
            conf['redis'] = [result[0][0], result[0][1]]
        except:
            logging.error('get ip,port from redis by product: %s faile,result: %s' % (self.product, str(result)))
            sys.exit()
        
        sql = "SELECT PRODUCT,NAME,UITREE FROM monitor where PRODUCT = '%s'" % self.product
        result = zmonlib.ExecSql(sql)
        conf['push_list'] = {}
        for rec in result:
            zcm_key = '/zmon/monflow/%s/%s' % (rec[0], rec[1])
            tmpdict = eval(rec[2])
            nodedict = {}
            for key in tmpdict:
                nodename = '%s/%s' % (zcm_key, key)
                nodedict[nodename] = tmpdict[key].replace(' ','').split(',')
            conf['push_list'][zcm_key] = nodedict
        self.conf = conf
        logging.debug(self.conf)
        self.push_list = conf['push_list']
        logging.info('load conf of product: %s success,result: %s' % (self.product, str(self.conf)))

    def zlist(self):
        self.generatePickle()
        self.writePickle()

    def generatePickle(self):
        data = {}
        keys_uniq = defaultdict(set)
        for zcm_key in self.push_list:
            for list_key in self.push_list[zcm_key]:
                data[list_key] = defaultdict(list)
        
        db = redis.Redis(self.conf['redis'][0], int(self.conf['redis'][1]), socket_timeout=1)
        db_keys = db.keys()
        
        for db_key in db_keys:
            zcm_key, where = db_key.split('\x01')[:2]
            keys_uniq[zcm_key].add(filter(lambda x: ord(x) < 128, where))
        logging.debug('get keys_uniq: %s' % str(keys_uniq))
        for zcm_key in keys_uniq:
            for where in keys_uniq[zcm_key]:
                if zcm_key not in self.push_list:
                    continue
                if len(where) == 0:
                    continue
                wheres = [x.split('\x03', 1) for x in where.split('\x02')]
                wheres_name = [x[0] for x in wheres]
                for list_key, key_names in self.push_list[zcm_key].iteritems():
                    if wheres_name == key_names[:len(wheres)]:
                        logging.debug('====  wheres_name: %s, key_names[:len(wheres)]: %s' % (wheres_name, key_names[:len(wheres)]))
                        logging.debug('sorted, list_key: %s, key_names: %s' % (list_key, key_names))
                        post_name = key_names[len(wheres)-1]
                        where_pre, where_post = [], None
                        for k, v in wheres:
                            if k == post_name:
                                where_post = (k, v)
                            else:
                                where_pre.append('\x03'.join((k, v)))
                        where_pre = '\x02'.join(where_pre)
                        value_post = filter_value(where_post[1])
                        data[list_key][where_pre].append({'name': value_post, 'where': where_post, 'isParent': len(wheres) != len(key_names)})
                    else:
                        logging.debug('!!!!  wheres_name: %s, key_names[:len(wheres)]: %s' % (wheres_name, key_names[:len(wheres)]))

        
        logging.debug(data)
        for list_key in data:
            for where_pre in data[list_key]:
                data[list_key][where_pre] = data[list_key][where_pre]
                logging.debug('unsort : %s' % data[list_key][where_pre])
                data[list_key][where_pre] = sorted(data[list_key][where_pre], key=lambda x: x['name'])
        self.data = data

    def writePickle(self):
        #sys.stdout.write(cPickle.dumps(self.data, cPickle.HIGHEST_PROTOCOL))
        f = open(self.pickleName,'wb')
        cPickle.dump(self.data, f, cPickle.HIGHEST_PROTOCOL)
        f.close()


if __name__ == '__main__':
    try:
        product = sys.argv[1]
    except:
        print 'please input product!'
        sys.exit(1)
    logging.basicConfig(filename='log/updatelist.log', format='%(levelname)s %(asctime)s %(filename)s:%(lineno)d:%(funcName)s: %(message)s', level=logging.DEBUG)
    l = ZList(product)
    l.zlist()
