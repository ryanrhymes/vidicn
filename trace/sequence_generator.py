#!/usr/bin/env python
"""
Given a list of items with their corresponding frequency,
sequence_generator generates a series of events consitent
with the popularity distribution in the given list.

This script is originally used for generating request series
given the popularity distribution.

Liang Wang @ Dept. of Computer Science, Univ. of Helsinki, Finland
2013.04.28
"""

import os
import sys
import random
import operator
import bisect


def sequence_generator(distr, count):
    distr = sorted(distr, key=operator.itemgetter(1))
    intvl = [distr[0][1]]
    seqll = list()
    # construct intervals
    for i in range(1, len(distr)):
        intvl.append(intvl[i-1] + distr[i][1])
    # generate sequence
    for i in range(count):
        tmpi = random.randint(0, intvl[-1]-1)
        idx = bisect.bisect_right(intvl, tmpi)
        seqll.append(distr[idx])
    return seqll

if __name__ == "__main__":
    x = [['a',5],['b',2],['c',3],['d',7],['e',1]]
    seqll = sequence_generator(x, 20)
    print seqll
    sys.exit(0)
