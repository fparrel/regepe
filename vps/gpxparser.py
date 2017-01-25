
# For xml parsing
try:
    from etree.ElementTree import ElementTree
except ImportError:
    from xml.etree.ElementTree import ElementTree

# For date parsing
from datetime import datetime
import time

# Model classes
from model import Bounds,Point,Track

#i18n
from flask_babel import gettext

# gpx creator="KeyMaze 500-700 PC Software" -> spdunit = hectometres/heure


class GpxPoint:
    def __init__(self,trkptxmlelement,xmlns):
        "Create a Point from a gpx:pt xmlelement and the xml namespace"
        self.lat = float(trkptxmlelement.get('lat'))
        self.lon = float(trkptxmlelement.get('lon'))
        elestr = trkptxmlelement.findtext(xmlns+'ele')
        if not elestr==None:
            # replace , by . in case bad formating (MobiDream)
            self.ele = float(elestr.replace(',','.'))
        else:
            self.ele = None
        spdstr = trkptxmlelement.findtext(xmlns+'speed')
        if not spdstr==None:
            self.spd = float(spdstr.replace(',','.'))
        else:
            self.spd = None
        coursestr = trkptxmlelement.findtext(xmlns+'course')
        if not coursestr==None:
            self.course = float(coursestr.replace(',','.'))
        else:
            self.course = None
        datetimestr = trkptxmlelement.findtext(xmlns+'time')
        if not datetimestr==None:
            # date in format YY-mm-dd
            if datetimestr.find('T')==8:
                datetimestr = '20' + datetimestr
            datetimestr = datetimestr[:19]
            # Fix a GPS Action Replay bug
            if not datetimestr.find('Z')==-1:
                datetimestr = datetimestr[:datetimestr.find('Z')]
            try:
                # Python > 2.4
                self.datetime = datetime.strptime(datetimestr,'%Y-%m-%dT%H:%M:%S')
            except AttributeError:
                try:
                    # Python 2.4
                    self.datetime = datetime(*(time.strptime(datetimestr,'%Y-%m-%dT%H:%M:%S')[0:6]))
                except ValueError:
                    raise Exception(gettext('Cannot convert date %s') % datetimestr)
        else:
            self.datetime = None
        for e in trkptxmlelement:
            if e.tag==xmlns+'extensions':
                for sube in e:
                    if sube.tag.endswith('TrackPointExtension'):
                        for subsube in sube:
                            if subsube.tag.endswith('hr'):
                                self.hr = int(subsube.text)
    def ToPoint(self):
        pt = Point(self.lat,self.lon,self.ele,self.spd,self.course,self.datetime)
        if hasattr(self,'hr'):
            pt.hr = self.hr
        return pt


class GpxTrkSeg:
    "Keeps a Track Segement (list of points) got from a gpx file (trkseg tag)"
    # ptlist: list of points
    # bounds: bounds of the list of points
    def __init__(self,trksegxmlelement,xmlns):
        "Create a TrackSeg from a gpx:trkseg xmlelement and the xml namespace"
        self.bounds = Bounds()
        self.ptlist = []
        for trkpt in trksegxmlelement:
            pt = GpxPoint(trkpt,xmlns)
            if not(pt.lat==0.0 and pt.lon==0.0): # Fix for Garmin Connect's bug
                self.ptlist.append(pt)
                self.bounds.Extend(pt.lat,pt.lon)
    def __add__(self,other):
        out = GpxTrkSeg([],'')
        out.ptlist.extend(self.ptlist)
        out.ptlist.extend(other.ptlist)
        for pt in out.ptlist:
            out.bounds.Extend(pt.lat,pt.lon)
        return out


class GpxTrack:
    "Keeps a Track got from a gpx file (trk tag)"
    # trkseglist: list of track segment
    # name: name of the track
    # bounds: bounds of track
    def __init__(self,trkxmlelement,xmlns):
        self.bounds = Bounds()
        self.trkseglist = []
        index = 0
        for e in trkxmlelement:
            if e.tag==xmlns+'name':
                self.name = e.text
            if e.tag==xmlns+'trkseg':
                index = index + 1
                trackseg = GpxTrkSeg(e,xmlns)
                self.trkseglist.append(trackseg)
                self.bounds.Extend(trackseg.bounds)


class GpxRoutePoint:
    # lat
    # lon
    # ele
    # name
    def __init__(self,rteptxmlelement,xmlns):
        "Create a Route Point from a gpx:rtept or a gpx:wpt xmlelement and the xml namespace"
        self.lat = float(rteptxmlelement.get('lat'))
        self.lon = float(rteptxmlelement.get('lon'))
        elestr = rteptxmlelement.findtext(xmlns+'ele')
        if not elestr==None:
            # replace , by . in case bad formating (MobiDream)
            self.ele = float(elestr.replace(',','.'))
        else:
            self.ele = None
        self.name = rteptxmlelement.findtext(xmlns+'name')
    def ToPoint(self):
        return Point(self.lat,self.lon,self.ele,None,None,None)
    def __str__(self):
        return 'GpxRoutePoint(%f,%f,%f,%s)'%(self.lat,self.lon,self.ele,self.name)


class GpxRoute:
    "Keeps a Route got from a gpx file (rte tag)"
    # ptlist: list of GpxRoutePt
    # name: name of the route
    # bounds: bounds of route
    def __init__(self,rtexmlelement,xmlns):
        self.ptlist = []
        self.bounds = Bounds()
        for e in rtexmlelement:
            if e.tag==xmlns+'name':
                self.name = e.text
            elif e.tag==xmlns+'rtept':
                pt = GpxRoutePoint(e,xmlns)
                self.ptlist.append(pt)
                self.bounds.Extend(pt.lat,pt.lon)

class GpxWpts:
    def __init__(self,rtexmlelement,xmlns):
        self.ptlist = []
        self.bounds = Bounds()
        for e in rtexmlelement:
            if e.tag==xmlns+'wpt':
                pt = GpxRoutePoint(e,xmlns)
                self.ptlist.append(pt)
                self.bounds.Extend(pt.lat,pt.lon)                

class GpxFile:
    "Keeps data contained in a gpx file (gpx tag)"
    # tracklist: list of GpxTrack
    # routelist: list of GpxRoute
    # bounds: bounds of gpx file
    def ParseBounds(self,boundsxmlelement):
        self.bounds.minlat = float(boundsxmlelement.get('minlat'))
        self.bounds.maxlat = float(boundsxmlelement.get('maxlat'))
        self.bounds.minlon = float(boundsxmlelement.get('minlon'))
        self.bounds.maxlon = float(boundsxmlelement.get('maxlon'))
    def __init__(self,gpxxmlelement,xmlns):
        self.bounds = Bounds()
        self.tracklist = []
        self.routelist = []
        for e in gpxxmlelement:
            if e.tag==xmlns+'bounds':
                self.ParseBounds(e)
            if e.tag==xmlns+'trk':
                track = GpxTrack(e,xmlns)
                self.tracklist.append(track)
                self.bounds.Extend(track.bounds)
            if e.tag==xmlns+'rte':
                route = GpxRoute(e,xmlns)
                self.routelist.append(route)
            if e.tag==xmlns+'wpt':
                route = GpxWpts(gpxxmlelement,xmlns)
                self.routelist.append(route)


def ParseGpxFile(inputfile,trk_id,trk_seg_id):
    tree = ElementTree()
    tree.parse(inputfile)
    xmlns = str(tree.getroot())
    xmlns = xmlns[xmlns.find('{'):xmlns.find('}')+1]
    gpx = GpxFile(tree.getroot(),xmlns)
    if len(gpx.tracklist)<1:
        # Try with <rte>
        if len(gpx.routelist)<1:
            raise Exception(gettext('No track found in file'))
        else:
            return map(GpxRoutePoint.ToPoint,gpx.routelist[trk_id].ptlist)
    return map(GpxPoint.ToPoint,reduce(lambda x,y:x+y,gpx.tracklist[trk_id].trkseglist).ptlist)
    #return map(GpxPoint.ToPoint,gpx.tracklist[trk_id].trkseglist[trk_seg_id].ptlist)


## UNIT TEST CODE ##

def main():
    #ptlist = ParseGpxFile('D:/Documents/Downloads/Racemment_importa_de_JAN0712_181820.GPX',0,0)
    ptlist = ParseGpxFile('D:/Userfiles/fparrel/Downloads/2015-01-12 1951__20150112_1951.gpx',0,0)
    #ptlist = ParseGpxFile('gpx/FPARREL_832004951_20091022_172903.gpx',0,0)
    #ptlist = ParseGpxFile('Test.gpx',0,0)
    for pt in ptlist:
        print pt
        if hasattr(pt,'hr'):
            print pt.hr
    #raw_input('Press Enter')

if __name__ == '__main__':
   main()

