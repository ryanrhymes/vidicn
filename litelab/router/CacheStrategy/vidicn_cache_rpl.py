#!/usr/bin/env python
# 
# This script implements the abstraction of cache object in a router. The
# relevant operations on cache can be implemented in this class.
#
# Liang Wang @ Dept. Computer Science, University of Helsinki, Finland
# 2011.05.31 created, 2011.06.12 modified.
#

import os
import sys
import time
import binascii
import numpy as np
from ctypes import *
#from common import *


class vidicn_cache_rpl(object):
    def __init__(self, quota):
        self.dtype = np.dtype([('fkey', np.int32), ('ckey', np.int32), ('utility', np.float64), \
                                   ('size', np.float64), ('timestamp', np.float64)])
        self.cache = np.array([], dtype=self.dtype)
        self.usedc = 0.0
        self.quota = quota
        self.pathcache ={}
        self.logfh = None
        pass

    @property
    def keys(self):
        return self.llist

    def add_chunk(self, key, utility, size):
        evict = []
        fkey, ckey = key
        ts = time.time()
        hit = np.where((self.cache['fkey']==fkey) & (self.cache['ckey']==ckey))[0]
        if len(hit):
            hit = hit[0]
            self.cache[hit]['utility'] = utility
            self.cache[hit]['timestamp'] = ts
        else:
            if self.usedc + size > self.quota:
                t_usedc = self.usedc
                t_utility = 0.0
                t_evict = []
                t_index = 0
                while True:
                    if (t_usedc + size <= self.quota) or (t_utility > utility):
                        break
                    ec = self.cache[t_index]
                    t_usedc -= ec['size']
                    t_utility += ec['utility']
                    t_evict.append(t_index)
                    t_index += 1
                if (t_usedc + size <= self.quota) and (t_utility <= utility):
                    self.usedc = t_usedc + size
                    for eci in t_evict:
                        evict.append(self.cache[eci])
                    self.cache = np.delete(self.cache, t_evict, axis=0)
                    self.cache = np.append(self.cache, np.array([(fkey, ckey, utility, size, ts)], dtype=self.dtype), axis=0)
            else:
                self.usedc += size
                self.cache = np.append(self.cache, np.array([(fkey, ckey, utility, size, ts)], dtype=self.dtype), axis=0)

        self.cache = np.sort(self.cache, order=['utility', 'timestamp'])
        return evict

    def get_chunk(self, key, utility):
        chunk = None
        fkey, ckey = key
        ts = time.time()
        hit = np.where((self.cache['fkey']==fkey) & (self.cache['ckey']==ckey))[0]
        if len(hit):
            hit = hit[0]
            chunk = self.cache[hit]
            self.cache[hit]['utility'] = utility
            self.cache[hit]['timestamp'] = ts
        self.cache = np.sort(self.cache, order=['utility', 'timestamp'])
        return chunk

    def del_chunk(self, key):
        pass

    def add_pathcache(self, key, src, dst):
        self.pathcache[key] = (src,dst)
        pass

    def del_pathcache(self, key):
        src, dst = self.pathcache.pop(key)
        return src,dst

    def current_size(self):
        return len(self.cache)

    def is_full(self):
        return self.usedc >= self.quota

    def is_hit(self, key):
        fkey, ckey = key
        hit = np.where((self.cache['fkey']==fkey) & (self.cache['ckey']==ckey))[0]
        hit = True if len(hit) else False
        return hit

    def get_val_by_key(self, key):
        """Remark: Pay attention to the differences between this function and
        get_chunk(...) function."""
        val = self.cache.get(key, None)
        return val

    pass


def test_fn():
    import random
    random.seed(123)
    cache = vidicn_cache_rpl(50)
    for i in range(100):
        evict = cache.add_chunk((random.randint(0,5), random.randint(0,50)), random.random(), 10*random.random())
        if len(evict):
            print "evict --->", evict
        #time.sleep(0.1)

    #print cache.cache
    print "-"*30
    #print np.sort(cache.cache, order=['size'])
    print "-"*30
    #print np.where((cache.cache['fkey']==0) & (cache.cache['ckey']==3))[0]
    pass

if __name__ == "__main__":
    print sys.argv[0]
    test_fn()

    sys.exit(0)
