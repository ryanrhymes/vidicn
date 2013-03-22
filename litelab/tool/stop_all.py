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

def stop_all(c):
    msg = pickle.dumps({'op':'exit', 'args':'', 'tid':random.randint(0, 65535)})

    for i in range(c):
        print "broadcast:", i
        broadcast(msg)
        time.sleep(0.5)
    pass

if __name__=="__main__":
    c = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    stop_all(c)
    sys.exit()
