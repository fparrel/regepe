
# For compression
import gzip
import zlib
# Model classes
from model import Point
#Datetime
from datetime import datetime
#options
from options import options
#date
from db import DbGet
import datetime
import time

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

def ParsePoint(line,d,forcems=False):
    #	new Point(43.622773,7.046705,"10:40:46",157,0.14,1,28),
    fields = line[line.index('(')+1:line.rindex(')')].split(',')
    if fields[2]=='"None"':
        t = None
    else:
        try:
            if len(fields[2])==10:
                t = datetime.datetime(d.year,d.month,d.day,int(fields[2][1:3]),int(fields[2][4:6]),int(fields[2][7:9]))
            else:
                t = datetime.datetime(int(fields[2][1:5]),int(fields[2][6:8]),int(fields[2][9:11]),int(fields[2][12:14]),int(fields[2][15:17]),int(fields[2][18:20]))
        except ValueError,e:
            raise Exception('Cannot parse date %s: %s'%(fields[2],str(e)))
    #print 'DEBUG: spd=%s "%s"' % (float(fields[4]),options['spdunit'])
    if not forcems:
        spdunit = options['spdunit']
    else:
        spdunit = 'm/s'
    if len(fields)==7:
        return Point(float(fields[0]),float(fields[1]),int(fields[3]),float(fields[4]),int(fields[6]),t,spdunit)
    elif len(fields)==8:
        return Point(float(fields[0]),float(fields[1]),int(fields[3]),float(fields[4]),int(fields[6]),t,spdunit,int(fields[7]))
    else:
        raise Exception('mapparser.py:54 Cannot parse line="%s"'%line)


def ParseMap(inputfname,compressed,forcems=False):
    
    # Get date
    i = inputfname.find('maps/')
    if i!=-1:
        j = inputfname.find('.',i+5)
        if j!=-1:
            mapid = inputfname[i+5:j]
    
    if mapid.endswith('-json'):
        mapid = mapid[:-5]
        type = 'json'
    else:
        type = 'ggl'
    
    d = getDate(mapid)
    
    if compressed:
        try:
            f = gzip.open(inputfname,'rb')
            contents = f.read()
        except:
            f = open(inputfname,'rb')
            contents = zlib.decompress(f.read())
    else:
        f = open(inputfname,'rb')
        contents = f.read()
    f.close()
    ptlist = []
    inptlist = False
    for line in contents.splitlines():
        #if not inptlist:
            #print 'DEBUG: %s<br/>' % line
        if inptlist:
            if line[:2]=='];':
                inptlist = False
                break
            else:
                ptlist.append(ParsePoint(line,d,forcems))
        elif line[:12]=='track_points':
            inptlist = True
        elif line[:12]=='$map_type = ':
            options['map_type'] = line[13:-2]
        elif line[:10]=='spdunit = ':
            options['spdunit'] = line[11:-2]
        elif line[:7]=='flat = ':
            options['flat'] = (line[7:-1]=='1')            
        elif line[:7]=='wind = ':
            options['wind'] = (line[7:-1]=='1')
        elif line[:9]=='maxspd = ':
            options['maxspd'] = (line[9:-1]=='1')
    #print 'DEBUG: %s' % options
        # no need to recompute ele from DEM
    return ptlist
  

## UNIT TEST CODE ##

def main():
    ptlist = ParseMap('../www/maps/52de97b7d06df.php.gz',True)
    print len(ptlist)
    ptlist = ParseMap('../../lamp/www/maps/52d45ad063a22.php.gz',True)
    print len(ptlist)
    return
    print options
    for pt in ptlist:
        print('%s %s %s %s %s %s' % (pt.datetime,pt.lat,pt.lon,pt.ele,pt.spd,pt.course))
    #raw_input('Press Enter')

if __name__ == '__main__':
   main()

