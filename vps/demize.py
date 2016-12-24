
import os
from db import DbPutWithoutPassword
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from log import Log
from dem import GetEleFromLatLonList
import pickle
from backup import Backup

if not os.path.isdir('data'):
    os.mkdir('data')
if not os.path.isdir('data/tmp'):
    os.mkdir('data/tmp')

# Class rewritten in light mode for optimal .obj saving
class DemizePt:
    def __init__(self,lat,lon,ele):
        self.lat = lat
        self.lon = lon
        self.ele = ele

def Parse(mapid):
    Log('demize: Parse',mapid)
    # Parse map
    options,ptlist = ParseMap(mapid)
    track = Track(ptlist)
    return track,options

def Save(ptlist,mapid):
    Log('demize: Save',mapid)
    file = open('data/tmp/%sptlistlatlonele.obj'%mapid,'w')
    # Instead of saving the whole track object, save (lat,lon,ele) tuple list (takes 10% of size of the whole object)
    pickle.dump(list(map(lambda pt: (pt.lat,pt.lon,pt.ele),ptlist)),file)
    file.close()

def Load(mapid):
    Log('demize: Load',mapid)
    file = open('data/tmp/%sptlistlatlonele.obj'%mapid,'r')
    latlonelelist = pickle.load(file)
    file.close()    
    return map(lambda t: DemizePt(t[0],t[1],t[2]),latlonelelist)

def Rebuild(track,mapid,options):
    Log('demize: Rebuild',mapid)
    # Rebuild map
    Backup(mapid)
    ProcessTrkSegWithProgress(track,mapid,mapid,True,options)

def Clean(mapid):
    tmpfile = 'data/tmp/%sptlistlatlonele.obj'%mapid
    if os.access(tmpfile,os.F_OK):
        os.remove(tmpfile)

def Demize(index,mapid):
    Log('Demize',mapid)

    if index==0:
        # First call, parse map
        track,options = Parse(mapid)
        ptlist = track.ptlist
    else:
        # Intermediate call, load from .obj file
        track = None
        ptlist = Load(mapid)

    GetEleFromLatLonList(ptlist[index:min(index+2000,len(ptlist))],True)
    l = len(ptlist)

    # Increment index for next call
    index += 2000

    if index<l:
        Save(ptlist,mapid)
        return index,l
    else:
        if track==None:
            # Inermediate calls have occured, reparse map and ...
            track,options = Parse(mapid)
            # ... rewrite elevations from .obj saved tuple list
            i = 0
            for pt in ptlist:
                track.ptlist[i].ele = pt.ele
                i += 1
        # Rebuild map and set demized tag
        Rebuild(track,mapid,options)
        DbPutWithoutPassword(mapid,'demized','Y')
        Clean(mapid)
        Log('Demize end',mapid)
        return 0,l
