#!c:/Python27/python.exe

from db import DbSearchLatLonRange,DbGetAllMaps,DbGet
from log import Log

import cgi

def GetMapListCgi():
    input = cgi.FieldStorage()
    Log('begin getmaplist\n')
    #if input.has_key('all') and input.getvalue('all')=='yes':
    #    latlonmapidss = DbGetAllMaps()
    #else:
    if input.has_key('minlat'):
        minlat = float(input.getvalue('minlat'))
        maxlat = float(input.getvalue('maxlat'))
        minlon = float(input.getvalue('minlon'))
        maxlon = float(input.getvalue('maxlon'))
        latlonmapidss = DbSearchLatLonRange(minlat,minlon,maxlat,maxlon)
    else:
        latlonmapidss = DbGetAllMaps()
    Log('build list\n')
    print('<results>')
    for (lat,lon,mapids) in latlonmapidss:
        print('<maps lat="%.4f" lon="%.4f">' % (lat,lon))
        for mapid in mapids:
            try:
                trkdesc = DbGet(mapid,'trackdesc')
            except:
                # ignore maps in error
                trkdesc = 'Error'
            try:
                startdate = DbGet(mapid,'date')
            except:
                startdate = ''
            try:
                (lat,lon) = DbGet(mapid,'startpoint').split(',')
            except:
                lat = 0.0
                lon = 0.0
            try:
                trackuser = DbGet(mapid,'trackuser')
            except:
                trackuser = 'unknown'
            print('<map mapid="%s" date="%s" lat="%s" lon="%s" user="%s">%s</map>' % (mapid,startdate,lat,lon,trackuser,trkdesc))
        print('</maps>')
    print('</results>')
    Log('end getmaplist\n')


print('Content-Type: text/xml')
print
try:
	GetMapListCgi()
except Exception, inst:
	print('Error: ' + str(inst))
