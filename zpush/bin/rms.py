#!/usr/bin/env python
import rms

def rms_extra_keys(key_names_index, key):
    try:
        return (rms.rms_product(key[key_names_index['reqip']]), )
    except:
        return 'None'
