#!/usr/bin/env python

import sys
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress,BuildMap
from backup import Backup
from db import DbGet
from options import options_default

if __name__=='__main__':
    if len(sys.argv) not in (2,3) or sys.argv[1] in ('-h','--help'):
        print 'Usage: %s mapid [kite|rando|baladeplat|snowkite|surf|riviere]' % sys.argv[0]
        exit()
    mapid = sys.argv[1]
    if len(sys.argv)==2:
        options,ptlist = ParseMap(mapid)
        track = Track(ptlist)
        Backup(mapid)
        ProcessTrkSegWithProgress(track,mapid,mapid,True,options)
    else:
        type = sys.argv[2]
        options = options_default
        if type=='kite':
            options['wind']=True
            options['flat']=True
            options['spdunit']='knots'
            options['maxspd']=True
            options['map_type']='GeoPortal'
        elif type=='rando':
            options['spdunit']='km/h'
            options['wind']=False
            options['flat']=False
            options['maxspd']=True
            options['map_type']='GeoPortal'
        elif type=='baladeplat':
            options['spdunit']='km/h'
            options['wind']=False
            options['flat']=True
            options['maxspd']=False
        elif type=='snowkite':
            options['spdunit']='km/h'
            options['wind']=True
            options['flat']=False
            options['maxspd']=True
            options['map_type']='GeoPortal'
        elif type=='surf':
            options['spdunit']='knots'
            options['wind']=False
            options['flat']=True
            options['maxspd']=True
        elif type=='riviere':
            options['spdunit']='km/h'
            options['wind']=False
            options['flat']=True
            options['maxspd']=True
            options['map_type']='GeoPortal'
        fname = 'uploads/%s_0.gpx'%mapid
        trk_id = 0
        trk_seg_id = 0
        desc = DbGet(mapid,'trackdesc')
        user = DbGet(mapid,'trackuser')
        pwd = BuildMap(open(fname,"r"),mapid,trk_id,trk_seg_id,mapid,desc,user,options)
