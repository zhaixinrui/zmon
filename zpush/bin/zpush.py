#!/usr/bin/env python2.7
#-*- coding:UTF-8 -*-
import threading,time,zmq,signal,sys
from collections import defaultdict

import redis

from zbase import ZBase
from zredis import push,merge
from rms import rms_extra_keys

db_retry_time = 0.1
EXIT_TAG = {}
#主进程被终止时的处理方法，保证主进程退出后子线程能够正常退出
def SignalHandler(sig,id):
    for key in EXIT_TAG:
        EXIT_TAG[key] = True
signal.signal(signal.SIGINT,SignalHandler)
signal.signal(signal.SIGTERM,SignalHandler)


class ZPushMain(ZBase):
    def __init__(self):
        ZBase.__init__(self, 'ZPush')
        self.products = self.GetConf('products')

    def getZpushConf(self, name=None, product=None):
        results = []
        try:
            #如果未指明需要加载监控的名字或者产品线，则遍历数据库，把本模块负责的产品线下全部监控都加载一次
            if name == None or product == None:
                for product in self.products:
                    result = self.ExecSql('select PRODUCT,UITREE,NAME from monitor where PRODUCT = "%s"' % product)
                    if result:
                        results.extend(result)
            #如果指明的产品线归本模块处理，才处理该次请求
            elif product in self.products:
                results = self.ExecSql("select PRODUCT,UITREE,NAME from monitor where NAME = '%s' and PRODUCT = '%s'" % (name, product))
        except Exception,e:
            self.logger.exception('Get zpush conf Exception :%s' % e)
        finally:
            self.logger.info('get zpush conf by name %s, product %s return: %s' % (name, product, results))
            return results


    def loadModules(self):
        zpushConfList = self.getZpushConf()
        for zpushConf in zpushConfList:
            env = self.getEnvByConf(zpushConf)
            t = ZPushThread(env['zcm_key'])
            t.setEnv(env)
            EXIT_TAG[env['zcm_key']] = False
            t.start()

    def getEnvByConf(self,zpushConf):
        env = {}
        env['modname'] = zpushConf[2]
        env['zcm_key'] = self.GetZcmKey(zpushConf[0], zpushConf[2])
        env['zcm_addr'] = self.GetZcmSock(zpushConf[0], zpushConf[2])
        env['push_time'] = [[10, 4000], [180, 4000], [3600, 4000], [86400, 4000]]
        env['extra_key_names'] = ['rms_product']
        env['push_list'] = []
        uitree = eval(zpushConf[1])
        for node in uitree:
            push_list = self.strToList(uitree[node], ',')
            env['push_list'].append(push_list)
        #push_list.append('rms_product')
        self.logger.info(env)
        return env
    
    def reloadModule(self, modname, product):
        self.deleteModule(modname, product)
        self.addModule(modname, product)
    
    def addModule(self, modname, product):
        zcm_key = self.GetZcmKey(product, modname)
        if zcm_key in EXIT_TAG:
            self.logger.warning('add module faile! module : %s has already exsited!' % modname)
            return 
        try:
            zpushConfList = self.getZpushConf(modname, product)
            for zpushConf in zpushConfList:
                env = self.getEnvByConf(zpushConf)
                t = ZPushThread(env['zcm_key'])
                t.setEnv(env)
                EXIT_TAG[env['zcm_key']] = False
                t.start()
                self.logger.info('add module: %s success, the conf is: %s' % (modname, env))
        except Exception,e:
            self.logger.exception('add module: %s error : %s' % (modname, e))
    
    def deleteModule(self, modname, product):
        zcm_key = self.GetZcmKey(product, modname)
        if not zcm_key in EXIT_TAG:
            self.logger.warning('delete module faile! module : %s do not exsit!' % modname)
            return 
        try:
            EXIT_TAG[zcm_key] = True
            #wait TailThread exit
            while True:
                if EXIT_TAG[zcm_key] == False:
                   EXIT_TAG.pop(zcm_key)
                   self.logger.info('delete module %s success!' % modname)
                   break
                else:
                   self.logger.info('wait %s exit, sleep 0.1s!' % modname)
                   time.sleep(0.1)
        except Exception,e:
            self.logger.exception('delete module error : %s' % e)

    def listen(self):
        time.sleep(1)
        while True:
            data = self.sub.recv_multipart()
            action = data[0]
            if action == 'ZMON_ADD':
                monitors = self.strToList(data[1],',')
                product = data[2]
                for name in monitors:
                    self.addModule(name, product)
            elif action == 'ZMON_DELETE':
                monitors = self.strToList(data[1],',') 
                product = data[2]              
                for name in monitors: 
                    self.deleteModule(name, product)
            elif action == 'ZMON_RELOAD':
                monitors = self.strToList(data[1],',')
                product = data[2]
                for name in monitors:
                    self.reloadModule(name, product)

class ZPushThread(threading.Thread, ZBase):
    def __init__(self, threadname):
        threading.Thread.__init__(self, name=threadname)
        ZBase.__init__(self,'PushThread_%s' % threadname)

    def setEnv(self,env):
        self.zcm_addr = env['zcm_addr']
        self.zcm_key  = env['zcm_key']
        self.push_time = env['push_time']
        #self.extra_key_names =env['extra_key_names']
        self.extra_key_names = None
        self.push_list = env['push_list']
        name = self.zcm_key.split('/')[4]
        product = self.zcm_key.split('/')[3]
        self.redisip,self.redisport = self.GetRedis(product, name)

    def run(self):
        ctx = zmq.Context()
        self.sub = ctx.socket(zmq.SUB)
        self.sub.setsockopt(zmq.IDENTITY, 'ZPUSH %s' % self.zcm_key)
        self.sub.setsockopt(zmq.SUBSCRIBE, '')
        self.sub.connect(self.zcm_addr)

        if self.extra_key_names:
            extra_keys = rms_extra_keys 
        else:
            extra_keys = None
        while 1:
            if EXIT_TAG[self.getName()] == True:
                EXIT_TAG[self.getName()] = False
                self.logger.info('module : %s exit success!' % self.getName())
                sys.exit() 
            try:
                self.all_data_dicts = defaultdict(lambda: defaultdict(float))
                for i in xrange(128):
                    if zmq.select([self.sub], [], [], 1)[0]:
                        msg = self.sub.recv_pyobj()
                        self.logger.info('module: %s receive msg' % self.zcm_key)
                        key_names_index = {}
                        for index, key_name in enumerate(msg['key_names']):
                            key_names_index[key_name] = index
                        if self.extra_key_names:
                            msg['key_names'].extend(self.extra_key_names)
                        for value_name, data_dict in msg['data'].iteritems():
                            add_data_dict = self.all_data_dicts[tuple(msg['key_names']), value_name, msg['time']]
                            #self.logger.debug('key_names: %s' % msg['key_names'])
                            for k, v in data_dict.iteritems():
                                #if extra_keys:
                                    #self.logger.debug('k: %s,key_names_index: %s' % (k,key_names_index))
                                    #k = k + extra_keys(key_names_index, k)
                                add_data_dict[k] += v
                    else:
                        break
                #db = redis.Redis(self.redisip, int(self.redisport)).pipeline(False)
                db = redis.Redis(self.redisip, int(self.redisport))
                push_count = 0
                for (data_key_names, value_name, data_time), data_dict in self.all_data_dicts.iteritems():
                    merge_dict = {}
                    for push_key_names in self.push_list:
                        sorted_key_names = merge(merge_dict, push_key_names, data_key_names, data_dict)
                        for i in xrange(len(push_key_names) - 1, -1, -1):
                            sorted_key_names = merge(merge_dict, push_key_names[:i], sorted_key_names, merge_dict[sorted_key_names])
                    for key_names, merge_data in merge_dict.iteritems():
                         #self.logger.debug(key_names)
                         for keys, value in merge_data.iteritems():
                             #self.logger.debug('key: %s,value: %s' % (keys, key_names))
                             push(db, db_retry_time, self.zcm_key, key_names, keys, value_name, value, data_time, self.push_time)
                             push_count += 1
                #while 1:
                #    try:
                #        db.execute()
                #        break
                #    except Exception,e:
                #        self.logger.exception('db.execute() faile!')
                #        time.sleep(db_retry_time)
                self.logger.info('zcm_key:%s,push_count:%d' % (self.zcm_key, push_count))
            except Exception,e:
                self.logger.exception('Exception: %s', e)

if __name__ == '__main__':
    iZPushMain = ZPushMain()
    iZPushMain.loadModules()
    iZPushMain.initSub()
    iZPushMain.listen()

