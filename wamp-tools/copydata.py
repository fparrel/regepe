#!/usr/bin/python

import os
import sys
ELELIST = {'maps':('trackdesc','trackuser','startpoint','date','winddir','demized'),'users':('mail',)}



src_dir = '../lamp-prod'
dest_dir = '../lamp-test'
onlyshow = False

def copy(src,dst):
    print 'copy %s %s' % (src,dst)
    if not onlyshow:
        fsrc = open(src,'rb')
        fdst = open(dst,'wb')
        fdst.write(fsrc.read())
        fdst.close()
        fsrc.close()


def mkdir(dir):
    print 'mkdir %s'%dir
    if not onlyshow:
        if not os.path.exists(dir):
            os.mkdir(dir)

for arg in sys.argv[1:]:
    if arg in ('-h','--help'):
        print 'Usage: copydata.py [-s] [--src=[../]wamp-src|[../]wamp-test|[../]lamp-test|[../]lamp-prod] [--dst=[../]wamp-src|[../]wamp-test|[../]lamp-test|[../]lamp-prod]'
        print 'Default source is %s and default destination is %s' % (src_dir,dest_dir)
        exit(0)
    elif arg=='-s':
        onlyshow = True
    elif arg in ('-d','--diff'):
        showdiffs = True
    elif arg.startswith('--src='):
        src_dir = arg[6:]
        assert(src_dir in ('../wamp-src','../wamp-test','../lamp-test','../lamp-prod','wamp-src','wamp-test','lamp-test','lamp-prod'))
    elif arg.startswith('--dst='):
        dest_dir = arg[6:]
        assert(dest_dir in ('../wamp-src','../wamp-test','../lamp-test','../lamp-prod','wamp-src','wamp-test','lamp-test','lamp-prod'))
    elif arg.startswith('--dest='):
        dest_dir = arg[7:]
        assert(dest_dir in ('../wamp-src','../wamp-test','../lamp-test','../lamp-prod','wamp-src','wamp-test','lamp-test','lamp-prod'))

mkdir('%s/www/maps'%dest_dir)
mkdir('%s/cgi-bin/maps'%dest_dir)
mkdir('%s/cgi-bin/users'%dest_dir)
for f in os.listdir('%s/www/maps'%src_dir):
    copy('%s/www/maps/%s'%(src_dir,f),'%s/www/maps/%s'%(dest_dir,f))
for f in os.listdir('%s/cgi-bin/maps'%src_dir):
    copy('%s/cgi-bin/maps/%s'%(src_dir,f),'%s/cgi-bin/maps/%s'%(dest_dir,f))
for f in os.listdir('%s/cgi-bin/users'%src_dir):
    copy('%s/cgi-bin/users/%s'%(src_dir,f),'%s/cgi-bin/users/%s'%(dest_dir,f))
for f in os.listdir('%s/cgi-bin'%src_dir):
    if f.endswith('.db'):
        copy('%s/cgi-bin/%s'%(src_dir,f),'%s/cgi-bin/%s'%(dest_dir,f))
for ele in ELELIST:
    for field in ELELIST[ele]:
        mkdir('%s/cgi-bin/.rebuild%s'%(dest_dir,field))
