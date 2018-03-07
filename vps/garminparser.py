
# Model classes
from model import Point
#Datetime
import datetime

#from log import Log

import json

def ParseJsonGarmingFileCourse(inputfile,trk_id,trk_seg_id):
    ptlist = []
    data = inputfile.read()
    js = json.loads(data)
    return map(lambda pt:Point(pt['latitude'],pt['longitude'],pt['elevation'],None,None,datetime.datetime.fromtimestamp(pt['timestamp']/1000)),js['geoPoints'])


def ParseJsonGarminFile(inputfile,trk_id,trk_seg_id):
    ptlist = []
    data = inputfile.read()
    js = json.loads(data)['com.garmin.activity.details.json.ActivityDetails']
    latidx = -1
    lonidx = -1
    eleidx = -1
    spdidx = -1
    timeidx = -1
    for measurement in js['measurements']:
        if measurement['key']=='directLatitude':
            latidx = measurement['metricsIndex']
        elif measurement['key']=='directLongitude':
            lonidx = measurement['metricsIndex']
        elif measurement['key']=='directElevation':
            eleidx = measurement['metricsIndex']
        elif measurement['key']=='directSpeed':
            spdidx = measurement['metricsIndex']
            spdunit = measurement['unit']
        elif measurement['key']=='directTimestamp':
            timeidx = measurement['metricsIndex']
    if latidx == -1 or lonidx == -1:
        raise Exception('lat/lon not found in activity json')
    if eleidx == -1:
        raise Exception('elevation not found in activity json')
    if spdidx == -1 or timeidx == -1:
        raise Exception('speed or time not found in activity json')
    return map(lambda metric: Point(float(metric['metrics'][latidx]),float(metric['metrics'][lonidx]),float(metric['metrics'][eleidx]),float(metric['metrics'][spdidx]),None,datetime.datetime.fromtimestamp(int(metric['metrics'][timeidx]/1000)),spdunit),js['metrics'])


## UNIT TEST CODE ##

def main():
    from orchestrator import GetFileType
    f = open('601780115.json','rb')
    print GetFileType(f)
    f.seek(0,0)
    ptlist = ParseJsonGarminFile(f,0,0)
    for pt in ptlist:
        print pt.datetime,pt.lat,pt.lon,pt.spd
    return

if __name__ == '__main__':
   main()

