#!/usr/bin/env python

import sys
from db import DbPutWithoutPassword

if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1] in ('-h','--help'):
        print 'Usage: %s mapid "description"' % sys.argv[0]
        exit()
    mapid = sys.argv[1]
    desc = sys.argv[2] #.encode('utf8') # not needed if terminal handle encoding well
    DbPutWithoutPassword(mapid,'trackdesc',desc)
