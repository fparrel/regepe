
# For compression
import gzip
# JSON parsing
import json
# Model classes
from model import Point
#date
from db import DbGet
import datetime
import time
from options import options_default

def getDate(mapid):
    date = None
    if mapid!=None:
        #date = datetime.strptime(DbGet(mapid,'date'),'%Y-%m-%d')
        datestr = DbGet(mapid,'date')
        #print 'date="%s"'%datestr
        if datestr!=None and datestr!='':
            date = datetime.datetime(*(time.strptime(datestr,'%Y-%m-%d')[0:6]))
        else:
            date = None
    if date==None:
        return datetime.date(1980,1,1)
    else:
        return date

def convdate(s,d):
    if s=="None":
        return None
    try:
        if len(s)==8:
            t = datetime.datetime(d.year,d.month,d.day,int(s[0:2]),int(s[3:5]),int(s[6:8]))
        else:
            t = datetime.datetime(int(s[0:4]),int(s[5:7]),int(s[8:10]),int(s[11:13]),int(s[14:16]),int(s[17:19]))
    except ValueError,e:
        raise Exception('Cannot parse date %s: %s'%(s,str(e)))
    return t

def convpt(pt,d,spdunit):
    if len(pt)==7:
        return Point(pt[0],pt[1],pt[3],pt[4],pt[6],convdate(pt[2],d),spdunit)
    elif len(pt)==8:
        return Point(pt[0],pt[1],pt[3],pt[4],pt[6],convdate(pt[2],d),spdunit,pt[7])
    else:
        raise Exception('error in convpt')

def ParseMap(mapid):
    
    # Get date
    d = getDate(mapid)

    # Parse json
    f=gzip.open('data/mapdata/%s.json.gz'%mapid,'rb')
    m=json.load(f)
    f.close()
    options=options_default
    for k in ('spdunit','flat','wind','maxspd'):
        options[k]=m[k]
    options['map_type']=m['type']
    return options,map(lambda pt: convpt(pt,d,options['spdunit']), m['points'])
  

## UNIT TEST CODE ##

def main():
    options,ptlist = ParseMap('e23237a52937')
    print len(ptlist)
    print options
    print max(map(lambda pt:pt.spd,ptlist))
    #for pt in ptlist:
    #    print('%s %s %s %s %s %s' % (pt.datetime,pt.lat,pt.lon,pt.ele,pt.spd,pt.course))
    #raw_input('Press Enter')

if __name__ == '__main__':
   main()

