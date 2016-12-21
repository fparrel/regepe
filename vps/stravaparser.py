
# Model classes
from model import Point
#Datetime
import datetime
#from tz import GetTimeZone
from log import Log

import json
#import tzwhere
#import pytz
import urllib2


def ParseJsonStravaFile(inputfilejson,inputfilehtml,trk_id,trk_seg_id):
    data = inputfilehtml.read()
    #open('tmp.html','wb').write(data)
    timeopentag = '<time>'
    tstart = data.index(timeopentag)+len(timeopentag)
    tend = data.index('</time>',tstart)
    t = data[tstart:tend]
    departure = datetime.datetime.strptime(t,"%B %d, %Y")
    ptlist = []
    data = inputfilejson.read()
    js = json.loads(data)
    #tz = pytz.timezone(tzwhere.w.tzNameAt(js['TrackPoints'][0]['Latitude'],js['TrackPoints'][0]['Longitude']))
    tz = 0
    return map(lambda i: Point(js['latlng'][i][0],js['latlng'][i][1],int(js['altitude'][i]),None,None,departure+datetime.timedelta(seconds=int(js['time'][i]),hours=8),tz),range(0,len(js['latlng'])))

def UrlOpenStrava(activityid):
    request_headers = {"Accept-Language": "en-US,en;q=0.5","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    request = urllib2.Request("https://www.strava.com/activities/%s"%activityid, headers=request_headers)
    f = urllib2.urlopen(request)
    return f


## UNIT TEST CODE ##

def main():
    from orchestrator import GetFileType
    #fhtml = UrlOpenStrava('505558211')
    fhtml = open('505558211.htm','rb')
    f = open('505558211.json','rb')
    print GetFileType(f)
    f.seek(0,0)
    ptlist = ParseJsonStravaFile(f,fhtml,0,0)
    for pt in ptlist:
        print pt.datetime,pt.lat,pt.lon,pt.spd,pt.ele
    return

if __name__ == '__main__':
   main()
