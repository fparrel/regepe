#!/usr/bin/env python

import sys
from db import DbDelMap
import os

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] in ('-h','--help'):
        print 'Usage: %s mapid' % sys.argv[0]
        exit()
    mapid = sys.argv[1]
    # Delete map
    DbDelMap(mapid)
    mapfile = 'data/mapdata/%s.json.gz' % mapid
    os.remove(mapfile)
