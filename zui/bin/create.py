#!/home/zxr/zmon/python/bin/python
#-*- coding:UTF-8 -*-
import json
import web
import time
import yaml
import logging
import MySQLdb
import socket
import zmonlib
import re
import auth
import baiduNameService

render = web.template.render('templates')

class create(object):
    def __init__(self):
        self.input = web.input()
        zmonlib.Init()
        self.keylist = []
        self.valuelist = []
        #default:300 success:200 error:400
        self.result = {'code':300,'txt':'unknown error'}
        self.EXEC_ID_LIST = ''
        try:
            self.InitConf()
            self.conn = MySQLdb.connect(host=self.mysqlIp,port=self.mysqlPort,user=self.mysqlUser,passwd=self.mysqlPass,db='zmon')
            self.cursor = self.conn.cursor()
        except Exception, e:
            self.result = {'code':400,'txt':'conn mysql error: %s' % e}
            logging.exception(e)

    def InitConf(self):
        f = open('conf/zui.yaml')
        self.yaml = yaml.load(f)
        f.close()
        self.mysqlIp = self.yaml['mysql']['ip']
        self.mysqlPort = int(self.yaml['mysql']['port'])
        self.mysqlUser = self.yaml['mysql']['user']
        self.mysqlPass = self.yaml['mysql']['pass']

    def POST(self):
        logging.debug('%s \n' % str(self.input))
        self.getInput()
        self.checkData()
        self.insertMysql()
        self.reloadBackend()
        self.cursor.close()
        self.conn.close()
        return json.dumps(self.result)

    def GET(self):
        userName = auth.uuap_sso()
        products = auth.getProcByName(userName)
        if products==None or len(products)==0:
            web.config.session.kill()
            return render.forbidden(userName)
        if self.input == None or len(self.input) == 0:
            return render.create(userName, products, web.ctx.homedomain)

    def getInput(self):
        """
        function: 解析用户输入 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        if self.result['code'] != 300:
            return
        self.product = self.input['product']
        self.monitorName = self.input['monitorname'].strip().replace(' ','')
        self.logPath = self.input['logpath'].strip().replace(' ','')
#        self.hostlist = zmonlib.strToList(self.input['hostlist'])
        self.serviceName = zmonlib.strToList(self.input['serviceName'])
        self.hostName = zmonlib.strToList(self.input['hostName'])
        self.grep = self.input['grep']
        self.grepv = self.input['grep-v']
        self.allfield = zmonlib.strToList(self.input['allfield'], ',')
        self.reList = {}
        self.nodeList = {}
        self.chartList = {}
        for key in self.input.keys():
            if key.startswith('re_name_'):
                re_name = key.replace('re_name_','').strip().replace(' ','')
                self.reList[re_name] = self.input[key]
                logging.debug("regular item : %s  %s\n" % (re_name,self.reList[re_name])) 
            elif key.startswith('node_name_'):
                node_name = key.replace('node_name_','').strip().replace(' ','')
                self.nodeList[node_name] = zmonlib.strToList(self.input[key], ',')
                logging.debug("tree node item : %s  %s\n" % (node_name,self.nodeList[node_name])) 
            elif key.startswith('chart_name_'):
                chart_name = key.replace('chart_name_','').strip().replace(' ','')
                self.chartList[chart_name] = self.input[key]
                logging.debug("tree chart item : %s  %s\n" % (chart_name,self.chartList[chart_name])) 

    def checkData(self):
        """
        function: 检查用户输入的正确性，根据检查的结果修改全局变量self.result 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        #监控项名不能和产品线内已有的监控名重复
        self.cursor.execute("select * from monitor where NAME = '%s' and PRODUCT = '%s'" % (self.monitorName, self.product))
        if self.cursor.fetchall():
            self.result = {'code':400,'txt':u'产品线 %s 已有监控项 %s ，改个名儿吧!' % (self.product, self.monitorName)}
            return
        #正则表达式是否正确
        for reName in self.reList:
            try:
                re.compile(self.reList[reName])
            except Exception,e:
                self.result = {'code':400,'txt':u'正则表达式[%s]有误，请注意检查,错误信息:[%s]' % (reName, e)}
                logging.exception('wrong regular: %s,Exception:%s' % (self.reList[reName],e))
                return
        #检查bns是否有效
        self.hostlist = []
        for name in self.serviceName:
            hostlist = baiduNameService.getInstanceByService(name)
            if len(hostlist) == 0:
                self.result = {'code':400,'txt':u'通过BNS:%s获取机器列表失败,错误' % name}
                return
            self.hostlist.extend(hostlist)
        #bns失效后获取尝试用机器名取机器列表
        logging.debug(self.hostlist)
        if len(self.hostlist) == 0:
            re_host_name = re.compile(r'.*-.*-.*\..*')
            re_host_ip = re.compile(r'\d+(?:\.\d+){3}')
            for name in self.hostName:
                try:
                    logging.debug(name)
                    if re_host_name.search(name) or re_host_ip.search(name):
                        ip = socket.gethostbyname(name)
                        self.hostlist.append((name, ip))
                    else:
                        self.result = {'code':400,'txt':u'[%s]不是有效的机器名或IP' % name}
                        return
                except Exception,e:
                    self.result = {'code':400,'txt':u'通过机器名[%s]获取IP失败，请注意检查，错误信息:[%s]' % (name, e)}
                    logging.exception('wrong hostname: %s,Exception:%s' % (name,e))
                    return
        #bns和机器名都失败后证明输入有误，直接返回
        logging.debug(self.hostlist)
        if len(self.hostlist) == 0:
            self.result = {'code':400,'txt':u'通过BNS和机器名获取机器列表失败'}
            return
        #keylist和valuelist中的值要先定义过
        for node_name in self.nodeList:
            for field in self.nodeList[node_name]:
                if not field in self.allfield:
                    self.result = {'code':400,'txt':u'%s 尚未定义！' % field}
                    return
        for chart in self.chartList:
            if not chart in self.allfield:
                self.result = {'code':400,'txt':u'%s 尚未定义！' % chart}
                return

    def insertMysql(self):
        """
        function: 把配置写入数据库 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        if self.result['code'] != 300:
            return
        reguIdList = self.insertRegular()
        if self.result['code'] != 300:
            return
        self.insertMonitor(reguIdList)
        if self.result['code'] != 300:
            return
        self.insertHostMonitor()

    def reloadBackend(self):
        if self.result['code'] != 300:
            return
        self.cursor.execute("select MONITOR_ID from monitor where NAME = '%s' and PRODUCT = '%s'" % (self.monitorName, self.product))
        result = self.cursor.fetchall()
        if result != None:
            monitor_id = result[0][0]
            logging.info(time.time())
            zmonlib.controlBackend(monitor_id)
            logging.info(time.time())
            self.result = {'code':200,'txt':u'提交成功'}
        else:
            self.result = {'code':400,'txt':u'重启后端失败'}

    def insertRegular(self):
        reguIdList = []
        for key,value in self.reList.iteritems():
            try:
                sql = "insert into regular (NAME, EXPRESSION) values ('%s','%s') " % (key,value.replace('\\','\\\\'))
                logging.debug(sql)
                self.cursor.execute(sql)
                self.cursor.execute("select @@IDENTITY")
                result = self.cursor.fetchall()
                reguId = result[0][0]
                reguIdList.append(int(reguId))
            except Exception, e:
                self.result = {'code':400,'txt':u'执行SQL失败: %s' % e}
                return None
        return reguIdList

    def insertMonitor(self,reguIdList):
        """
        function: 写Monitor表 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        NAME = self.monitorName
        BNS = zmonlib.listToStr(self.serviceName)
        LOGPATH = self.logPath
        PRODUCT = self.product
        ZCM_ADDR = "tcp://%s:7999" % zmonlib.getZcmIp(PRODUCT, NAME)
        GREP = self.grep
        GREPV = self.grepv
        KEY_ID_LIST = []
        VALUE_ID_LIST = []
        REGULAR_ID_LIST = reguIdList
        UITREE = {}
        UICHART= {}
        for node_name in self.nodeList:
            UITREE[node_name] = zmonlib.listToStr(self.nodeList[node_name],',')
            KEY_ID_LIST.extend(self.nodeList[node_name])
        for chart in self.chartList:
            VALUE_ID_LIST.append(chart)
            if self.chartList[chart] == 'true':
                UICHART[chart] = 'average'
            else:
                UICHART[chart] = 'sum'
        logging.debug(KEY_ID_LIST)
        KEY_ID_LIST = zmonlib.listToStr(list(set(KEY_ID_LIST)))
        VALUE_ID_LIST = zmonlib.listToStr(list(set(VALUE_ID_LIST)))
        sql = "insert into monitor\
            (NAME,LOGPATH,PRODUCT,BNS,ZCM_ADDR,GREP,GREPV,KEY_ID_LIST,VALUE_ID_LIST,REGULAR_ID_LIST,UITREE,UICHART) \
            values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', \"%s\", \"%s\")" % \
            (NAME,LOGPATH,PRODUCT,BNS,ZCM_ADDR,GREP,GREPV,KEY_ID_LIST,VALUE_ID_LIST,REGULAR_ID_LIST,str(UITREE),str(UICHART))
        try:
            result = self.cursor.execute(sql)
            logging.debug('exec sql: %s\n' % sql)
            logging.debug('get result: %s \n' % result)
        except Exception, e:
            self.result = {'code':400,'txt':u'exec mysql error: %s' % e}
            return

    def insertHost(self, hostname):
        try:
            server_ip = socket.gethostbyname(hostname)
            sql = "insert into host(NAME,IP) values('%s','%s')" % (hostname, server_ip)
            self.cursor.execute(sql)
            self.cursor.execute("select @@IDENTITY")
            result = self.cursor.fetchall()
            hostID = result[0][0]
            return hostID
        except:
            return None

    def addHostToMonitor(self, hostIp, monitorId):
        hostId = zmonlib.getHostId(hostIp)
        if hostId == -1:
             hostId = zmonlib.addHost(hostIp)
        if hostId == -1:
             logging.error('add Host:%s to Monitor:%s error!' % (hostIp, monitorId))
             return
        sql = "select * from host_monitor where HOST_ID=%s and MONITOR_ID=%s" % (hostId, monitorId)
        ret = zmonlib.ExecSql(sql)
        if ret == None or len(ret) == 0:
            sql = "insert into host_monitor(HOST_ID,MONITOR_ID) values('%s' , '%s')" % (hostId, monitorId)
            zmonlib.ExecSql(sql)
            logging.info('add Host:%s To Monitor:%s success!' % (hostIp, monitorId))
        else:
            logging.info('add Host:%s To Monitor:%s duplicate!' % (hostIp, monitorId))

    def insertHostMonitor(self):
        """
        function: 写HostMonitor表 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        logging.debug('begin to insert monitor: %s to host_monitoer.\n' % self.monitorName)
        self.cursor.execute("select MONITOR_ID from monitor where NAME = '%s' and PRODUCT = '%s'" % (self.monitorName, self.product))
        result = self.cursor.fetchall()
        if result == None:
            self.result = {'code':400,'txt':u'插入HostMonitor表失败'}
            return
        monitor_id = result[0][0]
        for host in self.hostlist:
            self.addHostToMonitor(host[1], monitor_id)
#        for hostname in self.hostlist:
#            try:
#                self.cursor.execute("select HOST_ID from host where NAME = '%s'" % hostname)
#                result = self.cursor.fetchall()
#                if result:
#                    host_id = result[0][0]
#                else:
#                    host_id = self.insertHost(hostname)
#                    if not host_id:
#                        self.result = {'code':400,'txt':u'数据库中添加机器%s失败' % hostname}
#                        return
#                self.cursor.execute("insert into host_monitor(HOST_ID,MONITOR_ID) values('%s' , '%s')" % (host_id,monitor_id))
#                server_ip = socket.gethostbyname(hostname)
#            except Exception, e:
#                self.result = {'code':400,'txt':'exec mysql error: %s' % e}
#                logging.exception(e)
           


if __name__ == '__main__':
    req = "{'product': u'space', 'grep': u'grep', 're_name_server': u'\\[server .*\\]', 'allfield': u'idc,server_ip,reqip,server,flow', 'logpath': u'/home/space/imgcache', 'chart_name_flow': u'false', 'chart_name_server': u'false', 'hostlist': u'jx-space-god.jx', 'node_name_product': u'reqip,server', 'node_name_server': u'idc,server_ip', 'grep-v': u'grep -v', 'chart_name_reqip': u'true', 're_name_reqip': u'\\[reqip .*\\]', 'monitorname': u'imgcache1'}"
    req = eval(req)
    c = create()
    ret = c.POST(req)
    print ret
    
