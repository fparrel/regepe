#!c:/Python27/python.exe

import cgi
import config
import traceback

def MeterToFeet(x):
    return int(float(x)*3.2808399)

def DoExportWpt(ptlist):
    print 'OziExplorer Waypoint File Version 1.0'
    print 'WGS 84'
    print 'Reserved 2,,Total waypoints: %s' % len(ptlist)
    print 'Reserved 3'
    i = 1
    for pt in ptlist:
        name = pt.name
        if name==None:
            name = 'PT%s' % i
        if pt.ele==None:
            ele = -777
        else:
            ele = MeterToFeet(pt.ele)
        symbol = 3
        print '%s,%s,%s,%s,0,%s,1,0,0,65535,, 0, 0,0,%s,6,0,17,0,10.0,2,,,' % (i,name,pt.lat,pt.lon,symbol,ele)
        i += 1
    #print

def DoExportGpx(ptlist):
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<gpx version="1.0" creator="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">' % config.domain
    #print '<time/>
    #print '<bounds/>'
    for pt in ptlist:
        print '<wpt lat="%s" lon="%s">' % (pt.lat,pt.lon)
        if pt.ele!=None:
            print '<ele>%s</ele>' % pt.ele
        if pt.name!=None:
            print '<name>%s</name>' % pt.name
            print '<cmt>%s</cmt>' % pt.name
            print '<desc>%s</desc>' % pt.name
        print '</wpt>'
    print '</gpx>'

def DoExport(ptlist,exportformat):
    if exportformat=='wpt':
        DoExportWpt(ptlist)
    elif exportformat=='gpx':
        DoExportGpx(ptlist)
    else:
        print 'Format %s not handled\n' % exportformat

class Point:
    def __init__(self,lat,lon,ele=None,name=None):
        self.lat=lat
        self.lon=lon
        self.ele=ele
        self.name=name

def PtStr2FloatArray(ptstr):
    out = ptstr.split(',')
    if len(out)==2:
        #lat,lon
        return Point(float(out[0]),float(out[1]))
    elif len(out)==3:
        #lat,lon,ele
        return Point(float(out[0]),float(out[1]),int(out[2]))
    #lat,lon,ele,name
    return Point(float(out[0]),float(out[1]),int(out[2]),out[3])

try:
    form = cgi.FieldStorage()
    exportformat = form.getvalue('fmt')
    ptlist = map(PtStr2FloatArray,form.getvalue('ptlist').split('~'))
    names = form.getvalue('names').split('~')
    i=0
    for pt in ptlist:
        pt.name = names[i]
        i += 1
    print('Content-Type: application/force-download')
    print('Content-Disposition: attachment; filename="out.%s";' % exportformat) 
    print
    #print 'hello'
    DoExport(ptlist,exportformat)
except Exception, inst:
    print('Content-Type: text/html')
    print
    print('<PRE>')
    print('Error: ' + str(inst))
    print('\n%s' % traceback.format_exc())
    print('</PRE>')
