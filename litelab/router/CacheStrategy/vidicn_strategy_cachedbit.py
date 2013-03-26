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

class vidicn_strategy_cachedbit(object):
    def __init__(self, router, cachesize):
        self.router = router  # Cache's corresponding router
        self.cache = None
        self.logfh = None
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
            if self.cache.is_hit(cid):
                logme3(self.logfh, hdr.seq, src, dst, "REQ", 1, fil, chk, hdr.hop)
                hdr.type = MessageType.RESPONSE
                hdr.swap_src_dst()
                hdr.hit = 1
                hdr.hop += 1
                chunk = self.cache.get_chunk(cid)
                hdr.siz = chunk['size']
            else:
                logme3(self.logfh, hdr.seq, src, dst, "REQ", 0, fil, chk, hdr.hop)
                if not hdr.is_cached_bit_set():
                    if random.random() <= self.get_save_prob(src, dst):
                        hdr.set_cached_bit()
                        hdr.crid = self.router.id
                pass

        elif hdr.type == MessageType.RESPONSE:
            logme3(self.logfh, hdr.seq, src, dst, "RSP", 0, fil, chk, hdr.hop)
            evict = []
            if not self.cache.is_hit(cid):
                if hdr.is_cached_bit_set() and hdr.crid == self.router.id:
                    evict = self.cache.add_chunk(cid, siz)
            if len(evict):
                logme3(self.logfh, hdr.seq, src, dst, "DEL", 0, fil, chk, len(evict))
            logme3(self.logfh, hdr.seq, src, dst, "ADD", 0, fil, chk, hdr.hop)

        return False

    def get_save_prob(self, src, dst):
        p = 1.0
        dist = len(self.router.pathdict[(src,dst)]) - 2
        dist = dist if dist > 0 else 1
        p = p / dist
        return p

    pass


if __name__ == "__main__":
    print sys.argv[0]
    sys.exit(0)
