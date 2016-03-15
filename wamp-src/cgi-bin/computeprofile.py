#!c:/Python27/python.exe

import cgi
import traceback
from dem2 import GetEleFromLatLonList
from pagebuilder import MyXYChart
from model import Point
from mathutil import GeodeticDist

def ComputeProfile(ptlist,nbpts,width,height):
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
        raise Exception('Cannot get elevations: ele=%s' % repr(ele))
    # build graph
    chart = MyXYChart([dists,ele],'','Elevation','Elevation Profile','Elevation Profile',nbpts=nbpts)
    ptinput2px = map(lambda ptoutput: chart.pt2px[ptoutput],ptinput2ptoutput)
    print chart.imagefileurl
    print str(ele)[1:-1]
    print str(dists)[1:-1]
    print chart.marginsize
    print str(chart.pt2px)[1:-1]
    print str(ptinput2px)[1:-1]

def PtStr2FloatArray(ptstr):
    out = ptstr.split(',')
    return (float(out[0]),float(out[1]))

def DoComputeProfileCgi():
    input = cgi.FieldStorage()
    ptlist = map(PtStr2FloatArray,input.getvalue('ptlist').split('~'))
    if(len(ptlist)<2):
        raise Exception('Cannot compute profile for only one point')
    width = int(input.getvalue('width'))
    height = int(input.getvalue('height'))
    nbpts = 400
    ComputeProfile(ptlist,nbpts,width,height)

def main():
    ptlist = [[1.0,2.0],[2.0,3.0],[4.0,5.0],[5.0,6.0]]
    ComputeProfile(ptlist,100,100)

print('Content-Type: text/html')
print
try:
	DoComputeProfileCgi()
except Exception, inst:
	print('Error: ' + str(inst))
	print(traceback.format_exc())
