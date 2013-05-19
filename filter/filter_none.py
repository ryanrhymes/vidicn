#!/usr/bin/env python

import os
import sys
import time

sys.path.append("/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/litelab/router/CacheStrategy")
from vidicn_cache_lru import vidicn_cache_lru as CacheModel

CSIZE = 2**10    # Cache size in MB

def test_filter(cache, reqs):
    miss = [ x for x, _ in reqs ]
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

    fh = open('miss_none.trace', 'w')
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
