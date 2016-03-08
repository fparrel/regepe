
import os

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

print 'Run translate.py and minify.sh first'
for root, dirs, files in os.walk("."):
    for file in files:
        if in_ignore(root,file):
            continue
        if file.endswith('.php') or file.endswith('.txt') or file.endswith('.apk') or file.endswith('.html') or file.endswith('.css') or file.endswith('.js') or file.endswith('.png') or file.endswith('.gif') or file.endswith('.jpg') or file.endswith('.svg') or file.endswith('.htc') or file.endswith('.py') or file=='.htaccess':
            f_from = open('%s/%s'%(root,file),'r')
            try:
                f_to = open('../lamp/%s/%s'%(root,file),'r')
            except IOError:
                print '+  %s/%s'%(root,file)
                f_from.close()
                continue
            c_from = f_from.read()
            modified=False
            if file.endswith('.php'):
                if c_from.find('http://localhost')>-1:
                    modified=True
                    c_from = c_from.replace('http://localhost','http://regepe.com')
                if c_from.find('.js"')>-1:
                    modified=True
                    c_from = c_from.replace('.js"','.min.js"')
            elif file.endswith('.js'):
                if c_from.find('i30ryoc55sqaj25dkn2ek85y')>-1:
                    modified=True
                    c_from = c_from.replace('${GeoPortalApiKey}','${GeoPortalApiKeyProd}')
            elif file=='config.py':
                if c_from.find("domain = 'localhost'")>-1:
                    modified=True
                    c_from = c_from.replace("domain = 'localhost'","domain = 'regepe.com'")
            elif file.endswith('.py'):
                if c_from.find('#!c:/Python27/python.exe')>-1:
                    modified=True
                    c_from = c_from.replace('#!c:/Python27/python.exe','#!/usr/bin/python')
            f_from.close()
            c_to = f_to.read()
            f_to.close()
            if c_from!=c_to:
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
