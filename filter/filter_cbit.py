#!/usr/bin/env python

import os
import sys
import time
import random

sys.path.append("/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/litelab/router/CacheStrategy")
from vidicn_cache_lru import vidicn_cache_lru as CacheModel

CSIZE = 2**10    # Cache size in MB
PLEN = 2         # Path lenghth 

def test_filter(cache, reqs):
    miss = []
    cache2 = CacheModel(CSIZE*(PLEN-1))
    rounds = 0
    t0 = time.time()
    for r, s in reqs:
        r = (r,0)
        if not cache.is_hit(r) and cache.is_full() and cache2.is_full():
            miss.append(r[0])
        if not cache2.is_hit(r) and random.random() < 1.0/PLEN:
            cache.add_chunk(r, s)
        else:
            cache2.add_chunk(r, s)
        # Print out info
        rounds += 1
        if rounds % 10**4 == 0:
            print "requess processed --->", rounds, \
                "\t%.1f pkts/s" % (10**4/(time.time()-t0))
            t0 = time.time()
    return miss

def load_request(ifn):
    request = []
    for line in open(ifn, 'r').readlines():
        r, s = line.split()
        request.append([int(r), int(float(s))])
    return request

def output_miss(miss):
    d = dict()
    for r in miss:
        d[r] = d.get(r, 0) + 1

    fh = open('miss_cbit.trace', 'w')
    freqs = sorted(d.values(), reverse=True)
    for i in range(len(freqs)):
        fh.write("%i %i\n" % (i+1, freqs[i]))
    fh.close()
    pass

if __name__ == "__main__":
    cache = CacheModel(CSIZE)
    reqs = load_request(sys.argv[1])
    miss = test_filter(cache, reqs[:])
    output_miss(miss)

    sys.exit(0)
