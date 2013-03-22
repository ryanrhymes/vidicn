#!/usr/bin/env python
# 
# This script implements the CachedBit caching strategy.
#
# Liang Wang @ Dept. Computer Science, University of Helsinki, Finland
# 2011.05.31 created
#

import os
import sys
import time
import binascii
from ctypes import *
from router.common import *
from messageheader import *


class vidicn_heuristic_0(object):
    def __init__(self, router, cachesize):
        self.router = router  # Cache's corresponding router
        self.cache = None
        self.logfh = None
        pass

    def ihandler(self, hdr, router):
        hdr.hop += 1
        cid = hdr.id
        src = hdr.src
        dst = hdr.dst

        print self.router.vrid, "---->", hdr.seq

        if hdr.type == MessageType.REQUEST:
            if self.cache.is_hit(cid):
                logme2(self.logfh, hdr.seq, src, dst, "REQ", 1, cid)
                hdr.type = MessageType.RESPONSE
                hdr.swap_src_dst()
                hdr.hit = 1
                hdr.data = self.cache.get_chunk(cid)

            else:
                logme2(self.logfh, hdr.seq, src, dst, "REQ", 0, cid)

        elif hdr.type == MessageType.RESPONSE:
            logme2(self.logfh, hdr.seq, src, dst, "RSP", 0, cid)
            evict = self.cache.add_chunk(cid, hdr.data)
            if evict[0]:
                logme2(self.logfh, hdr.seq, src, dst, "DEL", 0, evict[0])
            logme2(self.logfh, hdr.seq, src, dst, "ADD", 0, cid)

        return False


if __name__ == "__main__":
    print sys.argv[0]
    sys.exit(0)
