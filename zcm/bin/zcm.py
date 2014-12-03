#!/usr/bin/env python
#-*- coding:UTF-8 -*-
import os, zmq, time
from zbase import ZBase

class Zcm(ZBase): 
    def __init__(self):
        ZBase.__init__(self, 'Zcm')
        self.pub = {}
        self.products = self.GetConf('products')

    def getZcmConf(self, name=None, product=None):
        results = []
        try:
            #如果未指明需要加载监控的名字，则遍历数据库，把本模块负责的产品线下全部监控都加载一次
            if name == None or product == None:
                for product in self.products:
                    result = self.ExecSql('select NAME,PRODUCT from monitor where PRODUCT = "%s"' % product)
                    if result:
                        results.extend(result)
            #如果指明的产品线归本模块处理，才处理该次请求
            elif product in self.products:
                #之所以还要查一次数据库是为了防止提交的数据有误
                results = self.ExecSql("select NAME,PRODUCT from monitor where NAME = '%s' and PRODUCT = '%s'" % (name,product))
            else:
                results = None
            self.logger.debug('get zcm conf by name: %s, product: %s return : %s' % (name, product, results))
            return results 
        except:
            self.logger.exception('get zcm conf from mysql faile!')
            return None
    
    def addPub(self, name, product):
        zcmkey = self.GetZcmKey(product, name)
        #如果已经加载了zcmkey，直接退出，防止重复添加
        print zcmkey,self.pub.keys()
        if zcmkey in self.pub:
            self.logger.warning('Add zcm key %s to the pub dict faile!,the socket has exist: %s' % (zcmkey, str(self.pub)))
            return
        #检查存放socket的文件夹是否存在，不存在创建之
        if not os.path.exists('socket/monflow/%s' % product):
            os.makedirs('socket/monflow/%s' % product)
        #创建socket，监听zcmkey
        bind = zcmkey.replace('/zmon','ipc://socket') + '.sock'
        ctx = zmq.Context()
        s = ctx.socket(zmq.PUB)
        s.bind(bind)
        s.setsockopt(zmq.HWM, 1024)
        self.pub[zcmkey] = s
        self.logger.info('Add zcm key %s to the pub dict success!,bind socket: %s' % (zcmkey, bind))
    
    def delPub(self, name, product):
        zcmkey = self.GetZcmKey(product, name)
        if not zcmkey in self.pub:
            self.logger.warning('delete Pub faile, zcm key : %s did not exsit in PubDict: %s' % (zcmkey,self.pub))
            return
        self.pub[zcmkey].close()
        self.pub.pop(zcmkey)
        self.logger.info('delete zcm key: %s from the pub dict success!' % zcmkey)

    def loadModules(self):
        zcmkeydict = self.getZcmConf()
        for zcmkey in zcmkeydict:
            self.addPub(zcmkey[0], zcmkey[1])

    def addModule(self, name, product):
        if not product in self.products:
            self.logger.error('this zcm do not control product line : %s ' % product)
            return
        zcmkeydict = self.getZcmConf(name, product)
        if zcmkeydict != None and len(zcmkeydict) > 0:
            self.addPub(zcmkeydict[0][0], zcmkeydict[0][1])
        else:
           self.logger.error('add Pub faile, monitor : %s did not exsit in Mysql' % name)
    
    def deleteModule(self, name, product):
        zcmkeydict = self.getZcmConf(name, product)
        if zcmkeydict != None:
            self.delPub(zcmkeydict[0][0], zcmkeydict[0][1])
   
    def reloadModule(self, name, product):
        self.deleteModule(name, product)
        self.addModule(name, product)

    def listen(self): 
        time.sleep(1)
        while True:
            data = self.sub.recv_multipart()
            key = data[0]
            #监控项传过来的key不可能是ZMON_ADD或ZMON_DELETE或ZMON_RELOAD
            if key in self.pub:
                self.pub[key].send_multipart(data[1:])
                self.logger.info('%s send multipart' % key)
                #self.logger.debug('send data: %s' % data)
            elif key == 'ZMON_ADD':
                monitors = self.strToList(data[1],',')
                product = data[2]
                for name in monitors:
                    self.addModule(name, product)
            elif key == 'ZMON_DELETE':
                monitors = self.strToList(data[1],',')
                product = data[2]
                for name in monitors:
                    self.deleteModule(name, product)
            elif key == 'ZMON_RELOAD':
                monitors = self.strToList(data[1],',')
                product = data[2]
                for name in monitors:
                    self.reloadModule(name, product)
#            elif len(data) > 1 and key in self.pub:
#                self.pub[key].send_multipart(data[1:])
#                self.logger.info('%s send multipart' % key)
#                #self.logger.debug('send data: %s' % data)


if __name__ == '__main__':
    zcm = Zcm() 
    zcm.initSub()
    zcm.loadModules()
    zcm.listen()
   
