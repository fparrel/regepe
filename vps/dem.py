# Digital Elevation Model data reader
# It need .hgt zipped files in dem/dem1 (for 1" resolution data) and in dem/dem3 (for 3" resolution data)
# You can download data from http://www.viewfinderpanoramas.org
# Alternatively, it can request data from geonames.org

import anydbm
from log import Log
import zipfile
import struct
import datetime
from urllib import urlopen
from flask_babel import gettext


def GetEleFromServer(lat,lon):
    "Give elevation from latitude and longitude using geonames.org web service"
    query_str = 'http://api.geonames.org/astergdem?username=fredi&lat=%f&lng=%f' % (lat,lon)
    try:
        f = urlopen(query_str)
        ele = int(f.read())
    except IOError:
        raise Exception(gettext('Sorry, outage on DEM server, please resend the map without the DEM option checked'))
    return ele


data = {}

#In dem1 an dem3 .hgt files, data is serialized as an array of 16 bits big endian signed integers line is longitude
# column is latitude
#unpack1 = 'h'*3601*3601
#unpack3 = 'h'*1201*1201

def GetEleFromDem(lat,lon):
    ilat = int(lat)
    ilon = int(lon)
    if(lat>=0.0):
        fnamelat = 'N%s'% (ilat)
    else:
        fnamelat = 'S%s'% (-ilat)
    if(lon>=0.0):
        fnamelon = 'E%03d'% (ilon)
    else:
        fnamelon = 'W%03d'% (-ilon)
    fname1='dem/dem1/%s%s.zip'%(fnamelat,fnamelon)
    fname3='dem/dem3/%s%s.zip'%(fnamelat,fnamelon)
    if data.has_key(fname1):
        fname = fname1
        demnb = 1
    elif data.has_key(fname3):
        fname = fname3
        demnb = 3
    else:
        try:
            zip = zipfile.ZipFile(fname1,'r')
            demnb = 1
        except Exception,e:
            try:
                zip = zipfile.ZipFile(fname3,'r')
                demnb = 3
            except:
                return GetEleFromServer(lat,lon)
        if demnb==1:
            data[fname1] = zip.read(zip.namelist()[0])
        else:
            data[fname3] = zip.read(zip.namelist()[0])
        zip.close()
    #1 deg = 60 min = 3600 sec
    if demnb==1:
        la=int(3600.0-(lat-ilat)*3600.0)
        lo=int((lon-ilon)*3600.0)
        b=data[fname1][la*7202+lo*2:la*7202+lo*2+2]
    else:
        la=int(1200.0-(lat-ilat)*1200.0)
        lo=int((lon-ilon)*1200.0)
        b=data[fname3][la*2402+lo*2:la*2402+lo*2+2]
    ele = struct.unpack('>h',b)[0]
    return ele

def GetEleFromLatLon(lat,lon):
    return GetEleFromDem(lat,lon)


# Input/Output: pts: objects with lat and lon attributes, ele will be set (or overwritten)
# Return: none
def GetEleFromLatLonList(pts,interpolate=True):

    Log('GetEleFromLatLonList nbpts=%s\n' % len(pts))

    for pt in pts:
        pt.ele = GetEleFromDem(pt.lat,pt.lon)
        # TODO: bufferize buffer

    if interpolate:

        # Interpolate
        curele = pts[0].ele
        curidx = 0
        for i in range(0,len(pts)):
            if pts[i].ele!=curele:

                # build linear interpolation
                for j in range(curidx+1,i):
                    pts[j].ele = int(float(pts[curidx].ele) + float(j-curidx)*float(pts[i].ele-pts[curidx].ele)/float(i-curidx))
                curele = pts[i].ele
                curidx = i


## UNIT TEST CODE ##

def main():
    print GetEleFromDem(47.5,6.5)
    print GetEleFromDem(47.5,6.6)
    print GetEleFromDem(36.5,-6.2)

if __name__ == '__main__':
   main()
