#!/usr/bin/env python
# 
# This script is python version of the client in INCA experiment.
# It submits requests to the given server with certain pattern.
#
# usage: client.py
#
# Liang Wang @ Dept. Computer Science, University of Helsinki, Finland
# 2012.02.27 created.
#

import os
import sys
import time
import random as pyrnd
import struct
import threading

sys.path.append('/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/litelab/router/')
from common import *
from messageheader import *
from vidicn_common import *

TALIGNMENT = 10 # alignement for startup time.
filePopularity = prepare_file_popularity()
fileSize = prepare_filesize_distrib()
chunkPopularity = prepare_chunk_popularity_weibull()
chunkSize = prepare_chunksize_distrib(fileSize)



class Client(object):
    def __init__(self, vrid, router, args, logfh=None):
        self.vrid     = vrid              # the vrid of the router this client running on
        self.logfh    = logfh
        self.router   = router
        self.args     = args

        self.seq  = pyrnd.randint(0,9999999)
        metafile= args['app_args'].split()[0]
        self.reqs = load_request(metafile)
        self.servers = get_server_list(args['app_args'])

        pass

    def __del__(self):
        pass

    def start_request(self):
        for i in range(self.reqs.shape[0]):
            try:
                self.seq += 1
                server = pyrnd.sample(self.servers, 1)[0]
                self.request(self.seq, self.reqs[i], server)
                hdr = self.router.recv()
                print i, "=====>", hdr.src, hdr.dst, hdr.hop, hdr.fil, hdr.chk
                logme3(self.logfh, hdr.seq, hdr.src, hdr.dst, hdr.type, hdr.hit, hdr.fil, hdr.chk, hdr.hop)
            except Exception, err:
                print "Exception:Client.start_request():", err

        # Task done, wait for the receiving thread
        while True:
            time.sleep(1)
        print "Client: quit..."
        pass

    def request(self, seq, cid, server):
        """Request a single chunk"""
        hdr = MessageHeader()
        hdr.type = MessageType.REQUEST
        hdr.fil = cid[0]
        hdr.chk = cid[1]
        hdr.siz = chunkSize[cid[0],cid[1]]
        hdr.seq = seq
        hdr.src = self.vrid
        hdr.dst = server
        hdr.hit = 0
        hdr.hop = 1
        self.router.send(hdr)
        pass

    def start(self):
        """Start the client, both request and receive threads"""

        t0 = threading.Thread(target=self.start_request)
        t0.daemon = True
        t0.start()

        while True:
            time.sleep(1)
        pass

    pass


def main(router, args):
    print "+" * 100
    vrid   = args['vrid']
    logdir = args['logdir']
    logfh  = open("%s/client-%i" % (logdir, vrid), 'w')
    client = Client(vrid, router, args, logfh)

    time.sleep((int(time.time()) / TALIGNMENT) * TALIGNMENT + 2 * TALIGNMENT - time.time())
    client.start()
    pass


if __name__=="__main__":
    sys.exit(0)
