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

def kill_job(jobid):
    msg = pickle.dumps({'op':'jobk', 'args':'', 'jobid':jobid, 'tid':random.randint(0, 65535)})
    print "Kill job:", jobid
    broadcast(msg)
    pass

if __name__=="__main__":
    for jobid in sys.argv[1:]:
        jobid = int(jobid)
        kill_job(jobid)
        time.sleep(1)
    sys.exit(0)
