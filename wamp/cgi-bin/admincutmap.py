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
from users import CheckSession

def CutMapCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    firstptid = FormParseInt(form,'firstptid')
    lastptid = FormParseInt(form,'lastptid')
    action = FormParseStr(form,'action')
    
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    
    # Perform action
    startpointchanged = False
    if (action=='clear'):
        ptlist = ptlist[:firstptid] + ptlist[lastptid:]
        if firstptid<1:
            startpointchanged = True
    elif (action=='crop'):
        ptlist = ptlist[firstptid:lastptid]
        if firstptid>0:
            startpointchanged = True
    else:
        raise Exception('Invalid Action')
    
    # Rebuild map
    track = Track(ptlist)
    mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    ProcessTrkSegWithProgress(track,mapoutfilename,mapid)
    # If start point has changed, then update the database
    if startpointchanged:
        DbPutWithoutPassword(mapid,'startpoint','%.4f,%.4f' % (track.ptlist[0].lat,track.ptlist[0].lon))
    # Recompute thumbnail
    previewfile = '%s/../previews/%s.png' % (maps_root,mapid)
    if os.access(previewfile,os.F_OK):
        os.remove(previewfile)
    print('Done</p>')
    print('<p><a href="/showmap.php?mapid=%s">Back to map</a></p></body></html>' % mapid)
    print('<script type="text/javascript">location.href=\'/showmap.php?mapid=%s\';</script>' % mapid)


print('Content-Type: text/html')
print
try:
    print('<html><head></head><body><p>')
    CutMapCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
