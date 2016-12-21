
# Model classes
from model import Bounds,Point,Track
#Datetime
import datetime,time

from log import Log

import json


def ConvertDate(datetimestr):
    if not datetimestr==None:
        try:
            # Python > 2.4
            d = datetime.strptime(datetimestr,'%Y-%m-%d %H:%M:%S')
        except AttributeError:
            try:
                # Python 2.4
                #d = datetime(*(time.strptime(datetimestr,'%Y-%m-%d %H:%M:%S')[0:6]))
                d = datetime.datetime(*(time.strptime(datetimestr,'%Y-%m-%d %H:%M:%S')[0:6]))
            except ValueError:
                raise Exception('Cannot convert date %s' % datetimestr)
        return d
    else:
        return None


def ConvertPt(pt):
    course = None
    ptout = Point(float(pt['lat']),float(pt['lon']),float(pt['alt']),float(pt['speed']),course,ConvertDate(pt['timestamp']),'km/h')
    return ptout

def ParseJsonFile(inputfile,trk_id,trk_seg_id):
    ptlist = []
    data = inputfile.read()
    #print data
    begin = data.find('[')
    end = data.rfind(']')
    data = data[begin:end+1]
    #data = data.replace(',',',\n')
    #print 'ParseJsonFile data="%s"'%data
    pts = json.loads(data)
    return map(ConvertPt,pts)


## UNIT TEST CODE ##

def main():
    from orchestrator import GetFileType
    f = open('ksf15_17.json','rb')
    print GetFileType(f)
    f.seek(0,0)
    ptlist = ParseJsonFile(f,0,0)
    for pt in ptlist:
        print pt.datetime,pt.lat,pt.lon,pt.spd
    return

if __name__ == '__main__':
   main()

