#!/usr/bin/env python

import sys
from db import DbPutWithoutPassword
from demize import Demize

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] in ('-h','--help'):
        print 'Usage: %s mapid' % sys.argv[0]
        exit()
    mapid = sys.argv[1]
    index = 0
    newindex=-1
    while newindex!=0:
        newindex,l = Demize(index,mapid)
        print 'Demize %d/%i'%(newindex,l)
        index = newindex

