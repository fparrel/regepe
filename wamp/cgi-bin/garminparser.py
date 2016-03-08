
# Model classes
from model import Point
#Datetime
import datetime

#from log import Log

import json

def ParseJsonGarminFile(inputfile,trk_id,trk_seg_id):
    ptlist = []
    data = inputfile.read()
    js = json.loads(data)['com.garmin.activity.details.json.ActivityDetails']
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

