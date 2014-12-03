#!/usr/bin/env python
#-*- coding: UTF8 -*-
"""
文件名：ztail.py
功能：采集日志的客户端脚本，监听远程的控制命令
作者：程良渝
修改人：翟鑫瑞，加入端口监听机制，加入多线程机制，每个日志一个采集线程,配置改为从数据库读取
"""
import time
import re
import multiprocessing
import cPickle
from collections import defaultdict
import zmq
import rms
import tail
from zbase import ZBase
import zplugin


#rms
def getRms(ip):
    try:
        return rms.rms_product(ip)
    except Exception,e:
        return e

#日志采集进程
class TailProcess(multiprocessing.Process, ZBase):   
    def __init__(self, name=None, conf=None):   
        multiprocessing.Process.__init__(self,name = name)
        ZBase.__init__(self,'TailProcess_%s' % name)
        self.name = name
        self.conf = conf
        self.tailer = tail.Tail(self.conf['log_path'], self.conf['max_size']) 
        self.data = {}
        self.analyseResult = zplugin.DICT
        self.regular = {}
        self.transform = {}
        self.initRegular()
    
    def initRegular(self):
        """
        function: 初始化正则表达式，预编译以提高效率
        args: None
        return：None
        author: 翟鑫瑞
        """
        for key, regular in map(lambda _: (_['key'], _['expression']), self.conf['regular']):
            try:
                self.regular[key] = re.compile(r'%s' % regular)
                self.logger.debug("initRegular : [key: %s] [expression: %s]" % (key, r'%s' % regular))
            except Exception,e:
                self.logger.exception("initRegular : [key: %s] [expression: %s],error:%s" % (key, r'%s' % regular, e))
        for key, transform in map(lambda _: (_['key'], _['transform']), self.conf['regular']):
            if transform != None and transform != '':
                self.transform[key] = transform
                self.logger.debug("initRegular : [key: %s] [transform: %s]" % (key, r'%s' % transform))
        #初始化grep
        if self.conf['grep'] == None or self.conf['grep'] == '':
            self.grep = None
        else:
            self.grep = re.compile(r'%s' % self.conf['grep'].replace(r'\\\\',r'\\'))   
        #初始化grepv
        if self.conf['grepv'] == None or self.conf['grepv'] == '':
            self.grepv = None
        else:
            self.grepv = re.compile(r'%s' % self.conf['grepv'].replace(r'\\\\',r'\\'))   

    def initZmq(self):
        """
        function: 初始化采集模块的Zmq对象，用于向Zcm发送采集到的数据 
        args: None
        return：None
        author: 翟鑫瑞
        """
        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.setsockopt(zmq.HWM, self.conf['high_water_mark'])
        self.pub.connect(self.conf['zcm_addr'])
        #self.logger.debug("Connect zcm : %s success!" % self.conf['zcm_addr'])
    
    def destoryZmq(self):
        """
        function: 断开连接
        args: None
        return：None
        author: 翟鑫瑞
        """
        self.pub.close()
        self.ctx.destroy()
        #self.logger.debug("Destory zcm : %s success!" % self.conf['zcm_addr'])

    def getValueByRe(self,key,line):
        """
        function: 用正则从一行日志中过滤出需要的值
        args: key -> self.regular字典的key
        line -> 要处理的日志，通常为一行
        return：正则过滤出的值，成功则返回提取的值，如果未做提取，仅作匹配则返回1，失败则返回0
        author: 翟鑫瑞
        """
        #提取值
        ret = 0
        try:
           result = self.regular[key].search(line)
           if result:
               try:
                   ret = result.group(1)
               except:
                   ret = 1
           else:
               ret = 0
        except Exception, e:
           #self.logger.debug('Regular : %s return 0. The line is %s' % (key, line))
           ret = 0

        if key in self.transform:
            return self.transformValue(key, ret)
        else:
            return ret

    #结果进行后续处理
    def transformValue(self, key, srcValue):
        ret = 0
        if self.transform[key] == 'RMS':
            ret = getRms(srcValue)
            self.logger.debug('transform key: %s,srcValue: %s,return: %s' % (key, srcValue, ret))
        return ret
    

    def processLine(self,line):
        """
        function: 分析一行日志，取出需要的所有字段 
        args: line -> 一行日志数据
        return：返回一个元组，分别为key和value
        author: 翟鑫瑞
        """
        #用正则取关键值
        for key in self.regular:
            self.analyseResult[key] = self.getValueByRe(key,line)
            #self.logger.debug("[key: %s] [expression: %s] [rusult: %s]" % (key, regular, self.analyseResult[key]))
        #用上面取到的值构造返回值，转成元组形式    
        keytuple = tuple([self.analyseResult.get(x,0) for x in self.conf['key_names']])
        valuetuple = tuple([self.analyseResult.get(x,0) for x in self.conf['value_names']])
        return keytuple,valuetuple

#    def getanalyseResult(self,key):
#        """
#        function: 
#        args: None
#        return：None
#        author: 翟鑫瑞
#        """
#        if key in self.analyseResult:
#            return self.analyseResult[key]
#        elif key in DICT:
#            return DICT.get(key,0)
#        else:
#            self.logger.error('key: %s did not in analyseResult: %s' % (key,self.analyseResult))
#            return 0
    
    #提前过滤日志，检查是否需要处理，如用来过滤debug日志等
    def needProcess(self, line):
        result = True
        #如果grep不存在表明不需要过滤，全部需要处理
        if not self.grep:
            result = True
        else:
            #如果grep存在且符合正则则需要处理,不进行过滤
            if self.grep.search(line):
                result = True
            else:
                result = False
                return result
        #如果grepv存在且符合正则则不需要处理
        #如果grepv不存在表明不需要过滤，全部需要处理
        if not self.grepv:
            result = True
        else:
            #如果grepv存在且符合正则则过滤掉这部分日志，不进行处理
            if self.grepv.search(line):
                result = False
                return result
            else:
                result = True
        return result

    def analyse(self):
        """
        function:分析日志文件，并把分析结果发送给Zcm 
        args: None
        return：None
        author: 程良渝
        modifier: 翟鑫瑞
        change: 改进配置加载方式，改进处理流程，加入日志打印
        """
        self.logger.debug('Begin to analyse the log, the conf is : %s' % self.conf)
        for name in self.conf['value_names']:
            self.data[name] = defaultdict(float)
        last_report = int(time.time() / self.conf['report_time']) * self.conf['report_time']
        while 1:
            time.sleep(self.conf['rework_time'])
            for line in self.tailer:
                if self.needProcess(line):
                    #self.logger.debug('Process Line Begin')
                    key_list, value_list = self.processLine(line)
                    #self.logger.debug('ProcessLine get result key : %s , value : %s' % (key_list, value_list))
                    for i, name in enumerate(self.conf['value_names']):
                        try:
                            self.data[name][key_list] += float(value_list[i])
                        except: 
                            pass
            now = int(time.time() / self.conf['report_time']) * self.conf['report_time']
            if now != last_report:
                if now == last_report + self.conf['report_time']:
                    dump = cPickle.dumps({'time': last_report, 'key_names': self.conf['key_names'], 'data': self.data}, cPickle.HIGHEST_PROTOCOL)
                    self.send_data(dump)
                    self.logger.debug('[zcm_key :%s] [time :%s] [key_names :%s] [data : %s]' % (self.conf['zcm_key'], last_report, self.conf['key_names'], self.data))
                    self.logger.debug('[key_names :%s]' % self.conf['key_names'])
                    self.logger.debug('[data : %s]' % self.data)
                for value_name in self.data:
                    self.data[value_name].clear()
                last_report = now   

    def send_data(self, dump):
        try:
            self.initZmq()
            self.pub.send_multipart((self.conf['zcm_key'], dump))
            self.destoryZmq()
            self.logger.info('send data to %s %s' % (self.conf['zcm_addr'], self.conf['zcm_key']))
        except Exception,e:
            self.logger.exception('send data to %s %s fail, error:%s' % (self.conf['zcm_addr'], self.conf['zcm_key'], e))

    def run(self):
        """
        function: 子进程的start()方法
        args: None
        return：None
        author: 翟鑫瑞
        """
#        try:
#            self.initZmq()
#        except:
#            self.logger.exception('initZmq error: %s' % e)
#            sys.exit()
        while 1:
            try:
                self.analyse()
            except Exception,e:
                self.logger.exception('analyse log error: %s' % e)
                time.sleep(0.1)


