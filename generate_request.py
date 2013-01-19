#!/usr/bin/env python
"""
Generate request sequence

2013.01.18
"""

import os
import sys

from numpy import *

# Model constants

SEED = 555  # Random seed for the simulation
N = 100     # Number of files
P = 100     # Number of chunks in a file
R = 100000  # Number of requests


def request_weibull():
    """Generate weibull request pattern"""
    reqFile = sort(random.weibull(0.513, 10*R))[ : R]
    random.shuffle(reqFile)
    reqChunk = sort(random.weibull(0.8, 10*R))[0 : R]
    random.shuffle(reqChunk)
    return reqFile, reqChunk

def output_request(reqFile, reqChunk):
    norma = (N - 1) / max(reqFile)
    normb = (P - 1) / max(reqChunk)
    for i in range(R):
        print (int) (reqFile[i] * norma), (int) (reqChunk[i] * normb)
    pass

# Main function

if __name__ == "__main__":
    random.seed(SEED)
    rf, rc = request_weibull()
    output_request(rf, rc)

    sys.exit(0)
