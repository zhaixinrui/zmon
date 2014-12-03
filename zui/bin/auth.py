#!/usr/bin/env python
#-*- coding:UTF-8 -*-

import json
import web
import time
import os,sys
import logging
import urllib
import zmonlib

#SSO_URL = 'http://uuap.baidu.com'
SSO_URL = 'http://itebeta.baidu.com:8100'

render = web.template.render('templates')
class auth(object):
    #登陆后的回调函数
    def GET(self):
        user_data = web.input(u=None, ticket=None)
        if not user_data.u or not user_data.ticket:
            return render.forbidden('')
        service_url = '%s/zmon/auth?u=%s' % (web.ctx.homedomain, web.urlquote(user_data.u))
        validate_url = '%s/validate?service=%s&ticket=%s' % (SSO_URL, web.urlquote(service_url), web.urlquote(user_data.ticket))
        r = urllib.urlopen(validate_url).readlines()
        if len(r) == 2 and r[0].strip() == 'yes':
            web.config.session.sso_username = r[1].strip()
            raise web.seeother(user_data.u)
        else:
            return render.forbidden('')

class logout(object):
    def GET(self):
        web.config.session.kill()
        raise web.seeother('%s/logout' % SSO_URL)

#访问用户统一认证平台的单点登录系统
def uuap_sso():
    sso_username = web.config.session.get('sso_username')
    #如果有已经登陆则返回用户名，否则跳转到uuap登录页
    if sso_username:
        logging.debug('sso_username: %s' % sso_username)
        return sso_username
    service_url = '%s/zmon/auth?u=%s' % (web.ctx.homedomain, web.urlquote(web.ctx.homepath + web.ctx.fullpath))
    raise web.seeother('%s/login?service=%s' % (SSO_URL, web.urlquote(service_url)))

#跟进用户名取到有权限的产品线
def getProcByName(userName):
    ret = set()
    ret.add('zTest')
    sql = "select PRODUCT from user where USERNAME = '%s'" % userName
    result = zmonlib.ExecSql(sql)
    try:
        record = result[0][0]
        for product in eval(record):
            ret.add(product)
    except Exception,e:
        pass
    logging.debug("get PRODUCT from user by %s,return %s" % (userName, ret))
    return ret
