#!c:/Python27/python.exe

import anydbm
import cgi
from urllib import urlopen


def GetTimeZoneWebService(lat,lng):
    query_str = 'http://www.earthtools.org/timezone/%s/%s'%(lat,lng)
    try:
        f = urlopen(query_str)
        ret = f.read()
        try:
            i = ret.index('<offset>')
            j = ret.index('</',i+7)
            tz = float(ret[i+8:j])
        except:
            raise Exception('Cannot parse result from TimeZone server %s, assuming GMT+0'%ret)
    except IOError:
        #raise Exception('Sorry, outage on TimeZone server, assuming GMT+0')
        print 'Sorry, outage on TimeZone server, assuming GMT+0'
        return 0.0
    return tz

def GetTimeZoneCached(lat,lng):
    db = anydbm.open('TZ.db', 'c')
    dbkey = '%.4f,%.4f' % (lat,lng)
    if db.has_key(dbkey):
        tz = float(db[dbkey])
    else:
        tz = GetTimeZoneWebService(lat,lng)
        db[dbkey] = str(tz)
    db.close()
    return tz

def GetTimeZone(lat,lng):
    return GetTimeZoneCached(lat,lng)

def GetTimeZoneCgi():
    form = cgi.FieldStorage()
    lat = float(form.getvalue('lat'))
    lng = float(form.getvalue('lng'))
    mapid = form.getvalue('mapid')
    tz = GetTimeZoneCached(lat,lng)
    print '%s' % tz

#print('Content-Type: text/html')
#print
#try:
#    GetTimeZoneCgi()
#except Exception, inst:
#    print('Error: ' + str(inst))
