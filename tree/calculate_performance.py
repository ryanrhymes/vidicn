#!/usr/bin/env python
"""
Given the content distribution file and request trace, calculate
the hit rate and footprint reduction.

Usage: app.py request_trace cache_trace chunk_trace

Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
2013.02.21
"""

import os
import sys
import math
import networkx as nx

from numpy import *

TDEG = None  # Tree dgree
TLVL = None  # Tree level

def build_k_tree(deg=2, lvl=3):
    edgelist = [(0,1)]
    for i in range(1, (deg**lvl-1)/(deg-1) + 1):
        pn = int(math.ceil((i-1.0)/deg))
        edgelist.append((pn, i))
    G = nx.Graph(edgelist)
    return G

def construct_topology():
    edgelist = [(0,1), (1,2), (1,3), (2,4), (2,5), (3,6), (3,7),\
                    (4,8), (4,9), (5,10), (5,11), (6,12), (6,13), (7,14), (7,15)]
    G = nx.Graph(edgelist)
    return G

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
    cache = zeros((files+1, chunks+1, routers+1, routers+1))
    for line in lines:
        x, y, u, v, c = line.strip().split()
        cache[int(x), int(y), int(u), int(v)] = c
    return cache

def load_chunk(ifn):
    print "load chunk info ..."
    lines = open(ifn, 'r').readlines()
    files, chunks = (0, 0)
    for line in lines:
        x, y, s, t = line.strip().split()
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
        x, y, z, _, _ = line.strip().split()
        files = max(files, int(x))
        chunks = max(chunks, int(y))
        routers = max(routers, int(z))
    return files, chunks, routers

def calculate_performance(G, node, request, cache, chunk):
    integral = True if cache.shape[1] == 1 else False
    print "calculating performance ... [%s caching]" % ( "integral" if integral else "partial" )
    HR = 0.0
    byteHR = 0.0
    totalByte = 0.0
    FP = 0.0
    totalFP = 0.0
    M = len(nx.shortest_path(G, node, 0))
    for rf, rc in request:
        rct = 0 if integral else rc
        if 1 in cache[rf][rct][node][1:]:
            HR += 1.0
            byteHR += chunk[rf][rc]
            tpath = float('inf')
            for x in cache[rf][rct][node][1:]:
                y = len(nx.shortest_path(G, node, x))
                if tpath > y:
                    tpath = y
            FP += chunk[rf][rc] * tpath
        else:
            FP += chunk[rf][rc] * M
        totalByte += chunk[rf][rc]
    HR /= len(request)
    byteHR /= totalByte
    FPR = (totalByte * M - FP) / (totalByte * M)
    return HR, byteHR, FPR

def calculate_document_download_effort(cache):
    dEffort = 0.0
    N, P, M = cache.shape
    for i in range(N):
        tde = 0.0
        for j in range(P):
            tarr = where(cache[i][j] == 1)[0]
            index = M + 1 if len(tarr) == 0 else tarr[0]
            tde += index
        dEffort += tde / ((M + 1) * P)
    dEffort /= N
    return dEffort

def calculate_average_performance(G, request, cache, chunk):
    M = len(G)
    L = range(int(math.ceil((M-1.0)/TDEG)), M)
    HR, byteHR, FPR = 0.0, 0.0, 0.0
    for n in L:
        tHR, tbyteHR, tFPR = calculate_performance(G, n, request, cache, chunk)
        HR += tHR
        byteHR += tbyteHR
        FPR += tFPR
    HR /= len(L)
    byteHR /= len(L)
    FPR /= len(L)
    return HR, byteHR, FPR

# Main function

if __name__ == "__main__":
    TDEG, TLVL = int(sys.argv[4]), int(sys.argv[5])
    G = build_k_tree(TDEG, TLVL)
    request = load_request(sys.argv[1])
    cache = load_cache(sys.argv[2])
    chunk = load_chunk(sys.argv[3])
    HR, byteHR, FPR = calculate_average_performance(G, request, cache, chunk)
    print HR, byteHR, FPR

    sys.exit(0)
