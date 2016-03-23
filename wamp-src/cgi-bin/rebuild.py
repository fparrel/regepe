#!c:/Python27/python.exe

import cgi
import os
import traceback
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from config import maps_root
from cgiparser import FormParseInt,FormParseStr,FormParseOptions,FormParseBool
from log import Log
from options import options

def RebuildCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    forcerecompspd = FormParseBool(form,'forcerecompspd')
    
    Log("RebuildCgi: parse map %s\n" % mapid)
    
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    
    #overwrite options if requested
    FormParseOptions(form,options)
    
    Log("RebuildCgi: rebuild: Track %s\n" % mapid)
    
    # Rebuild map
    track = Track(ptlist)
    if forcerecompspd:
        track.ComputeSpeedWhenNeeded(force=True)
    mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    Log("RebuildCgi: rebuild: ProcessTrkSegWithProgress %s\n" % mapid)
    ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True)
    ProcessTrkSegWithProgress(track,mapoutfilename.replace('.php','-json.php'),mapid,light=True,type='json')
    
    # Recompute thumbnail
    previewfile = '%s/../previews/%s.png' % (maps_root,mapid)
    if os.access(previewfile,os.F_OK):
        os.remove(previewfile)
    
    Log("RebuildCgi: finished %s\n" % mapid)
    
    # Redirect to map
    print('Done</p>')
    print('<p><a href="/showmap-flot.php?mapid=%s">Back to map</a></p></body></html>' % mapid)
    print('<script type="text/javascript">location.href=\'/showmap-flot.php?mapid=%s\';</script>' % mapid)


print('Content-Type: text/html')
print
try:
    print('<html><head></head><body><p>')
    RebuildCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
