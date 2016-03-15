#!c:/Python27/python.exe

import cgi
import os
from db import DbChkPwd,DbGet,DbPutWithoutPassword
from config import maps_root
from cgiparser import FormParseStr
from users import CheckSession
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from log import Log
from dem2 import GetEleFromLatLonList
import pickle
from backup import Backup

# Class rewritten in light mode for optimal .obj saving
class DemizePt:
    def __init__(self,lat,lon,ele):
        self.lat = lat
        self.lon = lon
        self.ele = ele

def Parse(mapid,type):
    Log('demize: Parse %s\n'%mapid)
    # Parse map
    if type==None:
        mapfname = '%s/%s.php' % (maps_root,mapid)
    else:
        mapfname = '%s/%s-%s.php' % (maps_root,mapid,type)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    track = Track(ptlist)
    return track

def Save(ptlist,mapid):
    Log('demize: Save %s\n'%mapid)
    file = open('tmp/%sptlistlatlonele.obj'%mapid,'w')
    # Instead of saving the whole track object, save (lat,lon,ele) tuple list (takes 10% of size of the whole object)
    pickle.dump(list(map(lambda pt: (pt.lat,pt.lon,pt.ele),ptlist)),file)
    file.close()

def Load(mapid):
    Log('demize: Load %s\n'%mapid)
    file = open('tmp/%sptlistlatlonele.obj'%mapid,'r')
    latlonelelist = pickle.load(file)
    file.close()    
    return map(lambda t: DemizePt(t[0],t[1],t[2]),latlonelelist)

def Demize(ptlist,mapid,index):
    Log('demize: Demize %s %s\n' % (mapid,index))
    GetEleFromLatLonList(ptlist[index:min(index+2000,len(ptlist))],True)

def Rebuild(track,mapid,type):
    Log('demize: Rebuild %s\n' % (mapid))
    # Rebuild map
    if type==None:
        mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    else:
        mapoutfilename = '%s/%s-%s.php' % (maps_root,mapid,type)
    
    Backup(mapid,type)
    
    if type==None:
        ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True)
    else:
        ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True,type=type)

def Clean(mapid):
    tmpfile = 'tmp/%sptlistlatlonele.obj'%mapid
    if os.access(tmpfile,os.F_OK):
        os.remove(tmpfile)

def DemizeCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    pwd = FormParseStr(form,'pwd')
    if form.has_key('type'):
        type = form.getvalue('type')
    else:
        type = None
    
    Log('DemizeCgi mapid=%s type=%s\n'%(mapid,type))
    
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
    
    # Get index if provided, if first call, set to zero
    if form.has_key('index'):
        index = int(form.getvalue('index'))
    else:
        index = 0
    
    if index==0:
        # First call, parse map
        track = Parse(mapid,type)
        ptlist = track.ptlist
    else:
        # Intermediate call, load from .obj file
        track = None
        ptlist = Load(mapid)
    
    Demize(ptlist,mapid,index)
    l = len(ptlist)
    
    # Increment index for next call
    index += 2000
    
    if index<l:
        Save(ptlist,mapid)
        # Send results back to client
        percent = index * 100 / l
        print('<answer><result>OK</result><nextindex>%s</nextindex><percent>%s</percent></answer>' % (index,percent))
    else:
        if track==None:
            # Inermediate calls have occured, reparse map and ...
            track = Parse(mapid,type)
            # ... rewrite elevations from .obj saved tuple list
            i = 0
            for pt in ptlist:
                track.ptlist[i].ele = pt.ele
                i += 1
        # Rebuild map and set demized tag
        Rebuild(track,mapid,type)
        DbPutWithoutPassword(mapid,'demized','Y')
        Clean(mapid)
        Log('Demize end %s\n' % mapid)
        # Send results back to client
        print('<answer><result>Done</result></answer>')


print('Content-Type: text/xml')
print
try:
	DemizeCgi()
except Exception, inst:
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<answer><result>%s</result></answer>' % str(inst))
