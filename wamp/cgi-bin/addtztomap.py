#!c:/Python27/python.exe

import cgi
import os
import traceback
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from db import DbChkPwd,DbPut,DbGet,DbPutWithoutPassword
from config import maps_root
from cgiparser import FormParseInt,FormParseStr
from log import Log
from tz import GetTimeZone
from datetime import timedelta

def AddTimeZoneToMapCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    
    Log("AddTimeZoneToMapCgi: parse map %s\n" % mapid)
    
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    
    # Perform action
    tz = GetTimeZone(ptlist[0].lat,ptlist[0].lon)
    if tz==0:
        print 'In GMT+0, nothing to do'
        return
    tzdelta = timedelta(hours=tz)
    for pt in ptlist:
        pt.datetime = pt.datetime + tzdelta
    
    Log("AddTimeZoneToMapCgi: rebuild: Track %s\n" % mapid)
    
    # Rebuild map
    track = Track(ptlist)
    mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    Log("CutMapCgi: rebuild: ProcessTrkSegWithProgress %s\n" % mapid)
    ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True)
    
    Log("AddTimeZoneToMapCgi: finished %s\n" % mapid)
    
    # Redirect to map
    print('Done</p>')
    print('<p><a href="/showmap.php?mapid=%s">Back to map</a></p></body></html>' % mapid)
    print('<script type="text/javascript">location.href=\'/showmap.php?mapid=%s\';</script>' % mapid)


print('Content-Type: text/html')
print
try:
    print('<html><head></head><body><p>')
    AddTimeZoneToMapCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
