#!/usr/bin/env python

import os
import sys
import random
import bisect
import operator

def zipf(fnum, s):
    flist = []
    rfcap = 10000.0
    for i in range(fnum):
        freq = rfcap / ( (i+1)**s )
        flist.append( (i, freq, random.randint(5, 15)) )
    return flist

def sequence_generator(distr, count):
    distr = sorted(distr, key=operator.itemgetter(1))
    seqll = list()
    # construct intervals
    for i in range(1, len(distr)):
        print intvl[i-1], distr[i][1]
        intvl.append(intvl[i-1] + distr[i][1])
    # generate sequence
    for i in range(count):
        tmpi = random.randint(0, int(intvl[-1]-1))
        idx = bisect.bisect_right(intvl, tmpi)
        seqll.append(distr[idx][0])
    return seqll

def output(flist):
    print "write finfo trace ..."
    fh = open('finfo.trace', 'w')
    for idx, frq, fsz in flist:
        fh.write("%i %i %f\n" % (idx+1, frq, fsz))
    fh.close()
    
    print "write request trace ..."
    seqll = sequence_generator(flist, 10**6)
    fh = open('request.trace', 'w')
    for idx in seqll:
        fh.write("%i %f\n" % (idx+1, flist[idx][2]))
    fh.close()
    pass

if __name__ == "__main__":
    flist = zipf(10**4, 0.9)
    output(flist)
    sys.exit(0)
