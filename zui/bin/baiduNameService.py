#!/usr/bin/env python
# -*- coding:UTF-8 -*
import os
import re

#re_not_exist = re.compile(r'service not exist')
#re_wrong_param = re.compile(r'input wrong param')
re_ip = re.compile(r'((?:[01]?\d\d?|2[0-4]\d|25[0-5])\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])\.(?:[01]?\d\d?|2[0-4]\d|25[0-5]))')

def getInstanceByService(serviceName):
    #BNS为空直接返回
    if serviceName == None or serviceName == '':
        return []
    #调用get_instance_by_service取到instance，重试5次
    result = []
    for i in range(5):
        f = os.popen('get_instance_by_service -a "%s" 2>/dev/null' % serviceName)
        txt = f.readlines()
        f.close()
        #返回正常结果
        if re_ip.search(str(txt)):
            for line in txt:
                line = line.strip()
                line = line.split()
                result.append(line[:2])
            return result
    return []


if __name__ == '__main__':
    print getInstanceByService('iknow-ac.rp.jx')
    print getInstanceByService('test')
    print getInstanceByService('')
