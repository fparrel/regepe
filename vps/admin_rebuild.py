#!/usr/bin/env python

import sys
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from backup import Backup

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] in ('-h','--help'):
        print 'Usage: %s mapid' % sys.argv[0]
        exit()
    mapid = sys.argv[1]
    options,ptlist = ParseMap(mapid)
    track = Track(ptlist)
    Backup(mapid)
    ProcessTrkSegWithProgress(track,mapid,mapid,True,options)
