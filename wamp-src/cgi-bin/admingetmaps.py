#!/usr/bin/python

import cgi
import hashlib
import dbhash
from xml.sax.saxutils import escape

from db import DbGetListOfDates,DbGetMulitple
from log import Log

def DbGetCgi():
    form = cgi.FieldStorage()
    if not hashlib.sha1(form.getvalue('pwd')).hexdigest()=='${AdminPwdSha1}':
        print 'Error: bad password'
        return
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
            mapdata = DbGetMulitple(mapid,('startpoint','trackdesc','trackuser','pwd'))
            (lat,lon) = mapdata['startpoint'].split(',')
            try:
                desc = mapdata['trackdesc'].encode('ascii', 'xmlcharrefreplace') #.replace('"','&quot;')
                #desc = escape(mapdata['trackdesc'])
            except:
                desc = mapdata['trackdesc']
            print('<map mapid="%s" lat="%s" lon="%s" date="%s" user="%s" pwd="%s">%s</map>' % (mapid,lat,lon,date,mapdata['trackuser'],mapdata['pwd'],desc))
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
