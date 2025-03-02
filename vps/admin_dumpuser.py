#!/usr/bin/env python

import sys
from users import DumpUser

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] in ('-h','--help'):
        print('Usage: %s user' % sys.argv[0])
        exit()
    user = sys.argv[1]
    DumpUser(user,show_password=True)
