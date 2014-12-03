#!/usr/bin/env python
#-*- coding: UTF8 -*-
"""
文件名：ztail.py
功能：采集日志的客户端脚本，监听远程的控制命令
作者：程良渝
修改人：翟鑫瑞，加入端口监听机制，加入多线程机制，每个日志一个采集线程,配置改为从数据库读取
"""
import sys,os
import time
import socket
import signal
import copy
import re
#import MonitorProcess
import TailProcess
from zbase import ZBase


#主进程被终止时的处理方法，保证主进程退出后子线程能够正常出
def SignalHandler(sig,id):
    sys.exit()
signal.signal(signal.SIGINT,SignalHandler)
signal.signal(signal.SIGTERM,SignalHandler)

def getLogs(logPath):
    """根据模糊路径查找匹配的日志文件列表"""
    logPaths = set()
    #不使用模糊匹配
    if logPath.find('*') == -1:
        logPaths.add(logPath)
    #使用模糊匹配
    else:
        ret = os.popen('ls %s' % logPath)
        if not re.search(r'No such file or directory', repr(ret)):
            for path in ret:
                path = path.strip()
                os.path.isfile(path)
                os.path.islink(path)
                #文件或软链类型才有效，避免引入目录
                if os.path.isfile(path) or os.path.islink(path):
                    logPaths.add(path)
    return logPaths

class MonitorMain(ZBase):
    """
    function: 日志采集模块的主进程，负责处理远程命令并对具体的日志采集进程进行控制
    author: 翟鑫瑞
    """
    def __init__(self):
        ZBase.__init__(self,'ZTail')
        self.conf = {}
        #维护当前正在运行的进程，便于创建和清理
        self.tailProcess = {}

    @classmethod
    def getInstance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def loadconfs(self):
        """
        function: 从数据库加载配置文件 
        args: None
        return：None
        author: 翟鑫瑞
        """
        hostname = os.uname()[1].replace('.baidu.com','')
        ip = socket.gethostbyname(socket.gethostname())
        #get monitors_id by host
        result = self.ExecSql("select m.MONITOR_ID from host h,host_monitor m where h.HOST_ID = m.HOST_ID and (h.IP = '%s')" % ip);
        if not result:
            self.logger.error('%s did not hava any monitor in database zmon' % hostname)
            return
        for monitors in result:
            monitors_id = monitors[0]
            #通过MONITOR_ID取得对应监控的配置
            result = self.ExecSql("select NAME,LOGPATH,PRODUCT,ZCM_ADDR,REWORK_TIME,REPORT_TIME,MAX_TIME,HIGH_WATER_MARK,GREP,GREPV,KEY_ID_LIST,VALUE_ID_LIST,REGULAR_ID_LIST from monitor where MONITOR_ID = '%s'" % monitors_id)
            for rec in result:
                self.getModuleConf(rec)

    def loadModules(self):    
        """
        function: 增加一个新的日志监控模块 
        args: None
        return：None
        author: 翟鑫瑞
        """
        for modname in self.conf:
            self.tailProcess[modname] = []
            conf = copy.deepcopy(self.conf[modname])
            for logPath in getLogs(conf['log_path']):
                if logPath in self.tailProcess:
                    continue
                conf['log_path'] = logPath
                tp = TailProcess.TailProcess(modname, conf)
                tp.start()
                self.tailProcess[modname].append(tp)
                self.logger.info('start TailProcess %s success, the conf is: %s' % (modname, conf))
            self.logger.info('start MonitorProcess %s success, the conf is: %s' % (modname, self.conf[modname]))

    def reloadModule(self, modname, product):
        """
        function: 重新加载一个日志采集模块，用于修改配置后重载配置
        args: modname -> 要重载的模块名
        return：None
        author: 翟鑫瑞
        """
        self.delModule(modname, product)
        self.addModule(modname, product)

    def addModule(self, modname, product):
        """
        function: 新增一个日志采集模块
        args: modname -> 增加的模块名
        return：None
        author: 翟鑫瑞
        """
        if modname in self.tailProcess:
            self.logger.warning('add module faile! module : %s has already exsited!' % modname)
            return
        try:
            result = self.ExecSql("select NAME,LOGPATH,PRODUCT,ZCM_ADDR,REWORK_TIME,REPORT_TIME,MAX_TIME,HIGH_WATER_MARK,GREP,GREPV,KEY_ID_LIST,VALUE_ID_LIST,REGULAR_ID_LIST from monitor where NAME = '%s' and PRODUCT = '%s'" % (modname, product))
            self.getModuleConf(result[0])
            #增加日志
            self.tailProcess[modname] = []
            conf = copy.deepcopy(self.conf[modname])
            for logPath in getLogs(conf['log_path']):
                if logPath in self.tailProcess:
                    continue
                conf['log_path'] = logPath
                tp = TailProcess.TailProcess(modname, conf)
                tp.start()
                self.tailProcess[modname].append(tp)
                self.logger.info('start TailProcess %s success, the conf is: %s' % (modname, conf))
            self.logger.info('add module %s success, the conf is: %s' % (modname, self.conf[modname]))
        except Exception,e:
            self.logger.exception('add module %s error: %s' % (modname, e))

    #清理TailProcess子进程
    def stop(self):
        for modname in self.tailProcess:
            for process in self.tailProcess[modname]:
                try:
                    if process.is_alive():
                        process.terminate()
                        process.join()
                    self.logger.info('send terminate sinal to module %s success!' % modname)
                except Exception,e:
                    self.logger.exception('send terminate sinal to module %s error : %s' % (modname, e))
        sys.exit()

    def delModule(self, modname, product):
        """
        function: 删除一个日志采集模块
        args: modname -> 删除的模块名
        return：None
        author: 翟鑫瑞
        """
        if not modname in self.tailProcess:
            self.logger.warning('delete module faile! module : %s do not exsit!' % modname)
            return
        try:
            for process in self.tailProcess[modname]:
                if process.is_alive():
                    process.terminate()
                    process.join()
            self.tailProcess.pop(modname)
            self.logger.info('delete module %s success!' % modname)
        except Exception,e:
            self.logger.exception('delete module %s error : %s' % (modname, e))

    def getModuleConf(self, row):
        """
        function: 解析从数据库取到的配置
        args: None
        return：None
        author: 翟鑫瑞
        """
        modname = row[0]
        self.conf[modname] = {}
        self.conf[modname]['log_path'] = row[1]
        self.conf[modname]['zcm_key'] = '/zmon/monflow/%s/%s' % (row[2], row[0])
        self.conf[modname]['zcm_addr'] = row[3]
        self.conf[modname]['rework_time'] = float(row[4])
        self.conf[modname]['report_time'] = int(row[5])
        self.conf[modname]['max_size'] = int(row[6])
        self.conf[modname]['high_water_mark'] = int(row[7])
        self.conf[modname]['grep'] = row[8]
        self.conf[modname]['grepv'] = row[9]
        self.conf[modname]['key_names'] = self.strToList(row[10], ',')
        self.conf[modname]['value_names'] = self.strToList(row[11], ',')
        self.conf[modname]['regular'] = []
        regulars = eval(row[12])
        for reid in regulars:
            result = self.ExecSql("select NAME,EXPRESSION,TRANSFORM from regular where REGULAR_ID = '%d'" % int(reid))
            if result:
               self.conf[modname]['regular'].append( {'key':result[0][0].strip() , 'expression': r'%s' % result[0][1].replace(r'\\\\',r'\\'), 'transform':None if result[0][2]==None else result[0][2].strip()} )
        self.logger.debug('get %s\'s conf from mysql seccess,the conf is %s' % (modname, self.conf[modname]))

    def listen(self):
        """
        function: 监听端口，接受远程命令并进行处理
        args: None
        return：None
        author: 翟鑫瑞
        """
        time.sleep(1)
        while True:
            command = self.sub.recv_multipart()
            action = command[0]
            objects = command[1]
            product = command[2]
            self.logger.info('receive command : %s, object : %s' % (action, objects))
            if action == 'ZMON_RELOAD':
                for modname in objects.split(','):
                    self.reloadModule(modname, product)
            elif action == 'ZMON_ADD':
                for modname in objects.split(','):
                    self.addModule(modname, product)
            elif action == 'ZMON_DELETE':
                for modname in objects.split(','):
                    self.delModule(modname, product)
            elif action == 'ZMON_EXIT':
                os.popen("echo 'dx' > status/ztail/svcontrol")
                sys.exit()

                 
                 
if __name__ == '__main__':
    iMonitorMain = MonitorMain.getInstance()
    iMonitorMain.loadconfs()
    iMonitorMain.loadModules()
    iMonitorMain.initSub()
    iMonitorMain.listen()
