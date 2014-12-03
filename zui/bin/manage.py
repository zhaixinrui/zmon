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
from search import Search
from delete import Delete
from update import Update
import auth
render = web.template.render('templates')

class manage(object):
    def __init__(self):
        self.input = web.input()

    def POST(self):
        if self.input['oper'] == 'del':
            d = Delete(self.input)
            return d.delete()
        elif self.input['oper'] == 'edit':
            u = Update(self.input)
            return u.update()
       
    def GET(self):
        logging.debug(self.input)
        userName = auth.uuap_sso()
        products = auth.getProcByName(userName)
        if products==None or len(products)==0:
            web.config.session.kill()
            return render.forbidden(userName)
        if self.input == None or len(self.input) == 0:
            return render.manage(userName, products, web.ctx.homedomain)
        #更新树形菜单
        if self.input['oper'] == 'updatelist':
            #检查文件夹是否存在，不存在则创建
            dirPath = 'data/updateflag'
            product = self.input['product']
            updateflag = '%s/%s' % (dirPath,product)
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)
            #创建更新标志文件以触发updatelist.sh的更新任务
            f = open(updateflag, 'w')
            f.close()
            while os.path.exists(updateflag):
                time.sleep(0.1)
            return json.dumps({'code':200,'txt':u'更新成功'})
        elif self.input['oper'] == 'search':
            s = Search(self.input)
            return s.search()
            




if __name__ == '__main__':
    pass
