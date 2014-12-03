#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import logging
import sys
import redis
import MySQLdb
import zmq
import socket
import threading
import time
import yaml
import CmdTransmit

logging.basicConfig(filename='log/zui.log', format='%(levelname)s %(asctime)s %(filename)s %(lineno)d %(funcName)s %(message)s', level=logging.DEBUG)

class ZmqThread(threading.Thread):
    def __init__(self, ip, port, cmd):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.cmd = cmd

    def run(self):
        try:
            logging.debug('send cmd %s to ip: %s, port: %s' % (self.cmd, self.ip, self.port))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                s.connect((self.ip,self.port))  #'*.*.*.*'写上你要接入的IP地址
                s.close()
            except Exception, e:
                logging.exception('send cmd %s to ip: %s, port: %s error: %s' % (self.cmd, self.ip, self.port, e))
                s.close()
                return
            ctx = zmq.Context()
            pub = ctx.socket(zmq.PUB)
            pub.connect('tcp://%s:%s' % (self.ip, self.port))
            pub.setsockopt(zmq.HWM, 1024)
            pub.send_multipart(self.cmd)
        except Exception,e:
            logging.exception(e)

def Init():
	#InitPath()
	InitLog()

def InitPath():
	sys.path.insert(0,'/home/space/zmon/python/lib')
	sys.path.insert(0,'/home/space/zmon/redis/python"')
	sys.path.insert(0,'/home/space/zmon/scripts/rms"')

def InitLog():
	logging.basicConfig(filename='log/zui.log', format='%(levelname)s %(asctime)s %(filename)s %(lineno)d %(funcName)s %(message)s', level=logging.DEBUG)

def ExecSql(sql):
    try:
        f = open('conf/zui.yaml')
        conf = yaml.load(f)
        f.close()
        mysqlIp = conf['mysql']['ip']
        mysqlPort = int(conf['mysql']['port'])
        mysqlUser = conf['mysql']['user']
        mysqlPass = conf['mysql']['pass']
        conn = MySQLdb.connect(host=mysqlIp,port=mysqlPort,user=mysqlUser,passwd=mysqlPass,db='zmon')
        cursor = conn.cursor()
    except Exception,e:
        logging.exception('Connet to mysql faile!, error: %s' % e)
        return None
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        logging.debug('Execute sql : "%s" success! Return rusult : %s' % (sql, result))
        return result
    except Exception,e:
        logging.exception('Execute Sql Raise Exception')
        return None
    finally:
        cursor.close()
        conn.close()

def SendCmd(ip, port, cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip,port))
        s.close()
    except Exception:
        s.close()
        return
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    pub.connect('tcp://%s:%s' % (ip,port))
    pub.setsockopt(zmq.HWM, 1024)
    logging.debug('send cmd %s to ip: %s, port: %s' % (cmd, ip, port))
    pub.send_multipart(cmd,zmq.NOBLOCK)

def GetRedis(productname, monitor):
    try:
        result = ExecSql("select IP,PORT from redis where TYPE = '%s'" % productname)
        ip = result[0][0]
        port = int(result[0][1])
        logging.debug('productname : %s, monitor: %s get redis success, result: [ip : %s, port : %s]' % (productname, monitor, ip, port))
        return ip,port
    except:
        logging.error('Get Redis from mysql is null, productname : %s, monitor: %s' %(productname, monitor))
        return None,None

#把字符串转换成列表，同时对列表中的元素进行简单处理，如strip等
def strToList(scrString, separator = None):
	resultList = []
	tmplist = scrString.split(separator)
	for i in tmplist:
		if not i == '':
			t = i.strip().replace(' ','')
			resultList.append(t)
	return resultList


#根据分隔符把列表转换成字符串
def listToStr(scrList, separator = ','):
	resultStr = ''
	for i in scrList:
		if not i == '':
			resultStr += '%s%s' % (i, separator)
	return resultStr.rstrip(separator)

#操作后端的zcm，zpush，ztail等
def controlBackend(monitorId, oper='ZMON_RELOAD'):
    sql = "select NAME,PRODUCT from monitor where MONITOR_ID = '%s'" % monitorId
    result = ExecSql(sql)
    try:
        monitorName = result[0][0]
        product = result[0][1]
    except Exception,e:
        logging.exception(e)
        return False
    cmd = [oper, str(monitorName), str(product)]
    #操作zcm
    zcmIp = getZcmIp(str(product), str(monitorName))
    if zcmIp == None:
        logging.warning('get zcm ip by product: %s, monitorName: %s return None' % (product, monitorName))
        return False
    #待发送命令队列
    logging.debug('init CmdTransmit')
    logging.debug(CmdTransmit.CMD_TRANSMIT_EXIT_TAG)
    ct = CmdTransmit.CmdTransmit()
    logging.debug(CmdTransmit.CMD_TRANSMIT_EXIT_TAG)
    logging.debug('send cmd')
    ct.sendCmd(zcmIp,7888,cmd)
    ct.sendCmd(zcmIp,7999,cmd)
    #操作ztail
    hostIps = getHostIps(monitorId)
    if hostIps != None:
        for hostIp in hostIps:
            ct.sendCmd(hostIp,7111,cmd)
    ct.wait()
    ct.stop()


#操作后端的zcm，zpush，ztail等
def controlBackend1(monitorId, oper='ZMON_RELOAD'):
    sql = "select NAME,PRODUCT from monitor where MONITOR_ID = '%s'" % monitorId
    result = ExecSql(sql)
    try:
        monitorName = result[0][0]
        product = result[0][1]
    except Exception,e:
        logging.exception(e)
        return False
    cmd = [oper, str(monitorName), str(product)]
    #操作zcm
    zcmIp = getZcmIp(str(product), str(monitorName))
    if zcmIp == None:
        logging.warning('get zcm ip by product: %s, monitorName: %s return None' % (product, monitorName))
        return False
    #待发送命令队列
    cmdQueue = []
    cmdQueue.append((zcmIp,7888,cmd))
    cmdQueue.append((zcmIp,7999,cmd))
    #操作ztail
    hostIps = getHostIps(monitorId)
    if hostIps != None:
        for hostIp in hostIps:
            cmdQueue.append((hostIp,7111,cmd))
    #开启多线程发送命令
    threads = []
    try:
        for cmd in cmdQueue:
            t = ZmqThread(cmd[0], cmd[1], cmd[2])
            threads.append(t)
        for t in threads:
            #logging.debug('run cmd thread: %s ' % str(cmd))
            #t.setDaemon(True)
            t.start()
        startTime = time.time()
        #等待线程退出，超时3秒
        while threading.activeCount() > 1:
            waitTime = time.time() - startTime
            #等待时间小于3秒则继续等待
            if waitTime < 3:
                time.sleep(0.1)
            else:
                break
        logging.debug('reload all backends of monitorId: %s success!' % monitorId)
        return True
    except Exception,e:
        logging.exception('reload all backends of monitorId: %s error! %s' % (monitorId, e))
        return False

    
#取到监控项关联的机器
def getHostIps(monitorId):
    sql = 'select h.IP from host h,host_monitor hm where h.HOST_ID = hm.HOST_ID and hm.MONITOR_ID = "%s"' % monitorId
    result = ExecSql(sql)
    if result:
        logging.debug("get HostIps by monitorId:%s success!" % monitorId)
        return [ rec[0] for rec in result ]
    else:
        logging.error("get HostIps by monitorId:%s faile!" % monitorId)
        return None

#取到产品线对应的zcm部署地址
def getZcmIp(product, monitorName):
    sql = "select IP from redis where TYPE = '%s'" % product
    result = ExecSql(sql)
    try:
        logging.debug("get Zcm (%s,%s) addr success" % (product, monitorName))
        return result[0][0]
    except:
        logging.error("get Zcm (%s,%s) addr faile" % (product, monitorName))
        return None

#取到监控项关联的正则表达式
def getRegularIds(monitorId):
    sql = 'select REGULAR_ID_LIST from monitor where MONITOR_ID = "%s"' % monitorId
    result = ExecSql(sql)
    if result:
        return eval(result[0][0])
    else:
        return None

#删除zcmkey在redis中的值
def deleteRedis(product, monitorName):
    try:
        r = GetRedis(product, monitorName)
        db = redis.Redis(r[0], r[1])
        key = getZcmKey(product, monitorName)
        for db_key in db.keys():
            if db_key.startswith('%s\x01' % key):
                db.delete(db_key)
    except Exception,e:
        logging.exception(e)

def getProducts():
    sql = "select TYPE from redis"
    result = ExecSql(sql)
    products = []
    for rec in result:
        products.append(rec[0])
    products.sort()
    return products

def getZcmKey(product, monitor):
    return '/zmon/monflow/%s/%s' % (product, monitor)


def getHostId(hostIp):
    sql = "select HOST_ID from host where IP = '%s'" % hostIp
    result = ExecSql(sql)
    try:
        return result[0][0]
    except Exception,e:
        return -1

def addHost(hostIp):
    try:    
        hostname = socket.gethostbyaddr(hostIp)[0].replace('.baidu.com','') 
        sql = "insert into host(NAME,IP) values('%s','%s')" % (hostname, hostIp)
        ExecSql(sql)
    except Exception,e:
        logging.exception("add hostIp:%s to mysql error: %s" % (hostIp,e))
        return -1
    return getHostId(hostIp)

