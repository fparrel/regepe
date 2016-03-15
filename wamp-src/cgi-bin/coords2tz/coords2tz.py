# search in kdtree over anydbm

import anydbm

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
    if v[0]<aera[0][0] or v[0]>aera[0][2] or v[1]<aera[0][1] or v[1]>aera[0][3]:
        return False
    return point_inside_polygon(v[0],v[1],aera[1])

def parse_aera(s):
    (bboxs,ploys,name)=s.split('+')
    bbox = map(float,bboxs.split(','))
    poly = map(lambda pts:map(float,pts.split(',')),ploys.split('*'))
    return (bbox,poly,name)

def find_rec(v,db,nodeidx,depth):
    #print 'find_rec %s %s'%(nodeidx,depth)
    axis = depth % 2
    s=db[str(nodeidx)]
    (loc,left,right,mid)=s.split('|')
    aeras = map(parse_aera,mid.split('#'))
    for aera in aeras:
        if aera_match(v,aera):
            return aera
    loc=float(loc)
    if v[axis]<=loc:
        return find_rec(v,db,int(left),depth+1)
    elif v[axis]>=loc:
        return find_rec(v,db,int(right),depth+1)
    return None

tzdb = None

def find_tz(lat,lon):
    global tzdb
    if tzdb==None:
        tzdb = anydbm.open('tzaerastree.db','r')
    out = find_rec((lon,lat),tzdb,tzdb['rootid'],0)
    return out

def coords2tz_free():
    tzdb.close()

def test():
    import time
    t1 = time.time()
    found = find_tz(45.0,0.0)
    print time.time()-t1
    if found==None:
        print 'Not found'
    else:
        print 'found=%s'%found[2]

if __name__=='__main__':
    test()
