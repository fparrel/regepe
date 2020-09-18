#!/usr/bin/env python
import sys
from db import DbRebuildAllIfNeeded

if __name__=='__main__':
    if len(sys.argv)==1:
        for dbname in DbRebuildAllIfNeeded(force=('date', 'trackdesc', 'trackuser', 'startpoint'), verbose=True):
            print dbname
    elif sys.argv[1] in ('-h','--help'):
        print 'Usage: %s [date] [trackdesc] [trackuser] [startpoint]' % sys.argv[0]
        print '         Rebuild given indexes'
        print '       %s' % sys.argv[0]
        print '         Rebuild all indexes'
    else:
        for dbname in DbRebuildAllIfNeeded(force=sys.argv[1:], verbose=True):
            print dbname

