#!/usr/bin/env python
"""
Given the content distribution file and request trace, calculate
the hit rate and footprint reduction.

Usage: app.py request_trace cache_trace

Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
2013.01.18
"""

import os
import sys

from numpy import *


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

def load_cache_partial(lines):
    print "load partial caching trace ..."
    pass

def load_cache_integral(lines):
    print "load integral caching trace ..."
    routers, files, chunks = get_model_parameter(lines)
    pass

def get_model_parameter(lines):
    files, chunks, routers = (0, 0, 0)
    for line in lines:
        _, x, y, z = line.split("=")[0].split("_")
        files = max(files, int(x))
        chunks = max(chunks, int(y))
        routers = max(routers, int(z))
    return files, chunks, routers

def calculate_performance(request, cache, integral=True):
    byteHR = 0
    for rf, rc in request:
        rc = 0 if integral else rc
        print rf, rc
        if 1 in cache[rf][rc]:
            byteHR += 1.0
    byteHR /= len(request)
    print byteHR
    pass


# Main function

if __name__ == "__main__":
    request = load_request(sys.argv[1])
    cache = load_cache(sys.argv[2])
    calculate_performance(request, cache)

    sys.exit(0)
