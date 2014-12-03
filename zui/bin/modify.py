#!/home/zxr/zmon/python/bin/python
#-*- coding:UTF-8 -*-
import json
import web
import yaml
import logging
import MySQLdb
import socket
import zmonlib
import re
import auth
import baiduNameService

render = web.template.render('templates')

def loadMonitor(monitorId):
    sql = 'select NAME,PRODUCT,LOGPATH,GREP,GREPV,BNS,REGULAR_ID_LIST,UITREE,UICHART from monitor where MONITOR_ID=%s' % monitorId
    result = zmonlib.ExecSql(sql)
    try:
        monitorname = result[0][0]
        product = result[0][1]
        logpath = result[0][2]
        grep = result[0][3]
        grepv = result[0][4]
        serviceName = result[0][5]
        hostlist = ''
        reIdList = eval(result[0][6])
        UITREE = eval(result[0][7])
        UICHART = eval(result[0][8])
        relist = []
        treelist = []
        results = []
        index = 0
        for regularId in reIdList:
            sql = 'select REGULAR_ID,NAME,EXPRESSION from regular where REGULAR_ID = "%s"' % regularId
            result = zmonlib.ExecSql(sql)
            results.extend(result)
        for regular in results:
            if regular[1] in UICHART:
                relist.append([index, regular[1], regular[2], True, UICHART[regular[1]]])
            else:
                relist.append([index, regular[1], regular[2], False, 'sum'])
            index += 1
        for key in UITREE:
            treelist.append([index, key, UITREE[key]])
            index += 1
        if serviceName==None or serviceName=='':
            sql = 'select h.NAME from host h,host_monitor hm where h.HOST_ID = hm.HOST_ID and hm.MONITOR_ID = "%s"' % monitorId
            result = zmonlib.ExecSql(sql)
            for rec in result:
                hostlist += '%s\n' % rec[0]
        else:
            serviceName = serviceName.replace(',','\n')
            hostlist = ''
    except Exception,e:
        logging.exception(e)
        return None
    logging.debug('[monitorId:%s] [product:%s] [monitorname:%s] [logpath:%s] [serviceName:%s] [grep:%s] [grepv:%s] [relist:%s] [treelist:%s]' % (monitorId, product, monitorname, logpath, serviceName, grep, grepv, relist, treelist))
    return (monitorId, product, monitorname, logpath, serviceName, grep, grepv, relist, treelist, hostlist)

class modify(object):
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
        self.getInput()
        self.checkData()
        self.updateMysql()
        self.reloadBackend()
        self.cursor.close()
        self.conn.close()
        return json.dumps(self.result)

    def GET(self):
        try:
            monitorId = self.input['monitorId']
        except:
            return web.notfound(u'监控项不能为空')
        #加载监控项详情
        conf = loadMonitor(monitorId)
        if conf == None:
            return web.notfound(u'加载配置错误')
        monitorId, product, monitorname, logpath, serviceName, grep, grepv, relist, treelist, hostlist = conf
        #检查是否有权限
        userName = auth.uuap_sso()
        products = auth.getProcByName(userName)
        if products==None or len(products)==0 or not product in products:
            web.config.session.kill()
            return render.forbidden(userName)
        return render.modify(userName, monitorId, product, monitorname, logpath, serviceName, grep, grepv, relist, treelist, hostlist)

    def delRegulars(self):
        if self.result['code'] != 300:
            return
        sql = 'select REGULAR_ID_LIST from monitor where MONITOR_ID = "%s"' % self.monitorId
        result = zmonlib.ExecSql(sql)
        regularIdList = eval(result[0][0])
        for regularId in regularIdList:
            sql = 'delete from regular where REGULAR_ID = "%s"' % regularId
            zmonlib.ExecSql(sql)

    def getInput(self):
        """
        function: 解析用户输入 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        if self.result['code'] != 300:
            return
        self.monitorId = self.input['monitorId']
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
        #修改的监控项是否存在
        self.cursor.execute("select NAME,PRODUCT from monitor where MONITOR_ID=%s" % self.monitorId)
        if not self.cursor.fetchall():
            self.result = {'code':400,'txt':u'监控项不存在，新建一个吧!'}
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

    def updateMysql(self):
        """
        function: 把配置写入数据库 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        #删除老的正则
        self.delRegulars()
        #插入新的正则
        reguIdList = self.insertRegular()
        #更新监控配置
        self.updateMonitor(reguIdList)
        #删除老的机器关联
        self.deleteHostMonitor()
        #插入新的机器关联
        self.insertHostMonitor()

    def reloadBackend(self):
        if self.result['code'] != 300:
            return
        self.cursor.execute("select MONITOR_ID from monitor where NAME = '%s' and PRODUCT = '%s'" % (self.monitorName, self.product))
        result = self.cursor.fetchall()
        if result != None:
            monitor_id = result[0][0]
            zmonlib.controlBackend(monitor_id)
            self.result = {'code':200,'txt':u'提交成功'}
        else:
            self.result = {'code':400,'txt':u'重启后端失败'}

    def insertRegular(self):
        if self.result['code'] != 300:
            return
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

    def updateMonitor(self,reguIdList):
        """
        function: 写Monitor表 
        args: 无
        return：无
        author: 翟鑫瑞
        """
        if self.result['code'] != 300:
            return
        NAME = self.monitorName
        LOGPATH = self.logPath
        PRODUCT = self.product
        BNS = zmonlib.listToStr(self.serviceName)
        ZCM_ADDR = "tcp://%s:7999" % zmonlib.getZcmIp(PRODUCT, NAME)
        GREP = self.grep.replace('\\','\\\\')
        GREPV = self.grepv.replace('\\','\\\\')
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
        sql = 'update monitor set LOGPATH="%s",BNS="%s",ZCM_ADDR="%s",GREP="%s",GREPV="%s",KEY_ID_LIST="%s", \
               VALUE_ID_LIST="%s",REGULAR_ID_LIST="%s",UITREE="%s",UICHART="%s" where MONITOR_ID=%s' \
               % (LOGPATH,BNS,ZCM_ADDR,GREP,GREPV,KEY_ID_LIST,VALUE_ID_LIST,REGULAR_ID_LIST,str(UITREE),str(UICHART),self.monitorId)
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

    def deleteHostMonitor(self):
        if self.result['code'] != 300:
            return
        try:
            sql = 'delete from host_monitor where MONITOR_ID=%s' % self.monitorId
            self.cursor.execute(sql)
            self.cursor.fetchall()
        except Exception,e:
            self.result = {'code':400,'txt':u'清理HostMonitor表失败,错误:%s'%e}

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
        for host in self.hostlist:
            self.addHostToMonitor(host[1], self.monitorId) 

if __name__ == '__main__':
    req = "{'product': u'space', 'grep': u'grep', 're_name_server': u'\\[server .*\\]', 'allfield': u'idc,server_ip,reqip,server,flow', 'logpath': u'/home/space/imgcache', 'chart_name_flow': u'false', 'chart_name_server': u'false', 'hostlist': u'jx-space-god.jx', 'node_name_product': u'reqip,server', 'node_name_server': u'idc,server_ip', 'grep-v': u'grep -v', 'chart_name_reqip': u'true', 're_name_reqip': u'\\[reqip .*\\]', 'monitorname': u'imgcache1'}"
    req = eval(req)
    c = modify()
    ret = c.POST(req)
    print ret
    
