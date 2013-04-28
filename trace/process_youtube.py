#!/usr/bin/env python

import os
import sys
import numpy as np
import random
from operator import itemgetter, attrgetter

AVGSIZE = 8.0

def parsing(ifn):
    print "parsing ..."
    ifh = open(ifn, 'r')
    obj = list()
    total_length = 0
    total_videos = 0
    for line in ifh:
        try:
            fields = line.strip().split('|')
            # Process time
            tfs = fields[1].split(':')
            tfv = 0
            if len(tfs) == 3:
                tfv += float(tfs[0]) * 3600 + float(tfs[1]) * 60 + float(tfs[2])
            elif len(tfs) == 2:
                tfv += float(tfs[0]) * 60 + float(tfs[1])
            if tfv == 0:
                tfv = random.randint(4, 12)
            fields[1] = tfv
            obj.append([fields[0], tfv, int(fields[2])])
            total_length += tfv
            total_videos += 1
        except Exception, err:
            pass
    return obj, total_length / total_videos

def format_trace(obj, avglength):
    print "formatting trace ..."
    obj = sorted(obj, key=itemgetter(2), reverse=True)
    for i in range(len(obj)):
        vo = obj[i]
        vo[0] = "%07i" % i
        vo[1] = vo[1] * AVGSIZE / avglength
    return obj

def write_trace(ofn, obj):
    ofh = open(ofn, 'w')
    for vo in obj:
        ofh.write("%s %f %i\n" % (vo[0], vo[1], vo[2]))
    ofh.close()
    pass


if __name__ == "__main__":
    obj, avglength = parsing(sys.argv[1])
    obj = format_trace(obj, avglength)
    write_trace("youtube.trace", obj)
    sys.exit(0)
