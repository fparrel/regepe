
# Model classes
from model import Point
#Datetime
import datetime


def ParseRegepeFile(inputfile,trk_id,trk_seg_id):
    ptlist = []
    #print 'ParseRegepeFile begin'
    for line in inputfile:
        if line[0]==':':
            #print 'new point'
            fields = line[1:].rstrip().split(',')
            #print fields
            t = datetime.datetime.fromtimestamp(int(fields[5])/1000)
            ptlist.append(Point(float(fields[0]),float(fields[1]),int(float(fields[2])),float(fields[3]),float(fields[4]),t))
    return ptlist


## UNIT TEST CODE ##

def main():
    f = open('test.rgp','rb')
    ptlist = ParseRegepeFile(f,0,0)
    for pt in ptlist:
        print pt.datetime
    return

if __name__ == '__main__':
   main()

