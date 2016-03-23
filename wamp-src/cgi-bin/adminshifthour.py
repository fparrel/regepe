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
from datetime import timedelta

def ShiftHourCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    offset = FormParseInt(form,'offset')
    
    Log("ShiftHourCgi: parse map %s\n" % mapid)
    
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    
    # Perform action
    tzdelta = timedelta(hours=offset)
    for pt in ptlist:
        pt.datetime = pt.datetime + tzdelta
    
    Log("ShiftHourCgi: rebuild: Track %s\n" % mapid)
    
    # Rebuild map
    track = Track(ptlist)
    mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    Log("CutMapCgi: rebuild: ProcessTrkSegWithProgress %s\n" % mapid)
    ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True)
    
    Log("ShiftHourCgi: finished %s\n" % mapid)
    
    # Redirect to map
    print('Done</p>')
    print('<p><a href="/showmap.php?mapid=%s">Back to map</a></p></body></html>' % mapid)
    print('<script type="text/javascript">location.href=\'/showmap.php?mapid=%s\';</script>' % mapid)


print('Content-Type: text/html')
print
try:
    print('<html><head></head><body><p>')
    ShiftHourCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
