# kdtree with aeras in nodes and its serialization with anydbm

import json
import anydbm
from coords2tz import point_inside_polygon,aera_match
from pprint import pprint

# Compute bounding box from a polygon
def bounding_box(poly):
    (minx,miny,maxx,maxy)=(poly[0][0],poly[0][1],poly[0][0],poly[0][1])
    for (x,y) in poly:
        if(x<minx):
            minx=x
        elif(x>maxx):
            maxx=x
        if(y<miny):
            miny=y
        elif(y>maxy):
            maxy=y
    return (minx,miny,maxx,maxy)

# Group by 2 (reduce(groupby2, [1,2,3,4]) = [(1,2),(3,4)])
def groupby2(a,b):
    if hasattr(a,'__len__'):
        if len(a[-1])==2:
            return a+[[b]]
        else:
            return a[:-1]+[(a[-1][0],b)]
    else:
        return [(a,b)]


class Node:
    nodeidx_ = 0
    def __init__(self,location,leftchild,mid_aeras,rightchild):
        self.location=location
        self.leftchild=leftchild
        self.mid_aeras=mid_aeras
        self.rightchild=rightchild
        self.nodeidx = Node.nodeidx_
        Node.nodeidx_ += 1
    def find_rec(self,v,depth):
        axis = depth % 2
        if self.location==None:
            for aera in self.mid_aeras:
                if aeramatch(v,aera):
                    return aera
        elif v[axis]<=self.location:
            out = self.leftchild.find_rec(v,depth+1)
            if out==None:
                for aera in self.mid_aeras:
                    if aeramatch(v,aera):
                        return aera
                    return self.mid_aeras
            else:
                return out
        elif v[axis]>=self.location:
            out = self.rightchild.find_rec(v,depth+1)
            if out==None:
                for aera in self.mid_aeras:
                    if aeramatch(v,aera):
                        return aera
                    return self.mid_aeras
            else:
                return out
        else:
            raise Exception('<= and >= !!!')
    def find(self,v):
        return self.find_rec(v,0)
    def __str__(self):
        midstr = '#'.join(map(serialize_aera,self.mid_aeras))
        if self.leftchild==None:
            left=-1
        else:
            left=self.leftchild.nodeidx
        if self.rightchild==None:
            right=-1
        else:
            right=self.rightchild.nodeidx
        return '%s|%s|%s|%s' % (self.location,left,right,midstr)

def serialize_aera(aera):
    return '%s+%s+%s'%(str(aera[0])[1:-1],'*'.join(map(lambda pt:'%s,%s'%pt,aera[1])),aera[2])

def compute_median(aeras,axis):
    values = sorted(map(lambda aera:aera[0][axis],aeras)+map(lambda aera:aera[0][axis+2],aeras))
    return values[len(values)/2]

def build_kd_tree_rec(aeras,depth):
    if len(aeras)==0:
        return None
    elif len(aeras)==1:
        return Node(None,None,aeras,None)
    else:
        axis = depth % 2
        median = compute_median(aeras,axis)
        left=[]
        right=[]
        mid=[]
        for (bbox,poly,name) in aeras:
            if bbox[axis+2]<=median:
                left.append((bbox,poly,name))
            elif bbox[axis]>=median:
                right.append((bbox,poly,name))
            else:
                mid.append((bbox,poly,name))
        return Node(median,build_kd_tree_rec(left,depth+1),mid,build_kd_tree_rec(right,depth+1))

def build_kd_tree(aeras):
    return build_kd_tree_rec(aeras,0)

def serialize_kd_tree_rec(tree,db):
    db[str(tree.nodeidx)] = str(tree)
    if tree.leftchild!=None:
        serialize_kd_tree_rec(tree.leftchild,db)
    if tree.rightchild!=None:
        serialize_kd_tree_rec(tree.rightchild,db)

def serialize_kd_tree(tree):
    db = anydbm.open('tzaerastree.db','n')
    db['rootid']=str(tree.nodeidx)
    serialize_kd_tree_rec(tree,db)
    db.close()


print 'Parsing json...'
js = json.load(open('tz_world_compact.json','r'))

aeras = []

for feature in js['features']:
    assert(feature['geometry']['type']=='Polygon')
    tzname = feature['properties']['TZID']
    if tzname=='uninhabited':
        continue
    polygon = reduce(groupby2,feature['geometry']['coordinates'][0])
    r1 = bounding_box(polygon)
    aeras.append((r1,polygon,tzname))

print 'Nb of found aeras=%d. Building KD-tree...'%len(aeras)
tree = build_kd_tree(aeras)
print 'Tree built. Save tree to .db file...'
serialize_kd_tree(tree)
print 'Tree saved. Perform a find test:'
pprint(tree.find((0.0,45.0)))
