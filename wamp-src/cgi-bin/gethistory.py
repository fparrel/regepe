#!c:/Python27/python.exe

import cgi

from db import DbGetListOfDates,DbGet
from log import Log

def DbGetCgi():
    form = cgi.FieldStorage()
    if form.has_key('limit'):
        limit = int(form.getvalue('limit'))
    else:
        limit = -1
    Log('begin gethistory\n')
    l = DbGetListOfDates()
    Log('af DbGetListOfDates\n')
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print '<maps>'
    cptr = 0
    #for date,maps in l.iteritems():
    for date in sorted(l.iterkeys(),reverse=True):
        maps = l[date]
        for mapid in maps:
            (lat,lon) = DbGet(mapid,'startpoint').split(',')
            trackdesc = DbGet(mapid,'trackdesc')
            trackuser = DbGet(mapid,'trackuser')
            try:
                desc = trackdesc.encode('ascii', 'xmlcharrefreplace')
            except:
                desc = trackdesc
            print('<map mapid="%s" lat="%s" lon="%s" date="%s" user="%s">%s</map>' % (mapid,lat,lon,date,trackuser,desc))
            cptr += 1
            if(limit>-1) and (cptr>limit):
                break
        if(limit>-1) and (cptr>limit):
            break
    print '</maps>'
    Log('end gethistory\n')


print('Content-Type: text/xml')
print
try:
    DbGetCgi()
except Exception, inst:
    import traceback
    print('Error: ' + str(inst))
    print(traceback.format_exc())
