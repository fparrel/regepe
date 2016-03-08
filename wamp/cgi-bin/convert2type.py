#!c:/Python27/python.exe

import cgi
import os
import traceback
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from config import maps_root
from cgiparser import FormParseInt,FormParseStr
from log import Log
from options import options

def NextMapId(lastmapid):
    returnnext = False
    for mapid in sorted(map(lambda fname: fname[:-3],os.listdir('maps'))):
        if returnnext:
            return mapid
        if lastmapid==None:
            return mapid
        if mapid==lastmapid:
            returnnext = True
    return None

def RebuildCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    type = FormParseStr(form,'type')
    
    isall = False
    if mapid=='all':
        isall = True
        if form.has_key('lastmapid'):
            lastmapid = form.getvalue('lastmapid')
        else:
            lastmapid = None
        mapid = NextMapId(lastmapid)
    if mapid==None:
        print 'Finished<br/>'
        return
    
    Log("RebuildCgi: parse map %s\n" % mapid)
    
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    elif os.access(mapfname+'.gz',os.F_OK):
        ptlist = ParseMap(mapfname+'.gz',True)
    else:
        nextmapid = NextMapId(mapid)
        #os.remove('maps/%s.db'%mapid)
        if isall:
            mapid = nextmapid
        print 'No map data, ignored<br/>'
        ptlist = None
    
    if ptlist!=None:
        Log("RebuildCgi: rebuild: Track %s\n" % mapid)
        
        options['maxspd'] = True
        
        # Rebuild map
        track = Track(ptlist)
        mapoutfilename = '%s/%s-%s.php' % (maps_root,mapid,type)
        Log("RebuildCgi: rebuild: ProcessTrkSegWithProgress %s\n" % mapid)
        ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True,type=type)
        
        Log("RebuildCgi: finished %s\n" % mapid)
        
        print('<p><a href="/showmap.php?mapid=%s">Go to map</a></p></body></html>' % mapid)
    
    print('Done</p>')
    #print('<script type="text/javascript">location.href=\'/showmap.php?mapid=%s\';</script>' % mapid)
    if isall:
        print '<script type="text/javascript">location.href="/cgi-bin/convert2type.py?type=%s&lastmapid=%s&mapid=all";</script>' % (type,mapid)


print('Content-Type: text/html')
print
try:
    print('<html><head></head><body><p>')
    RebuildCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
