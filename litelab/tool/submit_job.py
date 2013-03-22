#!/usr/bin/env python
# 
# This script stops all the node_agent on Ukko cluster
#
# Liang Wang @ Dept. Computer Science, University of Helsinki, Finland
# 2012.02.27 created.
#

import os
import sys
import time
import pickle
import random

from broadcast import *

def submit_job(cdir):
    msg = pickle.dumps({'op':'job_', 'args':cdir, 'tid':random.randint(0, 65535)})
    broadcast(msg)
    print "broadcast:", cdir
    pass

if __name__=="__main__":
    cdir = sys.argv[1]
    submit_job(cdir)
    sys.exit()
