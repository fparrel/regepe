
# Model classes
from model import Bounds,Point,Track
#Datetime
from datetime import datetime,date

#only for unittests
import os

from log import Log

class Date:
    'Contains a date, with writable attributes'
    def __init__(self,year,month,day):
        self.year=year
        self.month=month
        self.day=day


def ParseNmeaLatOrLonVal(strofval):
    'Convert a lat/lon value from nmea format (DDMM.MMMM with DD: degrees, MM.MMMM: minutes) to float in degrees'
    # example: 4512.4589 -> 45 degrees + 12.4589 minutes
    pointid = strofval.find('.')
    if pointid==-1:
        raise Exception('Cannot parse this nmea data "%s"' % strofval)
    deg = float(strofval[0:pointid-2])
    minutes = float(strofval[pointid-2:])
    return (deg + minutes/60)


def ParseGgaSentence(sentence,current_date):
    'Parses a GGA sentence. Since GGA contains time but do not contains date, current_date will be used'
    #sentence[0]: $GPGGA
    #sentence[1]: Time;
    t = datetime(current_date.year,current_date.month,current_date.day,int(sentence[1][0:2]),int(sentence[1][2:4]),int(sentence[1][4:6]))
    #2,3=lat
    lat = ParseNmeaLatOrLonVal(sentence[2]) #float(sentence[2][0:2])+(float(sentence[2][2:])/60)
    if sentence[3]=='S':
        lat = -lat
    #4,5=lon
    lon = ParseNmeaLatOrLonVal(sentence[4]) #float(sentence[4][0:2])+(float(sentence[4][2:])/60)
    if sentence[5]=='W':
        lon = -lon
    #6: Fix quality
    #7: Number of satellites being tracked
    #8: Horizontal dilution of position
    #9,10: ele
    #print('DEBUG:'+sentence[9])
    try:
        ele = int(round(float(sentence[9])))
    except ValueError:
        try:
            #negative values are formated like this: -1.50 -> 1.-50
            ele = int(round(float(sentence[9].replace('.-','.'))))
        except ValueError:
            ele = None
    if sentence[10]!='M':
        raise Exeception('NMEA parse error: unit not supported')
    #11,12: height of geoid
    #13: time in seconds since last DGPS update
    #14: DGPS station ID number
    if lon==0.0 and lat==0.0:
        return None
    return Point(lat,lon,ele,None,None,t)


def ParseRmcSentence(sentence,current_date):
    'Parses a RMC sentence. current_date will be filled with date found in sentence'
    #0: $GPRMC
    #1: time
    #2: A=active,V=void
    #3,4:lat
    #5,6:lon
    #7:speed in knots
    #8:course
    #9: date
    #10,11:magnetic variation
    current_date.year = 2000+int(sentence[9][-2:])
    current_date.month = int(sentence[9][2:4])
    current_date.day = int(sentence[9][0:2])
    t = datetime(2000+int(sentence[9][-2:]),int(sentence[9][2:4]),int(sentence[9][0:2]),int(sentence[1][0:2]),int(sentence[1][2:4]),int(sentence[1][4:6]))
    lat = ParseNmeaLatOrLonVal(sentence[3]) #float(sentence[3][0:2])+(float(sentence[3][2:])/60)
    if sentence[4]=='S':
        lat = -lat
    lon = ParseNmeaLatOrLonVal(sentence[5]) #float(sentence[5][0:2])+(float(sentence[5][2:])/60)
    if sentence[6]=='W':
        lon = -lon
    if sentence[7]!='':
        spd = float(sentence[7]) * 0.514444444
    else:
        spd = None
    if sentence[8]!='':
        course = float(sentence[8])
    else:
        course = None
    if lon==0.0 and lat==0.0:
        return None
    return Point(lat,lon,None,spd,course,t)


def ParseGsaSentence(sentence):
    'Parses a GSA sentence. Parsing result is unused for the moment'
    #Auto/Man A: auto choose 2D or 3D, M: forced 2D or 3D
    #1 no fix, 2: 2D fix, 3: 3D fix
    #PRN of satellites (id or null)
    #... (idem 12 times in total)
    # PDOP
    # HDOP
    # VDOP
    # checksum
    auto_man = sentence[1]
    fix = int(sentence[2])
    if fix>1:
        sat_prn = sentence[3:14]
        pdop = float(sentence[15])
        hdop = float(sentence[16])
        vdop = float(sentence[17])
    return None

def ParseGsvSentence(sentence):
    'Parses a GSV sentence. Parsing result is unused for the moment'
    # number of sentences
    # sentence number
    # number of satellites in view
    
    # sat number
    # elevation deg
    # azimuth deg
    # SNR (higher is better)
    
    # 4 sat max by sentence
    return None

def ParseGllSentence(sentence,current_date):
    #0 GLL          Geographic position, Latitude and Longitude
    #1,2 4916.46,N    Latitude 49 deg. 16.45 min. North
    #3,4 12311.12,W   Longitude 123 deg. 11.12 min. West
    #5 225444       Fix taken at 22:54:44 UTC
    #6 A            Data Active or V (void)
    lat = ParseNmeaLatOrLonVal(sentence[1])
    if sentence[2]=='S':
        lat = -lat
    lon = ParseNmeaLatOrLonVal(sentence[3])
    if sentence[4]=='W':
        lon = -lon
    t = datetime(current_date.year,current_date.month,current_date.day,int(sentence[5][0:2]),int(sentence[5][2:4]),int(sentence[5][4:6]))
    if lon==0.0 and lat==0.0:
        return None
    return Point(lat,lon,None,None,None,t)

def ParseRmbSentence(sentence,current_date):
    return None

def ParseWplSentence(sentence):
    return None

def ParseSentence(line,current_date):
    'Parses a NMEA sentence'
    #checksum = line[:-2]
    try:
        sentence = line[:-3].split(',')
        if sentence[0]=='$GPGGA':
            return ParseGgaSentence(sentence,current_date)
        elif sentence[0]=='$GPRMC':
            return ParseRmcSentence(sentence,current_date)
        elif sentence[0]=='$GPGSA':
            return ParseGsaSentence(sentence)
        elif sentence[0]=='$GPGSV':
            return ParseGsvSentence(sentence)
        elif sentence[0]=='$GPGLL':
            return ParseGllSentence(sentence,current_date)
        elif sentence[0]=='$GPRMB':
            return ParseRmbSentence(sentence,current_date)
        elif sentence[0]=='$GPWPL':
            return ParseWplSentence(sentence)
        else:
            #others are ignored
            return None
            #raise Exception('NMEA sentence %s not supported' % sentence[0])
    except Exception,e:
        Log('Cannot parse "%s": %s\n' % (line,str(e)))
        return None

def ParseNmeaFile(inputfile,trk_id,trk_seg_id):
    current_date = Date(1980,1,1)
    #f = open(inputfile,'r')
    f = inputfile
    ptlist = []
    prevpt = None
    curday = None
    curtrkid = 0
    for line in f:
        if line[0]!='$':
            continue
        pt = ParseSentence(line.rstrip(),current_date)
        if pt==None:
            continue
        #print('DEBUG:ParseNmeaFile:ParseSentence: la=%s lg=%s e=%s s=%s c=%s t=%s' % (pt.lat,pt.lon,pt.ele,pt.spd,pt.course,pt.datetime))
        #if curday!=None:
        #    if pt.datetime.date!=curday:
        #        print('DEBUG: new day')
        #        # New day
        #        if curtrkid==trk_id:
        #            f.close()
        #            return ptlist
        #        else:
        #            ptlist = []
        #        curtrkid += 1
        #curday = pt.datetime.date
        if prevpt!=None:
            #print('DEBUG:ParseNmeaFile:revpt!=None')
            if prevpt.lat==pt.lat and prevpt.lon==pt.lon:
                #print('DEBUG:ParseNmeaFile:prevpt=curpt')
                if prevpt.ele!=None and pt.ele==None:
                    pt.ele = prevpt.ele
                if prevpt.spd!=None and pt.spd==None:
                    pt.spd = prevpt.spd
                ptlist = ptlist[:-1]
        prevpt = pt
        ptlist.append(pt)
    f.close()
    
    # if no date have been found set all points to today's date
    if current_date.year==1980 and current_date.month==1 and current_date.day==1:
        today = date.today()
        current_date.year = today.year
        current_date.month = today.month
        current_date.day = today.day
    
    # Put date of firsts points if possible, and correct speed unit if needed
    for i in range(len(ptlist)-1,-1,-1):
        pt = ptlist[i]
        if pt.spd!=None and pt.spdunit==None:
            pt.spdunit = 'm/s'
        if pt.datetime.year==1980 and pt.datetime.month==1 and pt.datetime.day==1:
            pt.datetime = datetime(current_date.year,current_date.month,current_date.day,pt.datetime.hour,pt.datetime.minute,pt.datetime.second,pt.datetime.microsecond,pt.datetime.tzinfo)
        else:
            current_date.year = pt.datetime.year
            current_date.month = pt.datetime.month
            current_date.day = pt.datetime.day
    
    return ptlist


## UNIT TEST CODE ##

def convertDatetimeToGpxFormat(date,datetime):
    s = str(datetime)
    return date + 'T' + s[11:] + 'Z'

def main():
    f = open('C:/Documents and Settings/fparrel/Desktop/temp/GPS_DATA/FPARREL_113300089_20111226_152142.TXT','rb')
    ptlist = ParseNmeaFile(f,0,0)
    for pt in ptlist:
        print pt.datetime
    return
    path = 'E:/GPS_DATA'
    dir = os.listdir(path)
    dir.sort()
    ptlist = []
    for fname in dir:
        if fname.endswith('.TXT') and fname.startswith('FPARREL_113300089_20111226'):
            print fname
            ptlist.extend(ParseNmeaFile(open('%s/%s'%(path,fname),'rb'),0,0))
    track = Track(ptlist)
    date = '%s-%s-%s' % (ptlist[0].datetime.year,ptlist[0].datetime.month,ptlist[0].datetime.day)
    f = open('out2.gpx','wb')
    # Print header
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.0" creator="www.regepe.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n<trk><trkseg>')
    for pt in ptlist:
        if pt.datetime==None:
            f.write('<trkpt lat="%s" lon="%s">\n<ele>%s</ele>\n<course>%s</course>\n<speed>%.4f</speed>\n</trkpt>' % (pt.lat,pt.lon,pt.ele,pt.course,pt.spd))
        else:
            f.write('<trkpt lat="%s" lon="%s">\n<time>%s</time><ele>%s</ele>\n<course>%s</course>\n<speed>%.4f</speed>\n</trkpt>' % (pt.lat,pt.lon,convertDatetimeToGpxFormat(date,pt.datetime),pt.ele,pt.course,pt.spd))
    # Print footer
    f.write('</trkseg></trk></gpx>\n')
    f.close()
    #for pt in ptlist:
    #    print(pt)
    #raw_input('Press Enter')

if __name__ == '__main__':
   main()

