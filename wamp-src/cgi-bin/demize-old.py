#!c:/Python27/python.exe

import cgi
import os
from db import DbChkPwd,DbGet
from config import maps_root
from cgiparser import FormParseStr
from users import CheckSession
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from log import Log
from dem import GetEleFromLatLonList
import pickle

def Parse(mapid):
    Log('demize: Parse %s\n'%mapid)
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    track = Track(ptlist)
    return track

def Save(track,mapid):
    Log('demize: Save %s\n'%mapid)
    file = open('tmp/%sele.obj'%mapid,'w')
    pickle.dump(track,file)
    file.close()

def Load(mapid):
    Log('demize: Load %s\n'%mapid)
    file = open('tmp/%sele.obj'%mapid,'r')
    track = pickle.load(file)
    file.close()
    return track

def Demize(track,mapid,index):
    Log('demize: Demize %s %s\n' % (mapid,index))
    GetEleFromLatLonList(track.ptlist[index:min(index+2000,len(track.ptlist))],True)

def Rebuild(track,mapid):
    Log('demize: Rebuild %s\n' % (mapid))
    # Rebuild map
    mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True)


def DemizeCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    pwd = FormParseStr(form,'pwd')
    
    # Check rights
    if form.has_key('user') and form.has_key('sess'):
        user = form.getvalue('user')
        sess = form.getvalue('sess')
        if CheckSession(user,sess):
            map_user = DbGet(mapid,'trackuser')
            if len(map_user)>0 and map_user==user:
                pass
            else:
                raise Exception('Map %s does not belong to user %s, but to user %s' % (mapid,user,map_user))
        else:
            raise Exception('Invalid session, please re-login')
    else:
        if not DbChkPwd(mapid,pwd):
            raise Exception("You do not have the map's password in your browser's cookies")
    
    if form.has_key('index'):
        index = int(form.getvalue('index'))
    else:
        index = 0
    
    if index==0:
        track = Parse(mapid)
    else:
        track = Load(mapid)
    
    Demize(track,mapid,index)
    
    index += 2000
    
    if index<len(track.ptlist):
        Save(track,mapid)
        print('<p>Next step...</p>')
        print('<script type="text/javascript">location.href=\'/cgi-bin/demize.py?mapid=%s&index=%s&user=%s&sess=%s&pwd=%s\';</script>' % (mapid,index,user,sess,pwd))
    else:
        Rebuild(track,mapid)
        Log('Demize end %s\n' % mapid)
        print('<p>Map DEMized</p>')
        print('<P><a href="../">Back to home</a></P>')


print('Content-Type: text/html')
print
try:
	DemizeCgi()
except Exception, inst:
    print('<P><b>Error:</b> %s' % str(inst))
    print('<P><a href="../">Back to home</a></P>')

