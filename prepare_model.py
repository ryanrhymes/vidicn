#!/usr/bin/env python
"""
Prepare model parameters

2013.01.18
"""

import os
import sys

from numpy import *

# Model constants

SEED = 123  # Random seed for the simulation
M = 5       # Number of routers
N = 100     # Number of files
P = 100     # Number of chunks in a file
K = 1       # Number of copies on the path
C = 100     # Cache size


# Help functions: Prepare model parameters before solving the LIP problem

def prepare_file_popularity():
    k = 0.513
    filePopularity = array([ k * x**(k - 1) * exp(-x**k) for x in range(50, N+50) ]) * 100
    return filePopularity

def prepare_filesize_distrib():
    random.seed(SEED + 5)
    fileSize = random.uniform(size=N) * 10 + 20
    return fileSize

def prepare_chunk_popularity_partial():
    random.seed(SEED + 7)
    chunkPopularity = array([sort(random.weibull(1.0, P))[::-1] for x in range(N)]) * 100
    return chunkPopularity

def prepare_chunk_popularity_integral():
    chunkPopularity = ones([N, P])
    return chunkPopularity

def prepare_chunksize_distrib(fileSize):
    chunkSize = array([ [x / P] * P for x in fileSize ])
    return chunkSize

def prepare_cachesize():
    cache = zeros((M), dtype = float64) + C
    return cache

def prepare_content_distrib_var():
    Y = zeros((N, P, M), dtype = int64)
    return Y

def prepare_model(ifn):
    filePopularity = prepare_file_popularity()
    fileSize = prepare_filesize_distrib()
    chunkPopularity = prepare_chunk_popularity_partial()
    chunkSize = prepare_chunksize_distrib(fileSize)
    cache = prepare_cachesize()
    
    f = open(ifn + ".file", "w")
    for i in range(N):
        f.write("%i %f %f \n" % (i, fileSize[i], filePopularity[i]))

    f = open(ifn + ".chunk", "w")
    for i in range(N):
        for j in range(P):
            f.write("%i %i %f %.20f \n" % (i, j, chunkSize[i][j], chunkPopularity[i][j]))

    pass

# Main function

if __name__ == "__main__":
    prepare_model("model.static")

    sys.exit(0)
