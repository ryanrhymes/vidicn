#!/usr/bin/env python
# 
# This script calculates the pathdict from a topology file.
# The pathdict is then dumped into a file.

# Usage:  dump_pathdict.py topology_file
#
# Liang Wang @ Dept. Computer Science, University of Helsinki, Finland
# 2012.03.22 created.
#

import os
import sys
import time
import pickle
sys.path.append('/fs/home/lxwang/cone/lxwang/litelab/router')

from prouter import Router


if __name__=='__main__':
    args = {}
    args['vrid'] = 0
    args['ip'] = "127.0.0.1"
    args['iport'] = 1980
    args['l2p'] = None
    args['logfh'] = None
    args['ibandwidth'] = 0
    args['ebandwidth'] = 0
    args['queuesize'] = 0
    args['queuepolicy'] = 0

    vr = Router(args)
    vr.read_topology_from_file(sys.argv[1])
    t0 = time.time()
    vr.build_pathdict()
    print "time overheads: %.2fs" % (time.time() - t0)

    print "dumping pathdict ..."
    f = open('pathdict.dump', 'w')
    pickle.Pickler(f).dump(vr.pathdict)
    f.close()

    sys.exit(0)
