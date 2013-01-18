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
    reqFile = random.weibull(0.513, R)
    reqChunk = random.weibull(1.0, R)
    return reqFile, reqChunk

def output_request(reqFile, reqChunk):
    norma = N / max(reqFile)
    normb = P / max(reqChunk)
    for i in range(R):
        print (int) (reqFile[i] * norma), (int) (reqChunk[i] * normb)
    pass

# Main function

if __name__ == "__main__":
    random.seed(SEED)
    rf, rc = request_weibull()
    output_request(rf, rc)

    sys.exit(0)
