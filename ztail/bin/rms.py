#!/usr/bin/env python
import os,sys

curDir = os.getcwd()
product_fn = '%s/data/rms' % curDir
product_cache = {}
product_stat = None
def rms_product(search_ip):
    global product_cache, product_stat
    try:
        stat_result = os.stat(product_fn)
    except:
        product_cache = {}
        product_stat = None
        return 'None'
    some_stat_result = (stat_result.st_dev, stat_result.st_ino, stat_result.st_size, stat_result.st_mtime)
    if product_stat == some_stat_result:
        return product_cache.get(search_ip, 'None')
    try:
        for line in open(product_fn):
            line = line.rstrip('\n')
            if len(line.split('\t'))==4:
                host, ip, dep, prod = line.split('\t')
                product_cache[ip] = '%s_%s' % (dep, prod)
    except:
        print sys.exc_info()
        product_cache.clear()
        product_stat = None
        return 'None'
    product_stat = some_stat_result
    return product_cache.get(search_ip, 'None')
