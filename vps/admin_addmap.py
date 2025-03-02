#!/usr/bin/env python

import sys
from orchestrator import BuildMap
from options import options_default

if __name__=='__main__':
    if len(sys.argv) not in (5,6):
        print('Usage: %s fname mapid kite|rando|baladeplat "description" [user]' % sys.argv[0])
        exit()
    fname = sys.argv[1]
    mapid = sys.argv[2]
    type = sys.argv[3]
    desc = sys.argv[4]
    if len(sys.argv)>5:
        user=sys.argv[5]
    else:
        user='unknown'
    print(fname,mapid,desc)
    options = options_default
    if type=='kite':
        options['wind']=True
        options['flat']=True
        options['spdunit']='knots'
        options['maxspd']=True
    elif type=='rando':
        options['spdunit']='km/h'        
        options['wind']=False
        options['flat']=False
        options['maxspd']=True
    elif type=='baladeplat':
        options['spdunit']='km/h'        
        options['wind']=False
        options['flat']=True
        options['maxspd']=False
    trk_id = 0
    trk_seg_id = 0
    pwd = BuildMap(open(fname,"r"),mapid,trk_id,trk_seg_id,mapid,desc,user,options)
