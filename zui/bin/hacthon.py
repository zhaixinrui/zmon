#!/home/zxr/zmon/python/bin/python
import json
import web
import time
import os,sys
import logging
import imp
import sso

class hacthon(object):
    def GET(self):
        web.config.debug = False
        logging.debug(str(web.config.session))
        return sso.auth()


if __name__ == '__main__':
    test = {'receive': u'13521641899', 'code': u'1'}
    h = hacthon(test)
    h.POST()
