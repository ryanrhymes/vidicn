#!/usr/bin/env python
"""
Given the content distribution file and request trace, calculate
the hit rate and footprint reduction.

Usage: app.py cache_trace_1 cache_trace_2 chunk_trace

Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
2013.01.24
"""

import os
import sys

from numpy import *
from calculate_performance import *


def similarity_cache(n1, n2):
    s1 = convert2set_cs(n1)
    s2 = convert2set_cs(n2)
    r = 0.0
    for k in s1.keys():
        ts1 = s1[k]
        ts2 = s2[k]
        r += 1.0 * len(ts1 & ts2) / len(ts1 | ts2)
    r /= len(s1.keys())
    return r

def similarity_cache_pw(n1, n2, info):
    r = 0.0
    s1 = convert2set_cs(n1)
    s2 = convert2set_cs(n2)
    for k in s1.keys():
        ts1 = s1[k]
        ts2 = s2[k]
        tw = 0.0
        cw = 0.0
        for x, y in (ts1 | ts2):
            tw += info[x,y]
        for x, y in (ts1 & ts2):
            cw += info[x,y]
        r += cw / tw
    r /= len(s1.keys())
    return r

def similarity_network(n1, n2):
    s1 = convert2set_nt(n1)
    s2 = convert2set_nt(n2)
    r = 1.0 * len(s1 & s2) / len(s1 | s2)
    return r

def similarity_network_pw(n1, n2, info):
    s1 = convert2set_nt(n1)
    s2 = convert2set_nt(n2)
    tw = 0.0
    cw = 0.0
    for x, y in (s1 | s2):
        tw += info[x,y]
    for x, y in (s1 & s2):
        cw += info[x,y]
    return cw / tw

def entropy_network(n1, n2, info):
    s1 = convert2set_nt(n1)
    s2 = convert2set_nt(n2)
    e1 = 0.0
    e2 = 0.0
    nm = info.max()
    for x, y in s1:
        e1 -= log2(info[x,y])
    for x, y in s2:
        e2 -= log2(info[x,y])
    r = min(e1, e2) / max(e1, e2)
    print e1, e2
    return r

def convert2set_nt(cache):
    s = set()
    x, y, z = cache.shape
    for i in range(x):
        for j in range(y):
            for k in range(z):
                if cache[i, j, k] == 1:
                    s.add( (i,j) )
    return s

def convert2set_cs(cache):
    r = dict()
    x, y, z = cache.shape
    for k in range(z):
        s = set()
        for i in range(x):
            for j in range(y):
                if cache[i, j, k] == 1:
                    s.add( (i,j) )
        r[k] = s
    return r


# Main function

if __name__ == "__main__":
    caches1 = load_cache(sys.argv[1])
    caches2 = load_cache(sys.argv[2])
    cinfo = load_chunk(sys.argv[3])

    cs = similarity_cache(caches1, caches2)
    cw = similarity_cache_pw(caches1, caches2, cinfo)
    ns = similarity_network(caches1, caches2)
    nw = similarity_network_pw(caches1, caches2, cinfo)
    en = entropy_network(caches1, caches2, cinfo)
    print cs, cw, ns, nw, en

    sys.exit(0)
