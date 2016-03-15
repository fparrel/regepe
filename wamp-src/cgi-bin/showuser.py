#!c:/Python27/python.exe

import cgi

from db import DbGetMapsOfUser,DbGet

class Map:
    def __init__(self,mapid,lat,lon,desc,date):
        self.mapid = mapid
        self.lat=lat
        self.lon=lon
        self.desc=desc
        self.date=date

def ShowUser():
    input = cgi.FieldStorage()
    user = input.getvalue('user')
    mapids = DbGetMapsOfUser(user)
    #print('<result>')
    print('<maps>')
    maps = []
    for mapid in mapids:
        (lat,lon) = DbGet(mapid,'startpoint').split(',')
        trackdesc = DbGet(mapid,'trackdesc')
        startdate = DbGet(mapid,'date')
        try:
            desc = trackdesc.encode('ascii', 'xmlcharrefreplace')
        except:
            desc = trackdesc
        maps.append(Map(mapid,lat,lon,trackdesc,startdate))
    maps.sort(key=lambda map: map.date,reverse=True)
    print('\n'.join(map(lambda map:'<map mapid="%s" lat="%s" lon="%s" date="%s">%s</map>' % (map.mapid,map.lat,map.lon,map.date,map.desc),maps)))
    print('</maps>')
    #print('</result>')


print('Content-Type: text/xml')
print
try:
	ShowUser()
except Exception, inst:
	print('Error: ' + str(inst))
