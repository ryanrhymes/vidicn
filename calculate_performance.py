#!/usr/bin/env python
"""
Given the content distribution file and request trace, calculate
the hit rate and footprint reduction.

Usage: app.py request_trace cache_trace chunk_trace

Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
2013.01.18
"""

import os
import sys

from numpy import *

# Model constants

M = 5


def load_request(ifn):
    print "load request trace ..."
    request = []
    for line in open(ifn, 'r').readlines():
        f, c = line.split()
        request.append([int(f), int(c)])
    return array(request)

def load_cache(ifn):
    print "load cache trace ..."
    lines = open(ifn, 'r').readlines()
    files, chunks, routers = get_model_parameter(lines)
    cache = zeros((files+1, chunks+1, routers+1))
    for line in lines:
        _, x, y, z = line.split("=")[0].split("_")
        cached = line.split("=")[1].strip()
        cache[int(x)][int(y)][int(z)] = cached
    return cache

def load_chunk(ifn):
    print "load chunk info ..."
    lines = open(ifn, 'r').readlines()
    files, chunks = (0, 0)
    for line in lines:
        x, y, s, t = line.split()
        files = max(files, int(x))
        chunks = max(chunks, int(y))
    chunk = zeros((files + 1, chunks + 1))
    for line in lines:
        x, y, s, t = line.split()
        chunk[int(x)][int(y)] = float(s)
    return chunk

def get_model_parameter(lines):
    files, chunks, routers = (0, 0, 0)
    for line in lines:
        _, x, y, z = line.split("=")[0].split("_")
        files = max(files, int(x))
        chunks = max(chunks, int(y))
        routers = max(routers, int(z))
    return files, chunks, routers

def calculate_performance(request, cache, chunk):
    integral = True if cache.shape[1] == 1 else False
    print "calculating performance ... [%s caching]" % ( "integral" if integral else "partial" )
    HR = 0.0
    byteHR = 0.0
    totalByte = 0.0
    FP = 0.0
    totalFP = 0.0
    for rf, rc in request:
        rct = 0 if integral else rc
        if 1 in cache[rf][rct]:
            HR += 1.0
            byteHR += chunk[rf][rc]
            index = where(cache[rf][rct] == 1)[0][0] + 1
            FP += chunk[rf][rc] * index 
        totalByte += chunk[rf][rc]
    HR /= len(request)
    byteHR /= totalByte
    FPR = (totalByte * (M+1) - FP) / (totalByte * (M+1))
    print HR, byteHR, FPR
    pass


# Main function

if __name__ == "__main__":
    request = load_request(sys.argv[1])
    cache = load_cache(sys.argv[2])
    chunk = load_chunk(sys.argv[3])
    calculate_performance(request, cache, chunk)

    sys.exit(0)
