
# Model classes
from model import Point
#Datetime
import datetime

import json

def ParseJsonMoveCountFile(inputfile,trk_id,trk_seg_id):
    data = inputfile.read()
    js = json.loads(data)
    return map(lambda trackpoint: Point(trackpoint['Latitude'],trackpoint['Longitude'],trackpoint['Altitude'],None,None,datetime.datetime.fromtimestamp(int(trackpoint['LocalTime']/1000))),js['TrackPoints'])


## UNIT TEST CODE ##

def main():
    from orchestrator import GetFileType
    f = open('41779004.json','rb')
    print(GetFileType(f))
    f.seek(0,0)
    ptlist = ParseJsonMoveCountFile(f,0,0)
    for pt in ptlist:
        print(pt.datetime,pt.lat,pt.lon,pt.spd)

if __name__ == '__main__':
   main()

