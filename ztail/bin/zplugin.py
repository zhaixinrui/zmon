#!/usr/bin/env python
#-*- coding: UTF8 -*-
import socket
import os

#进程退出标志
EXIT_TAG = {}
#idc
def getidc(hostname):
	JX = ('jx', 'ai', 'yf', 'cq01')
	HZ = ('hz01')
	if hostname.startswith(JX):
        	return 'JX'
	elif hostname.startswith(HZ):
        	return 'HZ'
	else:
        	return 'TC'

#插件字典，通用的关键字段获取方式可以放在这里
DICT={}
DICT['hostname'] = os.uname()[1].replace('.baidu.com','')
DICT['idc'] = getidc(DICT['hostname'])
DICT['server_ip'] = socket.gethostbyname(DICT['hostname'])
DICT['flow'] = 1

#比较变量
def compare(left, condition, right):
    """return (left condition right)"""
    if condition == '<':
        return left < right
    elif condition == '<=':
        return left <= right
    elif condition == '==':
        return left == right
    elif condition == '!=':
        return left != right
    elif condition == '>':
        return left > right
    elif condition == '>=':
        return left >= right
