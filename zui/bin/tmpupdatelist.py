#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import os
import json
from zlist import ZList
from jsgenerate import JsGenerate
import logging
import zmonlib
import sys
sys.path.insert(0, '/home/space/zmon/python/lib/redis')

class UpdateList(object):
    def __init__(self, product):
        self.result = {'code':400,'txt':u'未知错误'}
        self.product = product

    #处理用户请求
    def updateList(self):
        self.updateProduct(self.product)
        self.result = {'code':200,'txt':u'更新成功'}
        return json.dumps(self.result)

    #根据产品线名进行数据的更新
    def updateProduct(self,product):
        logging.debug('begin to update product: %s' % product)
        self.updatePickle(product)
        #self.updateJs(product)

    #更新JS文件
    def updatePickle(self,product):
        l = ZList(product)
        l.zlist()

#    #更新JS文件要加载的树形结构
#    def updateJs(self,product):
#        jg = JsGenerate(product)  
#        jg.jsGenerate()              
                           

if __name__ == '__main__':
    try:
        product = sys.argv[1]
    except:
        print 'please input product!'
        sys.exit(1)
    u = UpdateList(product)
    u.updateList()
