#!/home/space/zmon/python/bin/python
#-*- coding: GB2312 -*-
import MySQLdb,sys
import jstemplate
import zmonlib
import logging

class JsGenerate(object):
    def __init__(self, product):
        self.product = product
        self.jsfile = '../webroot/js/zmon.%s.js' % product

    def jsGenerate(self):
        self.getDate()
        self.analyseDate()
        self.generateString()
        self.writeJs()

    def getDate(self):
        if self.product == None:
            sql = "select PRODUCT,NAME,UITREE,UICHART from monitor"
        else:
            sql = "select PRODUCT,NAME,UITREE,UICHART from monitor where PRODUCT = '%s'" % self.product
        self.result = zmonlib.ExecSql(sql)

    def analyseDate(self):
        self.data = {}
        for record in self.result:
            productName = record[0]
            moduleName = record[1]
            uitree = self.getDictFromStr(record[2])
            uichart = self.getDictFromStr(record[3])
            #productName = self.getProductByKey(zcm_key)
            #moduleName = zcm_key.split('/')[-1]
            self.insert2Dict(productName, moduleName, uitree, uichart)
        logging.info("analyseDate return the result: %s" % self.data)
    
    def getDictFromStr(self, uitree):
        treeDict = eval(uitree)
        logging.info("getDictFromStr return the result: %s" % treeDict)
        return treeDict

    def insert2Dict(self, productName, moduleName, uitree, uichart):
        if productName in self.data:
            if moduleName in self.data[productName]:
                self.data[productName][moduleName]['uitree'] = uitree
                self.data[productName][moduleName]['uichart'] = uichart
            else:
                self.data[productName][moduleName] = {}
                self.data[productName][moduleName]['uitree'] = uitree
                self.data[productName][moduleName]['uichart'] = uichart
        else:
            self.data[productName] = {}
            if moduleName in self.data[productName]:
                self.data[productName][moduleName]['uitree'] = uitree
                self.data[productName][moduleName]['uichart'] = uichart
            else:
                self.data[productName][moduleName] = {}
                self.data[productName][moduleName]['uitree'] = uitree
                self.data[productName][moduleName]['uichart'] = uichart
        
    def getProductByKey(self, zcm_key):
        return zcm_key.split('/')[-2]


    def generateString(self):
        self.str = ''
        valueNames = ''
        nodes = ''
        #1======add product node begin
        for product in self.data:
            self.str += '{\n'
            self.str += 'name: \'%s\',\n' % product
            self.str += 'open: true,\n'
            self.str += 'nodes: [\n'
            #2======add module node begin
            modules = self.data[product].keys()
            modules.sort()
            for module in modules:
                self.str += '{\n'
                self.str += 'name: \'%s\',\n' % module
                self.str += 'isKey: true,\n'
                #3=========add module's chart begin
                self.str += 'valueNames: [\n'
                #add flow first
                self.str += '{\n'
                self.str += 'name: \'%s\',\n' % 'flow'
                self.str += 'unit: \'%s\'\n' % 'QPS'
                self.str += '},\n'
                for chart in self.data[product][module]['uichart']:
                    if chart == 'flow':
                        continue
                    if self.data[product][module]['uichart'][chart] == 'sum':
                        self.str += '{\n'
                        self.str += 'name: \'%s\',\n' % chart
                        self.str += 'unit: \'%s\'\n' % 'None'
                        self.str += '},\n'
                    else:
                        self.str += '{\n'
                        self.str += 'name: \'%s\',\n' % chart
                        self.str += 'unit: \'%s\',\n' % 'None'
                        self.str += 'hidden: true\n'
                        self.str += '},\n'
                        self.str += '{\n'
                        self.str += 'name: \'%s_average\',\n' % chart
                        self.str += 'unit: \'%s\',\n' % 'None'
                        self.str += 'divide: true,\n'
                        self.str += 'dividend: \'%s\',\n' % chart
                        self.str += 'divisor: \'flow\'\n'
                        self.str += '},\n'
                self.str += '],\n'
                #3=========add module's chart end

                #3=========add module's tree node begin
                self.str += 'nodes: [\n'
                for node in self.data[product][module]['uitree']:
                    self.str += '{\n'
                    self.str += 'name: \'%s\',\n' % node
                    self.str += 'isListKey: true,\n'
                    self.str += 'isParent: true,\n'
                    self.str += '},\n'
                self.str += ']\n'
                self.str += '},\n'
                #3=========add module's tree node end
            #2======add module node end
            self.str += ']\n'
            self.str += '},\n'
        #1======add product node end

    def getModuleStr(self, moduleName, moduleDict):
        str = ''
            
    def writeJs(self):
        f = open(self.jsfile, 'w')
        f.write(jstemplate.head)
        f.write(self.str)
        f.write(jstemplate.foot)
        f.close()

if __name__ == '__main__':
    jg = JsGenerate('space')
    jg.getDate()
    jg.analyseDate()
    jg.generateString()
    jg.writeJs()
    
