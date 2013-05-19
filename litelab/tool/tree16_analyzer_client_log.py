#!/usr/bin/env python
#
# This script is used to analyse the log files generated by the clients.
# The script is modified based on client_log_analyzer.py, the difference is
# bandwidth saving is also calculated.
#
# Usage: client_log_analyzer_2.py warmup_time topology_file log_files
#
# Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
# 2013.03.25
#

import re
import os
import sys
from multiprocessing import *

sys.path.append('/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/litelab/expconf/tree16/ihandler/')
from vidicn_common import *

D2SERVER = 7.0  # Hops to the server
filePopularity = prepare_file_popularity()
fileSize = prepare_filesize_distrib()
chunkPopularity = prepare_chunk_popularity_weibull()
chunkSize = prepare_chunksize_distrib(fileSize)


def parse_log(ifn):
    rsp = 1
    hit = 0
    hop = 0
    fpa = 0
    fpb = 0
    brsp = 0
    bhit = 0

    pattern = re.compile(r"(\S+?)\t(\S+?)\t(\S+?)\t(\S+?)\t(\S+?)\t(\S+?)\t(\S+?)\t(\S+)\t(\S+)")

    for line in open(ifn,'r'):
        d = parse_line(line, pattern)

        if not d:
            print line
        if d['typ'] == 1:
            rsp += 1
            brsp += chunkSize[d['fil'], d['chk']]
            if d['hit'] == 1:
                hit += 1
                bhit += chunkSize[d['fil'], d['chk']] 
            hop += d['hop']/2.0 - 1
            fpa += chunkSize[d['fil'], d['chk']] * (d['hop']/2.0 - 1)
            fpb += chunkSize[d['fil'], d['chk']] * D2SERVER

    print "%s: byte_hit:%.4f, fpr:%.4f, avg.hops:%.2f" % \
    (ifn, bhit/brsp, (fpb-fpa)/fpb, 1.0*hop/rsp)
    return bhit/brsp, (fpb-fpa)/fpb, 1.0*hop/rsp


def parse_line(line, pattern):
    d = {}
    m = pattern.search(line)
    if m:
        m = m.groups()
        d['ts']  = float(m[0])
        d['seq'] = int(m[1])
        d['src'] = m[2]
        d['dst'] = m[3]
        d['typ'] = int(m[4])
        d['hit'] = int(m[5])
        d['fil'] = int(m[6])
        d['chk'] = int(m[7])
        d['hop'] = int(m[8])
    return d

def parse_all(ifns):
    bhit = 0
    hop = 0
    fpr = 0

    p = Pool(processes=cpu_count())
    it =p.imap(parse_log, ifns)
    while True:
        try:
            bhitt, fprt, hopt = it.next()
            bhit += bhitt
            fpr += fprt
            hop += hopt
        except StopIteration:
            break
    print "-"*50
    print "sys: byte_hit:%.4f, fpr:%.4f, avg.hops:%.2f" % \
    (bhit/len(ifns), fpr/len(ifns), hop/len(ifns))

    pass

if __name__=="__main__":
    #for fname in sys.argv[1:]:
    #    parse_log(fname)

    parse_all(sys.argv[1:])

    sys.exit(0)