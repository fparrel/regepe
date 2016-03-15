#!c:/Python27/python.exe

import cgi
import os
import traceback
from mapparser import ParseMap
from model import Track
from progress import SetProgress
from orchestrator import BuildMapFromTrack
from config import maps_root
from cgiparser import FormParseInt,FormParseStr
from log import Log
from generate_id import uniqid
#from time import strptime
import datetime
from db import DbGet
from users import CheckSession

def MergeCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapids = FormParseStr(form,'mapids').split(',')
    user = FormParseStr(form,'user')
    if user!='unknown':
        sess = FormParseStr(form,'sess')
        if not CheckSession(user,sess):
            raise Exception('Cannot identify user %s %s'%(user,sess))
    
    ptlistmerged = {}
    
    for mapid in mapids:
        Log("MergeCgi: parse map %s\n" % mapid)
        
        # Parse map
        mapfname = '%s/%s.php' % (maps_root,mapid)
        if os.access(mapfname,os.F_OK):
            ptlist = ParseMap(mapfname,False)
        else:
            ptlist = ParseMap(mapfname+'.gz',True)
        
        # set right day if needed
        if ptlist[0].datetime.year<=1980:
            dfromdb = DbGet(mapid,'date')
            if dfromdb:
                d = datetime.datetime.strptime(dfromdb,'%Y-%m-%d')
                for pt in ptlist:
                    pt.datetime = pt.datetime.replace(year=d.year,month=d.month,day=d.day)
        
        # append to dict
        for pt in ptlist:
            ptlistmerged[pt.datetime] = pt
        #ptlistmerged.update(dict(zip(map(lambda pt:pt.datetime,ptlist),ptlist)))
    
    ptlistmerged = ptlistmerged.values()
    ptlistmerged.sort(key=lambda pt:pt.datetime)
    
    Log("MergeCgi: rebuild: Track len=%d\n" % len(ptlistmerged))
    
    newmapid = uniqid()
    
    # Rebuild map
    track = Track(ptlistmerged)
    mapoutfilename = '%s/%s.php' % (maps_root,newmapid)
    Log("MergeCgi: rebuild: ProcessTrkSegWithProgress %s\n" % newmapid)
    pwd = BuildMapFromTrack(track,mapoutfilename,newmapid,'Result of merge',user)
    
    Log("MergeCgi: finished %s\n" % newmapid)
    
    # Redirect to map
    print('Done</p>')
    print('<p><a href="/showmap-flot.php?mapid=%s">Go to map</a></p></body></html>' % newmapid)
    if user=='unknown':
        print('''<script type="text/javascript">
        var date = new Date();
        date.setTime(date.getTime()+(10*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = "pwd%s=%s"+expires+"; path=/";
        location.href=\'/showmap-flot.php?mapid=%s\';
        </script>''' % (newmapid,pwd,newmapid))
    else:
        print('<script type="text/javascript">location.href=\'/showmap-flot.php?mapid=%s\';</script>' % newmapid)


print('Content-Type: text/html')
print
try:
    print('<html><head></head><body><p>')
    MergeCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
