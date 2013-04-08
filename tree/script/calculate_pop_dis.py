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
import networkx as nx

from numpy import *


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
    chunk = zeros((files + 1, chunks + 1, 2))
    for line in lines:
        x, y, s, t = line.split()
        chunk[int(x),int(y),0] = float(s)
        chunk[int(x),int(y),1] = float(t)
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
    N, P, M, _ = cache.shape
    integral = True if P == 1 else False
    print "calculating performance ... [%s caching]" % ( "integral" if integral else "partial" )
    HR = 0.0
    byteHR = 0.0
    totalByte = 0.0
    FP = 0.0
    totalFP = 0.0
    for rf, rc in request:
        rct = 0 if integral else rc
        tpath = nx.diameter(G) + 2
        if 1 in cache[rf][rct][node][1:]:
            HR += 1.0
            byteHR += chunk[rf][rc]
            for x in where(cache[rf,rct,node]==1)[0]:
                y = len(nx.shortest_path(G, node, x))
                if tpath > y:
                    tpath = y
        FP += chunk[rf][rc] * tpath
        totalByte += chunk[rf][rc]
    HR /= len(request)
    byteHR /= totalByte
    FPR = (totalByte * M - FP) / (totalByte * M)
    dDE = calculate_document_download_effort(G, node, cache)
    #print node, "---->", HR, byteHR, FPR, dDE
    return HR, byteHR, FPR, dDE

def calculate_document_download_effort(G, node, cache):
    N, P, M, _ = cache.shape
    dEffort = 0.0
    N, P, M, _ = cache.shape
    for i in range(N):
        tde = 0.0
        for j in range(P):
            tpath = nx.diameter(G) + 2
            for x in where(cache[i,j,node]==1)[0]:
                y = len(nx.shortest_path(G, node, x))
                if tpath > y:
                    tpath = y
            tde += tpath
        dEffort += tde
    dEffort /= N * P * (nx.diameter(G) + 2)
    return dEffort

def calculate_popularity_distance(G, cache, chunk):
    N, P, M, _ = cache.shape
    router = zeros((M,2))
    for i in range(N):
        for j in range(P):
            for k in range(M):
                if cache[i,j,k,k] == 1:
                    router[k,0] += chunk[i,j,0]
                    router[k,1] += chunk[i,j,1] * chunk[i,j,0]
    for i in range(M):
        print i, router[i, 0], router[i, 1] / router[i, 0]
    pass

def calculate_popularity_per_bit(cache):
    pass

# Main function

if __name__ == "__main__":
    G = construct_topology()
    request = load_request(sys.argv[1])
    cache = load_cache(sys.argv[2])
    chunk = load_chunk(sys.argv[3])

    calculate_popularity_distance(G, cache, chunk)

    sys.exit(0)
