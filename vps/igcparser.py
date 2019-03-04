
# Model classes
from model import Point
#Datetime
import datetime
import json

def ConvertDate(initdate,hms):
    return datetime.datetime(initdate['year'],initdate['month'],initdate['day'],int(hms[0]),int(hms[1]),int(hms[2]))

def ParseIgcFile(inputfile,trk_id,trk_seg_id):
    data = json.load(inputfile)
    initdate = data['date']
    timeline_chart = map(lambda d:ConvertDate(initdate,d),zip(data['time']['hour'],data['time']['min'],data['time']['sec']))
    nbTrackPt = data['nbTrackPt']
    nbChartPt = data['nbChartPt']
    idx2time = lambda i: timeline_chart[0] + i * (timeline_chart[-1] + (timeline_chart[-1] - timeline_chart[-2]) - timeline_chart[0]) / nbTrackPt
    timeline = map(idx2time,range(0,nbTrackPt))
    ele = [data['elev'][i*nbChartPt/nbTrackPt] for i in range(0,nbTrackPt)]
    spd = [data['speed'][i*nbChartPt/nbTrackPt] for i in range(0,nbTrackPt)]
    pts = zip(data['lat'],data['lon'],ele,spd,timeline)
    return map(lambda pt: Point(pt[0],pt[1],pt[2],pt[3],None,pt[4]),pts)


## UNIT TEST CODE ##

def main():
    from orchestrator import GetFileType
    f = open('test.igc','rb')
    print GetFileType(f)
    f.seek(0,0)
    ptlist = ParseIgcFile(f,0,0)
    print len(ptlist)
    for pt in ptlist:
        print pt.datetime,pt.lat,pt.lon,pt.spd
    return

if __name__ == '__main__':
   main()

