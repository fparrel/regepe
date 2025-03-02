
import anydbm
from urllib import urlopen
from log import Warn
from flask_babel import gettext


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
            raise Exception(gettext('Cannot parse result from TimeZone server %s, assuming GMT+0')%ret)
    except IOError:
        Warn('Sorry, outage on TimeZone server, assuming GMT+0')
        return 0.0
    return tz

def GetTimeZoneCached(lat,lng):
    db = anydbm.open('data/TZ.db', 'c')
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
