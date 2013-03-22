#!/usr/bin/env python
# 
# This script implements broadcast function on Ukko cluster
#
# Liang Wang @ Dept. Computer Science, University of Helsinki, Finland
# 2012.02.27 created.
#

import os
import sys
import socket

BADDR = '<broadcast>'
BPORT = 2011

def broadcast(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(msg, (BADDR, BPORT))
    pass

if __name__=="__main__":
    broadcast('hello')
    sys.exit()
