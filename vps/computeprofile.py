
from dem import GetEleFromLatLonList
from model import Point
from mathutil import GeodeticDist
from flask_babel import gettext

def ComputeProfile(ptlist,nbpts):
    ptinput2ptoutput = []
    # interpolate ptlist
    period = nbpts/(len(ptlist)-1)
    if period<1:
        period = 1
    nbpts = period*(len(ptlist)-1)
    j = 0
    pts = []
    dists = []
    distint = 0.0
    d = 0.0
    for i in range(0,nbpts):
        if (i % period)==0:
            lat = ptlist[j][0]
            lon = ptlist[j][1]
            j += 1
            ptinput2ptoutput.append(i)
            distint += d
            d = GeodeticDist(lat,lon,ptlist[j][0],ptlist[j][1])
            alpha = 0.0
        else:
            alpha = float(i % period)/float(period)
            lat = (1-alpha)*ptlist[j-1][0] + alpha*ptlist[j][0]
            lon = (1-alpha)*ptlist[j-1][1] + alpha*ptlist[j][1]
        pts.append(Point(lat,lon,None,None,None,None))
        dists.append(distint+d*alpha)
    ptinput2ptoutput.append(i)
    # get elevations
    GetEleFromLatLonList(pts)
    ele = map(lambda pt:pt.ele,pts)
    prevele = None
    for i in range(0,len(ele)):
        if ele[i]==None:
            ele[i] = prevele
        else:
            prevele = ele[i]
    if min(ele)==None or max(ele)==None:
        raise Exception(gettext('Cannot get elevations: ele=%s') % repr(ele))
    return [ele,dists,[],[]]

def main():
    ptlist = [[1.0,2.0],[2.0,3.0],[4.0,5.0],[5.0,6.0]]
    ComputeProfile(ptlist,100)

if __name__=='__main__':
    main()
