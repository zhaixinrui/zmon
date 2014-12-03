#!/usr/bin/env python2.7
#-*- coding:UTF-8 -*-
# 该文件提供操作redis的接口
import time
from collections import defaultdict

g_origin_time = int(time.mktime(time.gmtime(0)))

def merge(merge_dict, merge_key_names, data_key_names, data_dict):
    merge_key_names = tuple(merge_key_names)
    if merge_key_names in merge_dict:
        return merge_key_names
    data_key_index = {}
    for i, k in enumerate(data_key_names):
        data_key_index[k] = i
    merge_key_index = map(data_key_index.get, merge_key_names)
    merge_data = merge_dict[merge_key_names] = defaultdict(float)
    for keys, value in data_dict.iteritems():
        try:
            merge_data[tuple(map(keys.__getitem__, merge_key_index))] += value
        except:
            pass
    return merge_key_names

def push(db, db_retry_time, zcm_key, key_names, keys, value_name, value, data_time, push_time):
    where = '\x02'.join(map('\x03'.join, zip(key_names, map(str, keys))))
    db_key_prefix = '%s\x01%s\x01%s\x01' % (zcm_key, where, value_name)
    for interval, ca_size in push_time:
        time_key = (data_time - g_origin_time) // interval
        db_key = '%s%d\x02%d' % (db_key_prefix, interval, ca_size)
        db.caincrby(db_key, ca_size, time_key, value)
        print '(db_key: %s, ca_size: %s, time_key: %s, value: %s)' % (db_key, ca_size, time_key, value)
            

