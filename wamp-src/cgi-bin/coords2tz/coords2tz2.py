# search in kdtree over anydbm

import anydbm
import struct

def point_inside_polygon(x,y,poly):

    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def aera_match(v,aera):
    #print 'aera_match'
    #print 'aera_match %s %s'%(v,aera)
    if v[0]<aera[0][0] or v[0]>aera[0][2] or v[1]<aera[0][1] or v[1]>aera[0][3]:
        return False
    return point_inside_polygon(v[0],v[1],aera[1])

def parse_aera(s):
    (bboxs,ploys,name)=s.split('+')
    bbox = map(float,bboxs.split(','))
    poly = map(lambda pts:map(float,pts.split(',')),ploys.split('*'))
    return (bbox,poly,name)

def unserialize(s):
    (locdefined,loc,left,right)=struct.unpack('<bfii',s[:13])
    i = 13
    l=len(s)
    aeras=[]
    while i<l:
        (r0,r1,r2,r3,tznamelen) = struct.unpack_from('<ffffH',s,i)
        i+=18
        tzname = s[i:i+tznamelen]
        i+=tznamelen
        nbpts=struct.unpack_from('<H',s,i)[0]
        i+=2
        poly = [struct.unpack_from('<ff',s,i+j*8) for j in range(0,nbpts)]
        i+=(8*nbpts)
        aeras.append(((r0,r1,r2,r3),poly,tzname))
    if locdefined==0:
        location=None
    else:
        location=loc
    return (location,left,right,aeras)
    

def find_rec(v,db,nodeidx,depth):
    #print 'find_rec %s %s'%(nodeidx,depth)
    axis = depth % 2
    # Decode from database
    (loc,left,right,aeras)=unserialize(db[str(nodeidx)])
    # First check in aera attached to the node
    for aera in aeras:
        if aera_match(v,aera):
            return aera
    # Then check left or right depending on KD-tree split dimention and value
    if v[axis]<=loc and left!=-1:
        return find_rec(v,db,left,depth+1)
    elif v[axis]>=loc and right!=-1:
        return find_rec(v,db,right,depth+1)
    # If nothing found return none
    return None

tzdb = None

def find_tz(lat,lon):
    # Open db if needed
    global tzdb
    if tzdb==None:
        tzdb = anydbm.open('tzaerastree2.db','r')
    # Perform recursive search in KD-tree
    return find_rec((lon,lat),tzdb,int(tzdb['rootid']),0)

def coords2tz_free():
    # Free db if needed
    if tzdb!=None:
        tzdb.close()

def test1():
    import time
    t1 = time.time()
    found = find_tz(45.0,0.0)
    print time.time()-t1
    if found==None:
        print 'Not found'
    else:
        print 'found=%s'%found[2]

def test2():
    import random
    import time
    random.seed(time.time())
    for i in range(0,100):
        lat = random.random()*180.0-90.0
        lon = random.random()*360.0-180.0
        t1 = time.time()
        found = find_tz(lat,lon)
        t = (time.time()-t1)
        if found==None:
            print '%f %f - Not found in %.3f sec' % (lat,lon,t)
        else:
            print '%f %f - Found %s in %.3f sec'%(lat,lon,found[2],t)

def gettzforstartpt(fname):
    (lat,lon)=map(float,anydbm.open('../../../lamp/cgi-bin/maps/%s'%fname,'r')['startpoint'].split(','))
    print lat,lon
    found = find_tz(lat,lon)
    if found==None:
        return None
    else:
        return found[2]

def test3():
    import os
    for fname in filter(lambda fnam:fnam.endswith('.db'),os.listdir('../../../lamp/cgi-bin/maps')):
        print fname,gettzforstartpt(fname)

if __name__=='__main__':
    test3()
    test1()
    #test2()
    coords2tz_free()
