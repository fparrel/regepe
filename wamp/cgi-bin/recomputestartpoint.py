#!c:/Python27/python.exe

import cgi
import os
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from db import DbChkPwd,DbPutWithoutPassword,DbGet
from config import maps_root
from cgiparser import FormParseInt,FormParseStr
from users import CheckSession

def RecomputeStartPointCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    
    # Perform action
    curstartpoint = DbGet(mapid,'startpoint')
    print 'cur startpoint = %s' % (curstartpoint)
    print 'new startpoint = %.4f,%.4f' % (ptlist[0].lat,ptlist[0].lon)
    DbPutWithoutPassword(mapid,'startpoint','%.4f,%.4f' % (ptlist[0].lat,ptlist[0].lon))
    print('Done<BR/>')


print('Content-Type: text/html')
print
try:
	RecomputeStartPointCgi()
except Exception, inst:
    print('<PRE>')
    print('Error: ' + str(inst))
    print(traceback.format_exc())
    print('</PRE>')

