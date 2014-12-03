#!/home/zxr/zmon/python/bin/python
import json
import web
import re


class TestRegular(object):
    def __init__(self):
        self.input = web.input()
        self.ret = {'code':300, 'msg':''}

    def POST(self):
        try:
            self.log_line = self.input['log_line']
            self.re_expr = self.input['re_expr']
        except:
            self.ret = {'code':400, 'msg':u'获取输入失败'}
            return json.dumps(self.ret)

        if not self.initRegular():
            return json.dumps(self.ret)

        try:
            val = self.getValueByRe(self.re_expr, self.log_line)
            self.ret = {'code':200, 'msg':u'%s' % val}
            return json.dumps(self.ret)
        except Exception,e:
            self.ret = {'code':200, 'msg':u'执行异常[%s]' % e}
            return json.dumps(self.ret)


    def initRegular(self):
        try:
            self.re_expr = re.compile(r'%s' % self.re_expr)
            return True
        except Exception,e:
            self.ret = {'code':400, 'msg':u'正则表达式语法错误[%s]' % e}
            return False

    def getValueByRe(slef, regular, line):
        """用正则从一行日志中过滤出需要的值"""
        ret = None
        result = regular.search(line)
        if result:
            try:
                ret = result.group(1)
            except:
                ret = 1
        else:
            ret = None
        return ret

if __name__ == '__main__':
    pass
