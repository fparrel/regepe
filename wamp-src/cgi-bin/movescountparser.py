
# Model classes
from model import Point
#Datetime
import datetime
from tz import GetTimeZone
#from log import Log

import json
#import tzwhere
import pytz

def ParseJsonMoveCountFile(inputfile,trk_id,trk_seg_id):
    ptlist = []
    data = inputfile.read()
    js = json.loads(data)
    #tz = pytz.timezone(tzwhere.w.tzNameAt(js['TrackPoints'][0]['Latitude'],js['TrackPoints'][0]['Longitude']))
    tz = 0
    return map(lambda trackpoint: Point(trackpoint['Latitude'],trackpoint['Longitude'],trackpoint['Altitude'],None,None,datetime.datetime.fromtimestamp(int(trackpoint['LocalTime']/1000)),tz),js['TrackPoints'])
    #return map(lambda metric: Point(float(metric['metrics'][latidx]),float(metric['metrics'][lonidx]),float(metric['metrics'][eleidx]),float(metric['metrics'][spdidx]),None,datetime.datetime.fromtimestamp(int(metric['metrics'][timeidx]/1000)),spdunit),js['metrics'])


## UNIT TEST CODE ##

def main():
    from orchestrator import GetFileType
    f = open('41779004.json','rb')
    print GetFileType(f)
    f.seek(0,0)
    ptlist = ParseJsonMoveCountFile(f,0,0)
    for pt in ptlist:
        print pt.datetime,pt.lat,pt.lon,pt.spd
    return

if __name__ == '__main__':
   main()

