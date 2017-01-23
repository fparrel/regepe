#!/usr/bin/env python

import sys
from orchestrator import BuildMap
from options import options_default

if __name__=='__main__':
    fname = sys.argv[1]
    mapid = sys.argv[2]
    type = sys.argv[3]
    desc = sys.argv[4]
    print fname,mapid,desc
    options = options_default
    if type=='kite':
        options['wind']=True
        options['flat']=True
        options['spdunit']='knots'
        options['maxspd']=True
    trk_id = 0
    trk_seg_id = 0
    pwd = BuildMap(open(fname,"r"),mapid,trk_id,trk_seg_id,mapid,desc,'unknown',options)
