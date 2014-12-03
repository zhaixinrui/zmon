#!/home/zxr/zmon/python/bin/python
import re
import json
import web
import logging
import zmonlib
import auth
class Search(object):
    def __init__(self, input):
        self.input = input
        zmonlib.Init()

    def search(self):
        if self.input['from'] == 'monitorlist':
            return self.searchMonitor()
        elif self.input['from'] == 'hostlist':
            return self.searchHost()
        elif self.input['from'] == 'regularlist':
            return self.searchRegular()
        elif self.input['from'] == 'product':
            return self.searchProduct()

    def searchProduct(self):
        products = zmonlib.getProducts()
        response = {'code':200,'txt':products}
        return json.dumps(response)

    def searchHost(self):
        if not 'monitorid' in self.input:
            return
        limit      = int(self.input.get('rows'))
        page     = int(self.input.get('page'))
        if limit and page:
            start = limit * page - limit # do not put $limit*($page - 1)
        sql = 'select COUNT(*) as count from host h,host_monitor hm where h.HOST_ID = hm.HOST_ID and hm.MONITOR_ID = "%s"' % self.input['monitorid']
        count = zmonlib.ExecSql(sql)
        count = count[0][0]
        total_pages = int((count+limit-1)/limit)
        sql = 'select h.HOST_ID,h.NAME,h.IP from host h,host_monitor hm where h.HOST_ID = hm.HOST_ID and hm.MONITOR_ID = "%s" limit %d,%d' % (self.input['monitorid'], start, limit)
        result = zmonlib.ExecSql(sql)
        return self.changejson(result, page, total_pages, count)

    def searchMonitor(self):
        userName = auth.uuap_sso()
        products = auth.getProcByName(userName)
        if len(products) == 1:
            products.add('')
        products = tuple(products)
        mask = self.input.get('mask','')
        limit      = int(self.input.get('rows'))
        page     = int(self.input.get('page'))
        if limit and page:
            start = limit * page - limit # do not put $limit*($page - 1)
        sql = "select COUNT(*) as count from monitor where PRODUCT in %s and (LOGPATH LIKE '%%%s%%' or NAME like '%%%s%%' or PRODUCT like '%%%s%%')" % (str(products), mask, mask, mask)
        count = zmonlib.ExecSql(sql)
        count = count[0][0]
        total_pages = int((count+limit-1)/limit)
        sql = "select MONITOR_ID,NAME,PRODUCT,LOGPATH,GREP,GREPV,REGULAR_ID_LIST from monitor where PRODUCT in %s and (LOGPATH LIKE '%%%s%%' or NAME like '%%%s%%' or PRODUCT like '%%%s%%') limit %d,%d" % (str(products), mask, mask, mask, start, limit)
        rows = []
        result = zmonlib.ExecSql(sql)
        for rec in result:
            row = [rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], self.getHostNum(rec[0]), len(eval(rec[6]))]
            rows.append(row)
        #result = filter(self.filterByRe, rows)
        logging.debug(rows)
        return self.changejson(rows, page, total_pages, count)

    def filterByRe(self, rec):
        mask = self.input.get('mask',None)
        if None == mask:
            return True
        re_mask = re.compile(r'%s' % mask)
        for i in rec:
            if re_mask.search(str(i)):
                return True
        return False

    def searchRegular(self):
        if not 'monitorid' in self.input:
            return
        sql = 'select REGULAR_ID_LIST from monitor where MONITOR_ID = "%s"' % self.input['monitorid']
        result = zmonlib.ExecSql(sql)
        regularIdList = eval(result[0][0])
        results = []
        for regularId in regularIdList:
            sql = 'select REGULAR_ID,NAME,EXPRESSION from regular where REGULAR_ID = "%s"' % regularId
            result = zmonlib.ExecSql(sql)
            results.extend(result)
        return self.change2json(results)

    def getRegularNum(self, monitorId):
        sql = 'select REGULAR_ID_LIST from monitor where MONITOR_ID = "%s"' % monitorId
        result = zmonlib.ExecSql(sql)
        regularIdList = eval(result[0][0])
        return len(regularIdList)

    def change2json(self,record):
        responce = {}
        responce['page'] = 1
        responce['total'] = 1
        responce['records'] = len(record)
        responce['rows'] = []
        for rec in record:
            row = {'id':rec[0],'cell':rec}
            responce['rows'].append(row)
        logging.debug(responce)
        return json.dumps(responce)   

    def changejson(self, record, page, total_pages, count):
        responce = {}
        responce['page'] = page
        responce['total'] = total_pages
        responce['records'] = count
        responce['rows'] = []
        for rec in record:
            row = {'id':rec[0],'cell':rec}
            responce['rows'].append(row)
        logging.debug(responce)
        return json.dumps(responce) 

    def getHostNum(self, monitorId):
        sql = 'select COUNT(*) AS count from host h,host_monitor hm where h.HOST_ID = hm.HOST_ID and hm.MONITOR_ID = "%s"' % monitorId
        result = zmonlib.ExecSql(sql)
        try:
            return result[0][0]
        except:
            return 0

if __name__ == '__main__':
   pass 
