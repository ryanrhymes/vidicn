#!/usr/bin/env python

import os
import sys

from sequence_generator import sequence_generator

COUNT = 100000    # sequence length

def generate_request(ifn):
    distr = list()
    finfo = list()

    print "parsing log ..."
    for line in open(ifn, 'r'):
        flds = line.strip().split()
        oname, osize, ofrq = flds[0], float(flds[1]), float(flds[2])
        distr.append([oname, ofrq])
        finfo.append([oname, osize, ofrq])

    print "generating sequece ..."
    seqll = sequence_generator(distr, COUNT)

    print "writing to file ..."
    ofn = open('youtube.request.trace', 'w')
    for obj in seqll:
        idx = int(obj[0])
        ofn.write("%s %f %i\n" % (finfo[idx][0], finfo[idx][1], finfo[idx][2]))
    pass


if __name__ == "__main__":
    generate_request(sys.argv[1])
    sys.exit(0)
