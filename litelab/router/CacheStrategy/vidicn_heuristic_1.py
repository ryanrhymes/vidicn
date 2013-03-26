#!/usr/bin/env python
# 
# This script implements the CachedBit caching strategy.
#
# Liang Wang @ Dept. Computer Science, University of Helsinki, Finland
# 2013.03.25
#

import os
import sys
import time
import binascii
from ctypes import *
from router.common import *
from messageheader import *
import random

class vidicn_heuristic_0(object):
    def __init__(self, router, cachesize):
        self.router = router  # Cache's corresponding router
        self.cache = None
        self.logfh = None
        self.freq = dict()
        pass

    def ihandler(self, hdr, router):
        hdr.hop += 1
        fil = hdr.fil
        chk = hdr.chk
        cid = (fil, chk)
        siz = hdr.siz
        src = hdr.src
        dst = hdr.dst

        if hdr.type == MessageType.REQUEST:
            self.freq[fil] = self.freq.get(fil, 0.0) + 1
            self.freq[(fil,chk)] = self.freq.get((fil,chk), 0.0) + 1

            if self.cache.is_hit(cid):
                logme3(self.logfh, hdr.seq, src, dst, "REQ", 1, fil, chk, hdr.hop)
                hdr.type = MessageType.RESPONSE
                hdr.swap_src_dst()
                hdr.hit = 1
                hdr.hop += 1
                chunk = self.cache.get_chunk(cid, self.utility(fil,chk,siz,dst))
                hdr.siz = chunk['size']

            else:
                logme3(self.logfh, hdr.seq, src, dst, "REQ", 0, fil, chk, hdr.hop)
                pass

        elif hdr.type == MessageType.RESPONSE:
            logme3(self.logfh, hdr.seq, src, dst, "RSP", 0, fil, chk, hdr.hop)
            evict = self.cache.add_chunk(cid, self.utility(fil,chk,siz,src), siz)
            if len(evict):
                logme3(self.logfh, hdr.seq, src, dst, "DEL", 0, fil, chk, len(evict))
            logme3(self.logfh, hdr.seq, src, dst, "ADD", 0, fil, chk, hdr.hop)

        return False

    def utility(self, fil, chk, siz, dst):
        retrieve_effort = len(self.router.pathdict[(self.router.vrid,dst)])
        uval = self.freq.get(fil, 0.0) * self.freq.get((fil,chk), 0.0) * siz * retrieve_effort
        return uval

    pass


if __name__ == "__main__":
    print sys.argv[0]
    sys.exit(0)