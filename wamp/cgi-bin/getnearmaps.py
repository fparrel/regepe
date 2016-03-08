#!c:/Python27/python.exe

from db import DbGetNearbyPoints,DbGet,DbGetMulitple
import cgi
import json
import traceback

def GetNearbyMapsCgi():
    input = cgi.FieldStorage()
    mapid = input.getvalue('mapid')
    lat,lon = map(float,DbGet(mapid,'startpoint').split(','))
    print '{'+','.join(['"%s":%s' % (_mapid,json.dumps(DbGetMulitple(_mapid,('startpoint','trackdesc','trackuser','date')))) for _mapid in filter(lambda mid: mid!=mapid,DbGetNearbyPoints(lat,lon))])+'}'

print('Content-Type: application/json')
print
try:
	GetNearbyMapsCgi()
except Exception, inst:
	print('Error: ' + str(inst))
	print(traceback.format_exc())
