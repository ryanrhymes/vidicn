#!/usr/bin/env python

import os
import sys

from numpy import *

SEED = 123   # Random seed for the simulation
N = 100      # Number of files
P = 4        # Number of chunks in a file


def load_request(ifn):
    request = []
    for line in open(ifn, 'r').readlines():
        f, c = line.split()
        request.append([int(f), int(c)])
    return array(request)

def weibull(k, lmd, x):
    k, lmd, x = (1.0 * k, 1.0 * lmd, 1.0 * x)
    y = (k/lmd) * (x/lmd)**(k - 1) * exp(-(x/lmd)**k)
    return y

def prepare_file_popularity():
    k = 0.513; lmd = 40.0
    filePopularity = array([ weibull(k, lmd, x) for x in range(10, N+10) ]) * 100
    return filePopularity

def prepare_filesize_distrib():
    random.seed(SEED + 5)
    fileSize = random.uniform(size=N) * 10 + 20
    return fileSize

def prepare_chunk_popularity_integral():
    chunkPopularity = ones([N, P])
    return chunkPopularity

def prepare_chunk_popularity_weibull():
    k = 0.5; lmd = 1.0;
    chunkPopularity = array([ [ weibull(k, lmd, 0.1+1.0*x/(P-1)) for x in range(P) ] for y in range(N)]) * 100
    return chunkPopularity

def prepare_chunk_popularity_linear():
    random.seed(SEED + 7)
    chunkPopularity = array([sort(x)[::-1] for x in random.uniform(size=(N, P))]) * 100
    return chunkPopularity

def prepare_chunksize_distrib(fileSize):
    chunkSize = array([ [x / P] * P for x in fileSize ])
    return chunkSize


if __name__=="__main__":
    sys.exit(0)
