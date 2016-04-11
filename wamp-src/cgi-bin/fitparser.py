
# Model classes
from model import Bounds,Point,Track
#Datetime
from datetime import datetime,date

import struct

#only for unittests
import os

from log import Log

def DecodeField(f):
    endianability = (f[2] & 0b10000000)>0
    basetypenb = f[2] & 0b00001111
    return f[0],f[1],endianability,basetypenb
    #field definition number, size in bytes, endianability, base type number

fitBaseTypeToStruct = ['B','b','B','h','H','i','I',Exception('not implemented'),'f','d','B','H','I',Exception('not implemented')]

fieldDefNbName = ['lat','lon','ele','heartrate','cadence','','speed','power','','','','','','temperature']+[''for i in range(0,256)]
fieldDefNbName[253]='datetime'

#latitude = (lat / (double)0x7fffffff) * 180

class FitDecoder:
    def __init__(self,inputfile):
        self.fd = inputfile
        self.data = []
        self.eof = False
        self.fields = {}
        self.datastruct = {}
        self.datastructlen = {}
        self.ptlist=[]
        self.where_are_lat={}
        self.where_are_lon={}
        self.where_are_ele={}
        self.where_are_spd={}
        self.where_are_time={}
    def DecodeRecord(self):
        rechdr = struct.unpack("<B",self.fd.read(1))[0]
        if rechdr=='':
            return False
        compressed = (rechdr & 0b10000000)>0
        if not compressed:
            definition = (rechdr & 0b01000000)>0    
            locmsgtype = (rechdr & 0b00001111)
        else:
            raise Exception('compressed header not implemented')
        if definition:
            try:
                (reserved,archi,msgnb,nbfields) = struct.unpack('<BBHB',self.fd.read(5))
            except:
                print 'Cannot read more'
                return False
            if archi!=0:
                raise Exception('big endian not implemented')
            fields = map(lambda i: struct.unpack('<BBB',self.fd.read(3)),range(0,nbfields))
            fields = map(DecodeField,fields)
            print 'fields',locmsgtype,fields
            self.fields[locmsgtype] = fields
            self.datastruct[locmsgtype] = '<'+''.join(map(lambda field:fitBaseTypeToStruct[field[3]],fields))
            self.datastructlen[locmsgtype] = struct.calcsize(self.datastruct[locmsgtype])
            for i in range(0,len(fields)):
                if fieldDefNbName[fields[i][0]]=='lat':
                    self.where_are_lat[locmsgtype]=i
                if fieldDefNbName[fields[i][0]]=='lon':
                    self.where_are_lon[locmsgtype]=i
                if fieldDefNbName[fields[i][0]]=='ele':
                    self.where_are_ele[locmsgtype]=i
                if fieldDefNbName[fields[i][0]]=='speed':
                    self.where_are_spd[locmsgtype]=i
        else:
            if locmsgtype not in self.datastruct:
                print 'locmsgtype has bad value %d rode %d data recods at %d bytes of file'%(locmsgtype,len(self.data),self.fd.tell())
                return False
            data = struct.unpack(self.datastruct[locmsgtype],self.fd.read(self.datastructlen[locmsgtype]))
            #print 'data',locmsgtype,data
            self.data.append(data)
            if locmsgtype in self.where_are_lat and locmsgtype in self.where_are_lon:
                lat=(data[self.where_are_lat[locmsgtype]]/2147483647.000000)*180.0
                lon=(data[self.where_are_lon[locmsgtype]]/2147483647.000000)*180.0
            else:
                lat=None
            if locmsgtype in self.where_are_ele:
                ele=data[self.where_are_ele[locmsgtype]]/5.0-500.0
            else:
                ele=None
            if locmsgtype in self.where_are_spd:
                try:
                    spd=data[self.where_are_spd[locmsgtype]]/1000.0
                except:
                    spd=None
            else:
                spd=None
            if locmsgtype in self.where_are_time:
                tm =  datetime.fromtimestamp(data[self.where_are_datetime[locmsgtype]]+631065600)
            else:
                tm=None
            if lat!=None:
                self.ptlist.append(Point(lat,lon,ele,spd,None,datetime))
        return True
    def DecodeFile(self):
        while self.DecodeRecord():
            pass

def ParseFitFile(inputfile,trk_id,trk_seg_id):
    ptlist=[]
    
    # Parse file header
    hdrsize = ord(inputfile.read(1))
    print hdrsize
    hdr = inputfile.read(hdrsize-1)
    (protocol_version,profile_version,data_size,data_type,crc) = struct.unpack("<BHI4sH",hdr)
    assert(data_type=='.FIT')
    #TODO: CRC check
    
    dec = FitDecoder(inputfile)
    dec.DecodeFile()
    return dec.ptlist
    
    #first record header
    rechdr = struct.unpack("<B",inputfile.read(1))[0]
    compressed = (rechdr & 0b10000000)>0
    if not compressed:
        definition = (rechdr & 0b01000000)>0    
        locmsgtype = (rechdr & 0b00001111)
    else:
        raise Exception('compressed header not implemented')
    if definition:
        (reserved,archi,msgnb,nbfields) = struct.unpack('<BBHB',inputfile.read(5))
        if archi!=0:
            raise Exception('big endian not implemented')
        fields = map(lambda i: struct.unpack('<BBB',inputfile.read(3)),range(0,nbfields))
    fields = map(DecodeField,fields)
    print fields
    inputfile.close()
    return ptlist


## UNIT TEST CODE ##

def convertDatetimeToGpxFormat(date,datetime):
    s = str(datetime)
    return date + 'T' + s[11:] + 'Z'

def main():
    f = open('../../63U85834.FIT','rb')
    ptlist = ParseFitFile(f,0,0)
    for pt in ptlist:
        print pt.datetime
    return

if __name__ == '__main__':
   main()

