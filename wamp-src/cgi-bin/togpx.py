#!c:/Python27/python.exe

import cgi
import os
from cgiparser import FormParseStr
from config import maps_root
from mapparser import ParseMap
from model import Point


def convertDatetimeToGpxFormat(datetime):
    s = str(datetime)
    return s[0:10] + 'T' + s[11:] + 'Z'

def ToGpx():
    # Get input args
    form = cgi.FieldStorage()
    mapid = FormParseStr(form,'mapid')
    if form.has_key('type'):
        type = form.getvalue('type')
    else:
        type = None
    # Parse map
    if type==None:
        mapfname = '%s/%s.php' % (maps_root,mapid)
    else:
        mapfname = '%s/%s-%s.php' % (maps_root,mapid,type)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    # Print header
    print('<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.0" creator="www.regepe.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n<trk><trkseg>')
    for pt in ptlist:
        if pt.datetime==None:
            print('<trkpt lat="%s" lon="%s">\n<ele>%s</ele>\n<course>%s</course>\n<speed>%.4f</speed>\n</trkpt>' % (pt.lat,pt.lon,pt.ele,pt.course,pt.spd))
        else:
            print('<trkpt lat="%s" lon="%s">\n<time>%s</time><ele>%s</ele>\n<course>%s</course>\n<speed>%.4f</speed>\n</trkpt>' % (pt.lat,pt.lon,convertDatetimeToGpxFormat(pt.datetime),pt.ele,pt.course,pt.spd))
    # Print footer
    print('</trkseg></trk></gpx>\n')


#print('Content-Type: text/xml')
#print('Content-Type: text/plain')
print('Content-Type: application/force-download')
print('Content-Disposition: attachment; filename="out.gpx";') 
print
try:
	ToGpx()
except Exception, inst:
    print('<PRE>')
    print('Error: ' + str(inst))
    print(traceback.format_exc())
    print('</PRE>')

