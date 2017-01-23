#!/usr/bin/env python

import sys
from db import DbPutWithoutPassword

if __name__=='__main__':
    mapid = sys.argv[1]
    desc = sys.argv[2] #.encode('utf8')
    DbPutWithoutPassword(mapid,'trackdesc',desc)
