#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import os
import json
from zlist import ZList
from jsgenerate import JsGenerate
import web
import logging
import zmonlib

class UpdateList(object):
    def __init__(self):
        self.input = web.input()
        self.result = {'code':400,'txt':u'未知错误'}
        self.product = self.input['product']

    #处理用户请求
    def updateList(self):
        if self.product == 'ALL_PRODUCT':
            #更新所有产品线的数据
            products = zmonlib.getProducts()
            for product in products:
                self.updateProduct(product)
        else:
            #只更新用户指定的产品线的数据
            self.updateProduct(self.product)
        self.result = {'code':200,'txt':u'更新成功'}
        return json.dumps(self.result)

    #根据产品线名进行数据的更新
    def updateProduct(self,product):
        logging.debug('begin to update product: %s' % product)
        self.updatePickle(product)
        self.updateJs(product)

    #更新JS文件
    def updatePickle(self,product):
        l = ZList(product)
        l.zlist()

    #更新JS文件要加载的树形结构
    def updateJs(self,product):
        jg = JsGenerate(product)  
        jg.jsGenerate()              
                           

if __name__ == '__main__':
    u = UpdateList()
    u.updateList()
