
import os
import sys

def in_ignore(root,file):
    # root
    if root=='.':
        return True
    # maps and user db
    if root in ('.\www\maps','.\cgi-bin\maps','.\cgi-bin\maps-Bad','.\cgi-bin\users') or file.endswith('_INV.db') or file in ('DEM.db','PROGRESS.db','TZ.db'):
        return True
    # previews
    if root=='.\www\previews':
        return True
    # compiled python
    if file.endswith('.pyc'):
        return True
    # dem not duplicated
    if root=='.\cgi-bin\dem1' or root=='.\cgi-bin\dem3':
        return True
    # logs
    if root=='.\cgi-bin\logs':
        return True
    # 230 db
    if file=='Log230.csv':
        return True
    # not used
    if root.startswith('.\www\wmts') or root.startswith('.\www\meteociel') or root.startswith('.\www\meteomarine'):
        return True
    if root.startswith('.\cgi-bin\pytz\zoneinfo') or root=='.\cgi-bin\coords2tz':
        return True
    # wamp admin tools
    if file in ('genrebuildall.sh',):
        return True
    # .bak
    if file.endswith('.bak'):
        return True
    # tests
    if file.startswith('test') and root.startswith('.\\cgi-bin'):
        return True
    if file.startswith('test') and root.startswith('.\\www'):
        return True
    # maintenance scripts
    if file.startswith('maintenance') and root.startswith('.\\www'):
        return True
    return False

def open_mkdir(fname,row):
    path = os.path.dirname(fname)
    print 'path='+path
    if not os.path.exists(path):
        print 'mkdir -p '+path
        os.makedirs(path)
    return open(fname,row)

instantiate_new = False
test_sys = False

if len(sys.argv)>1 and sys.argv[1] in ('-h','--help'):
    print 'Usage: python toprod.py [--new]'
    exit(0)
elif len(sys.argv)>1 and sys.argv[1] in ('-n','--new'):
    instantiate_new = True
if len(sys.argv)>2 and sys.argv[2] in ('-t','--test'):
    test_sys = True

print 'Run translate.py and minify.sh first'
if test_sys:
    dest_dir = 'lamp-test/'
else:
    dest_dir = 'lamp-prod/'
for root, dirs, files in os.walk("wamp"):
    for file in files:
        if in_ignore(root,file):
            continue
        is_new = False
        if file.endswith('.php') or file.endswith('.txt') or file.endswith('.apk') or file.endswith('.html') or file.endswith('.css') or file.endswith('.js') or file.endswith('.png') or file.endswith('.gif') or file.endswith('.jpg') or file.endswith('.svg') or file.endswith('.htc') or file.endswith('.py') or file=='.htaccess':
            f_from = open('%s/%s'%(root,file),'r')
            try:
                f_to = open('%s/%s'%(root.replace('wamp/',dest_dir),file),'r')
            except IOError:
                print '+  %s/%s'%(root,file)
                if instantiate_new:
                    f_to = open_mkdir('%s/%s'%(root.replace('wamp/',dest_dir),file),'w')
                    is_new = True
                else:
                    f_from.close()
                    continue
            c_from = f_from.read()
            modified=False
            if file.endswith('.php'):
                if c_from.find('http://localhost')>-1 and not test_sys:
                    modified=True
                    c_from = c_from.replace('http://localhost','http://regepe.com')
                if c_from.find('.js"')>-1 and not test_sys:
                    modified=True
                    c_from = c_from.replace('.js"','.min.js"')
            elif file.endswith('.js'):
                if c_from.find('${GeoPortalApiKey}')>-1:
                    modified=True
                    c_from = c_from.replace('${GeoPortalApiKey}','${GeoPortalApiKeyProd}')
            elif file=='config.py' and not test_sys:
                if c_from.find("domain = 'localhost'")>-1:
                    modified=True
                    c_from = c_from.replace("domain = 'localhost'","domain = 'regepe.com'")
            elif file.endswith('.py'):
                if c_from.find('#!c:/Python27/python.exe')>-1:
                    modified=True
                    c_from = c_from.replace('#!c:/Python27/python.exe','#!/usr/bin/python')
            f_from.close()
            if instantiate_new and is_new:
                f_to.write(c_from)
            else:
                c_to = f_to.read()
            f_to.close()
            if not is_new and c_from!=c_to:
                if modified:
                    print 'D! %s/%s'%(root,file)
                    #print len(c_from),len(c_to)
                    #open('d:/from.%s.txt'%file,'w').write(c_from)
                    #open('d:/to.%s.txt'%file,'w').write(c_from)
                    #print c_from
                    #print c_to
                else:
                    print 'D  %s/%s'%(root,file)
        else:
            print '!!! %s %s' % (root,file)
