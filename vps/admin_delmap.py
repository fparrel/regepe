#!/usr/bin/env python

import sys
from db import DbDelMap
import os

if __name__=='__main__':
    mapid = sys.argv[1]
    # Delete map
    DbDelMap(mapid)
    mapfile = 'data/mapdata/%s.json.gz' % mapid
    os.remove(mapfile)
