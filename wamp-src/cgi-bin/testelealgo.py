

import os
from mapparser import ParseMap
from config import maps_root

def main():
    mapid = '5211b89fc0540'#lac negre
    mapid = '50807fdf61260'#uturuncu
    mapid = '5007d4f4be92a'#merveilles
    mapid = '4bcf31221f323'#corsica
    # Parse map
    mapfname = '%s/%s.php' % (maps_root,mapid)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    #print ptlist
    
    # First impl
    threshold = 20
    ele = ptlist[0].ele
    dminus = 0
    dplus = 0
    for pt in ptlist:
        if abs(pt.ele - ele) > threshold:
            if pt.ele - ele<0:
                dminus += ele - pt.ele
                #print 'd-: %d' % (pt.ele - ele)
            else:
                dplus += pt.ele - ele
                #print 'd+: %d' % (pt.ele - ele)
            ele = pt.ele
    print 'D+:%d D-:%d' % (dplus,dminus)
    
    # Second impl
    threshold = 20
    ele = ptlist[0].ele
    print ele
    maxe = ele
    mine = ele
    dminus = 0
    dplus = 0
    lastdiff = 0
    lastmine = mine
    lastmaxe = maxe
    for pt in ptlist:
        if pt.ele>maxe:
            maxe = pt.ele
        if pt.ele<mine:
            mine = pt.ele
        diff = pt.ele - ele
        if abs(diff) > threshold:
            if diff<0:
                if lastdiff==1:
                    print 'up down',lastmine,maxe
                    lastmaxe = maxe
                    dplus += maxe - lastmine
                    print 'd+: %d' % (maxe - lastmine)
                lastdiff = -1
            else:
                if lastdiff==-1:
                    print 'down up',mine,lastmaxe
                    lastmine = mine
                    dminus += lastmaxe - mine
                    print 'd-: %d' % (lastmaxe - mine)
                lastdiff = 1
            ele = pt.ele
            maxe = ele
            mine = ele
    if lastdiff==1:
        print 'end up',lastmine,pt.ele
        dplus += pt.ele - lastmine
    if lastdiff==-1:
        print 'end down',lastmaxe,pt.ele
        dminus += lastmaxe - pt.ele
    print 'D+:%d D-:%d' % (dplus,dminus)

if __name__=='__main__':
    main()
