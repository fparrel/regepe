
# For xml parsing
try:
    from etree.ElementTree import ElementTree
except ImportError:
    from xml.etree.ElementTree import ElementTree

# Model classes
from model import Bounds,Point,Track
# For unzip .kmz
from unzip import iszip,unzipOne
import StringIO

class KmlTuple:
    # lat
    # lon
    # ele
    def __init__(self,str):
        splitresult = str.split(",")
        if len(splitresult)>=2:
            self.lon = float(splitresult[0])
            self.lat = float(splitresult[1])
        else:
            raise Exception("Error while parsing kml file")
        if len(splitresult)==3:
            self.ele = int(float(splitresult[2]))
        else:
            self.ele = None
    def ToPoint(self):
        return Point(self.lat,self.lon,self.ele,None,None,None)
    def __str__(self):
        return '%s,%s,%s' % (self.lat,self.lon,self.ele)


class KmlCoordinates:
    # tuples
    def __init__(self,text):
        self.tuples = []
        #for line in text.splitlines():
        #print 'DEBUG: %s' % text.split()
        for line in text.split():
            self.tuples.append(KmlTuple(line))
    def __str__(self):
        return 'KmlCoordinates(%s)' % ','.join(map(str,self.tuples))


class KmlLineString:
    # coordinates
    def __init__(self,xmlelement,xmlns):
        self.coordinates = KmlCoordinates(xmlelement.findtext(xmlns+'coordinates'))
    def __str__(self):
        return 'KmlLineString(%s)' % str(self.coordinates)


class KmlPlacemark:
    # name
    # geometry
    def __init__(self,xmlelement,xmlns):
        name = xmlelement.findtext(xmlns+'name')
        if name==None:
            name = 'unknown'
            #raise Exception('No name for Placemark')
        self.name = name.replace('/','-')
        self.geometry = None
        for e in xmlelement:
            if e.tag==xmlns+'LineString':
                self.geometry = KmlLineString(e,xmlns)
            elif e.tag==xmlns+'MultiGeometry':
                for sube in e:
                    if sube.tag==xmlns+'LineString':
                        self.geometry = KmlLineString(sube,xmlns)
    def __str__(self):
        return 'KmlPlacemark(%s,%s)' % (self.name,self.geometry)


class KmlContainer:
    # subcontainers
    # placemarks
    # name
    def __init__(self,xmlelement,xmlns):
        self.subcontainers = []
        self.placemarks = []
        name = xmlelement.findtext(xmlns+'name')
        if name==None:
            self.name = 'Root'
        else:
            self.name = name.replace('/','-')
        for e in xmlelement:
            if e.tag==xmlns+'Folder' or e.tag==xmlns+'Document':
                self.subcontainers.append(KmlContainer(e,xmlns))
            if e.tag==xmlns+'Placemark':
                self.placemarks.append(KmlPlacemark(e,xmlns))
    def GetFromPath(self,path):
        splitresult = path.split('/')
        if len(splitresult)==1:
            for placemark in self.placemarks:
                if placemark.name==splitresult[0]:
                    return placemark
            return None
        for subcontainer in self.subcontainers:
            if subcontainer.name==splitresult[0]:
                return subcontainer.GetFromPath('/'.join(splitresult[1:]))
        return None
    def GetFlattedList(self):
        placemarks = self.placemarks
        for subcontainer in self.subcontainers:
            placemarks.extend(subcontainer.GetFlattedList())
        return placemarks
    def __str__(self):
        return 'KmlContainer(%s,\n%s,\n%s\n)' % (self.name,','.join(map(str,self.subcontainers)),','.join(map(str,self.placemarks)))


class KmlFile:
    # root = root container
    def __init__(self,rootxmlelement,xmlns):
        self.root = KmlContainer(rootxmlelement,xmlns)
    def GetFromPath(self,path):
        if len(path)>0:
            if path[0]=='/':
                path = path[1:]
        return self.root.GetFromPath(path)
    def GetFromId(self,trk_id):
        i = 0
        for placemark in self.root.GetFlattedList():
            if placemark.geometry!=None:
                if (i==trk_id):
                    return placemark
                i = i + 1
        return None
    def __str__(self):
        return 'KmlFile(\n%s\n)' % str(self.root)


def ParseKmlFile(inputfile,trk_id,trk_seg_id):
    tree = ElementTree()
    #print 'DEBUG: ParseKmlFile(%s)' % inputfile
    #if iszip(inputfile):
    #    inputfile = StringIO.StringIO(unzipOne(inputfile))
    tree.parse(inputfile)
    xmlns = str(tree.getroot())
    xmlns = xmlns[xmlns.find('{'):xmlns.find('}')+1]
    kml = KmlFile(tree.getroot(),xmlns)
    placemark = kml.GetFromId(trk_id)
    if placemark==None:
        raise Exception('Placemark not found in kml file')
    return map(KmlTuple.ToPoint,placemark.geometry.coordinates.tuples)


def ParseKmlFile2(inputfile,path_to_linestring):
    tree = ElementTree()
    tree.parse(inputfile)
    xmlns = str(tree.getroot())
    xmlns = xmlns[xmlns.find('{'):xmlns.find('}')+1]
    kml = KmlFile(tree.getroot(),xmlns)
    placemark = kml.GetFromPath(path_to_linestring)
    if placemark==None:
        raise Exception('Path not found in kml file')
    return map(KmlTuple.ToPoint,placemark.geometry.coordinates.tuples)


## UNIT TEST CODE ##

def main():
    #ptlist = ParseKmlFile2('Test.kml','My Activities 30-06-2009/Route')
    #ptlist = ParseKmlFile('GUNNN.kmz',0,0)
    ptlist = ParseKmlFile('Test.kml',0,0)
    for pt in ptlist:
        print(pt)
    #raw_input('Press Enter')

if __name__ == '__main__':
   main()

