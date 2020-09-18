#!/usr/bin/env python

import sys
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from db import DbPutWithoutPassword
import os

def remove_points(mapid, modifyfunction):
        # Parse map
        options, ptlist = ParseMap(mapid)
        # Apply modifications
        ptlist,startpointchanged = modifyfunction(ptlist)
        # Rebuild map
        track = Track(ptlist)
        ProcessTrkSegWithProgress(track,mapid,mapid,True,options)
        # If start point has changed, then update the database
        if startpointchanged:
            DbPutWithoutPassword(mapid,'startpoint','%.4f,%.4f' % (track.ptlist[0].lat,track.ptlist[0].lon))
        # Recompute thumbnail
        previewfile = 'data/thumbnail_cache/%s.png' % mapid
        if os.access(previewfile,os.F_OK):
            os.remove(previewfile)

def main():
	if sys.argv[1] in ('-h','--help'):
		print 'Usage: %s mapid pt1 pt2 crop|clear' % sys.argv[0]
		return
	mapid = sys.argv[1]
	pt1 = int(sys.argv[2])
	pt2 = int(sys.argv[3])
	if sys.argv[4]=='crop':
		modifyfunc = lambda ptlist: (ptlist[pt1:pt2],pt1!=0)
	elif sys.argv[4]=='clear':
		modifyfunc = lambda ptlist: (ptlist[:pt1]+ptlist[pt2:],pt1==0)
	else:
		print 'Modify must be crop or clear'
		return
	remove_points(mapid, modifyfunc)

if __name__=='__main__':
	main()

