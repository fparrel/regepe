
import os
import sys
import json

def in_ignore(root,file):
    #print 'in_ignore('+root+','+file
    # root
    if root=='.':
        return True
    # maps and user db
    if root in (src_dir+'/www/maps',src_dir+'/cgi-bin/maps',src_dir+'/cgi-bin/maps-Bad',src_dir+'/cgi-bin/users') or file.endswith('_INV.db') or file in ('DEM.db','PROGRESS.db','TZ.db'):
        return True
    # previews
    if root==src_dir+'/www/previews':
        return True
    # compiled python
    if file.endswith('.pyc'):
        return True
    # dem not duplicated because too big
    if root==src_dir+'/cgi-bin/dem1' or root==src_dir+'/cgi-bin/dem3':
        return True
    # logs
    if root==src_dir+'/cgi-bin/logs':
        return True
    # 230 db
    if file=='Log230.csv':
        return True
    # not used
    if root.startswith(src_dir+'/www/wmts') or root.startswith(src_dir+'/www/meteociel') or root.startswith(src_dir+'/www/meteomarine'):
        return True
    if root==src_dir+'/cgi-bin/coords2tz':
        return True
    # wamp admin tools
    if file in ('genrebuildall.sh',):
        return True
    # .bak
    if file.endswith('.bak'):
        return True
    # tests
    if file.startswith('test') and root.startswith(src_dir+'/cgi-bin'):
        return True
    if file.startswith('test') and root.startswith(src_dir+'/www'):
        return True
    # maintenance scripts
    if file.startswith('maintenance') and root.startswith(src_dir+'/www'):
        return True
    return False

def open_mkdir(fname,row):
    path = os.path.dirname(fname)
    #print 'path='+path
    if not os.path.exists(path):
        #print 'mkdir -p '+path
        os.makedirs(path)
    return open(fname,row)

instantiate_new = False
src_dir = 'wamp'
dest_dir = 'lamp-prod'

for arg in sys.argv[1:]:
    if arg in ('-h','--help'):
        print 'Usage: python toprod.py [--new|-n] [--src=wamp|lamp-test|lamp-prod] [--dst=wamp|lamp-test|lamp-prod]'
        print '--new: copy non exiting files to destination'
        print 'Default source is wamp and default destination is lamp-prod'
        exit(0)
    elif arg in ('-n','--new'):
        instantiate_new = True
    elif arg.startswith('--src='):
        src_dir = arg[6:]
        assert(src_dir in ('wamp','lamp-test','lamp-prod'))
    elif arg.startswith('--dst='):
        dest_dir = arg[6:]
        assert(dest_dir in ('wamp','lamp-test','lamp-prod'))
    elif arg.startswith('--dest='):
        dest_dir = arg[7:]
        assert(dest_dir in ('wamp','lamp-test','lamp-prod'))

pythonwindowsbinarypostcgistuff = '''try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass
'''

if dest_dir in ('lamp-prod'):
    keysnpwds = json.load(open('keysnpwds-prod.json','r'))
elif dest_dir in ('lamp-test','wamp'):
    keysnpwds = json.load(open('keysnpwds-test.json','r'))

print 'Source=%s Destination=%s' % (src_dir, dest_dir)
print 'Run translate.py and minify.sh first'
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if in_ignore(root,file): #ignore data and logs
            continue
        is_new = False
        # Check source code only
        if file.endswith('.php') or file.endswith('.txt') or file.endswith('.apk') or file.endswith('.html') or file.endswith('.css') or file.endswith('.js') or file.endswith('.png') or file.endswith('.gif') or file.endswith('.jpg') or file.endswith('.svg') or file.endswith('.htc') or file.endswith('.py') or file=='.htaccess' or root.startswith(src_dir+'/cgi-bin/pytz/zoneinfo'):
            f_from = open('%s/%s'%(root,file),'r')
            try:
                f_to = open('%s/%s'%(root.replace(src_dir+'/',dest_dir+'/'),file),'r')
            except IOError:
                # Cannot open destination file => this is a new file
                print '+  %s/%s'%(root,file)
                if instantiate_new:
                    f_to = open_mkdir('%s/%s'%(root.replace('wamp/',dest_dir+'/'),file),'w')
                    is_new = True
                else:
                    f_from.close()
                    continue
            c_from = f_from.read()
            modified=False
            
            # Perform the replacments
            if file.endswith('.php'):
                if src_dir in ('wamp','lamp-test') and dest_dir=='lamp-prod':
                    if c_from.find('http://localhost')>-1:
                        modified=True
                        c_from = c_from.replace('http://localhost','http://regepe.com')
                    if c_from.find('.js"')>-1:
                        modified=True
                        c_from = c_from.replace('.js"','.min.js"')
                elif src_dir=='lamp-prod' and dest_dir in ('wamp','lamp-test'):
                    if c_from.find('http://regepe.com')>-1:
                        modified=True
                        c_from = c_from.replace('http://regepe.com','http://localhost')
                    if c_from.find('.min.js"')>-1:
                        modified=True
                        c_from = c_from.replace('.min.js"','.js"')
                for k,v in keysnpwds.iteritems():
                    try:
                        c_from = c_from.replace(k,v)
                    except UnicodeDecodeError,e:
                        print k,v,file,root
                        raise e
            elif file.endswith('.js'):
                if src_dir in ('wamp','lamp-test') and dest_dir=='lamp-prod':
                    if c_from.find('${GeoPortalApiKey}')>-1:
                        modified=True
                        c_from = c_from.replace('${GeoPortalApiKey}','${GeoPortalApiKeyProd}')
                elif src_dir=='lamp-prod' and dest_dir in ('wamp','lamp-test'):
                    if c_from.find('${GeoPortalApiKeyProd}')>-1:
                        modified=True
                        c_from = c_from.replace('${GeoPortalApiKeyProd}','${GeoPortalApiKey}')
                for k,v in keysnpwds.iteritems():
                    try:
                        c_from = c_from.replace(k,v)
                    except UnicodeDecodeError,e:
                        print k,v,file,root
                        raise e
            elif file=='config.py':
                if src_dir in ('wamp','lamp-test') and dest_dir=='lamp-prod':
                    if c_from.find("domain = 'localhost'")>-1:
                        modified=True
                        c_from = c_from.replace("domain = 'localhost'","domain = 'regepe.com'")
                elif src_dir=='lamp-prod' and dest_dir in ('wamp','lamp-test'):
                    if c_from.find("domain = 'regepe.com'")>-1:
                        modified=True
                        c_from = c_from.replace("domain = 'regepe.com'","domain = 'localhost'")
            elif file.endswith('.py'):
                if src_dir=='wamp' and dest_dir in ('lamp-test','lamp-prod'):
                    if c_from.find('#!c:/Python27/python.exe')>-1:
                        modified=True
                        c_from = c_from.replace('#!c:/Python27/python.exe','#!/usr/bin/python')
                        c_from = c_from.replace(pythonwindowsbinarypostcgistuff,'#pythonwindowsbinarypostcgistuff\n')
                elif src_dir in ('lamp-test','lamp-prod') and dest_dir=='wamp':
                    if c_from.find('#!/usr/bin/python')>-1:
                        modified=True
                        c_from = c_from.replace('#!/usr/bin/python','#!c:/Python27/python.exe')
                        c_from = c_from.replace('#pythonwindowsbinarypostcgistuff\n',pythonwindowsbinarypostcgistuff)
            
            f_from.close()
            if instantiate_new and is_new:
                f_to.write(c_from)
            else:
                c_to = f_to.read()
            f_to.close()
            
            # Compare files
            if not is_new and c_from!=c_to:
                if modified:
                    # Files differs and modification has been done by realign.py
                    print 'D! %s/%s'%(root,file)
                else:
                    # Files differs and no modification was done by realign.py
                    print 'D  %s/%s'%(root,file)
        else:
            # Don't know how to handle this file!
            print '!!! %s %s' % (root,file)
