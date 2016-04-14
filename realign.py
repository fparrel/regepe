#!/usr/bin/python

import os
import sys
import json
import difflib
import stat

def diff(old,new):
    """
    To compute differences between two files. Diffs are filtered through is_expected_diff()
    
    @param old Contents of old file
    @param new Contents of new file
    
    @return A string representation of the diff (to be displayed with a Monospaced font). Empty string is returned if no diffs are found (or if all diffs can be ignored)
    """
    linesold = old.split('\n')
    linesnew = new.split('\n')
    s = difflib.SequenceMatcher(isjunk=lambda x: x in(" ","\t"),a=linesold,b=linesnew,autojunk=False)
    #s = difflib.SequenceMatcher(a=linesold,b=linesnew)
    for opcode,a1,a2,b1,b2 in s.get_opcodes():
        if opcode=='equal':
            pass
        #elif opcode=='replace' and is_expected_diff(opcode,linesold[a1:a2],linesnew[b1:b2]):
        #    pass
        else:
            yield (opcode,linesold[a1:a2],linesnew[b1:b2])

def format_diff(opcode,linesold,linesnew):
    """
    To print a diff
    @param opcode Kind of diff: 'replace', 'delete', 'insert'
    @param linesold Array containing the old lines
    @param linesnew Array containging the new lines
    
    @return A string that represent the diff (to be displayed with a Monospaced font)
    """
    if opcode=='replace':
        return ''.join(map(lambda line:'- %s'%line,linesold)+['\n']+map(lambda line:'+ %s'%line,linesnew))
    elif opcode=='delete':
        return ''.join(map(lambda line:'- %s'%line,linesold))
    elif opcode=='insert':
        return ''.join(map(lambda line:'+ %s'%line,linesnew))
    else:
        raise Exception("Unknow opcode for diff: %s"%opcode)

def get_diffs(old,new):
    return '\n'.join(map(lambda p: format_diff(p[0],p[1],p[2]),diff(old,new)))

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
    # submitted gpx files
    if root==src_dir+'/cgi-bin/submit':
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
    #if file.startswith('maintenance') and root.startswith(src_dir+'/www'):
    #    return True
    # temporary files on cgi
    if root==src_dir+'/cgi-bin/tmp':
        return True
    return False

def open_mkdir(fname,row):
    path = os.path.dirname(fname)
    #print 'path='+path
    if not os.path.exists(path):
        #print 'mkdir -p '+path
        os.makedirs(path)
    return open(fname,row)

src_dir = 'wamp-src'
dest_dir = 'lamp-prod'
overwrite = False
showdiffs = False

for arg in sys.argv[1:]:
    if arg in ('-h','--help'):
        print 'Usage: realign.py [-f] [-d|--diff][--src=wamp-src|wamp-test|lamp-test|lamp-prod] [--dst=wamp-src|wamp-test|lamp-test|lamp-prod]'
        print '-f: overwrite destination. By default, only show files that are in diff'
        print 'Default source is %s and default destination is %s' % (src_dir,dest_dir)
        exit(0)
    elif arg=='-f':
        overwrite = True
    elif arg in ('-d','--diff'):
        showdiffs = True
    elif arg.startswith('--src='):
        src_dir = arg[6:]
        assert(src_dir in ('wamp-src','wamp-test','lamp-test','lamp-prod'))
    elif arg.startswith('--dst='):
        dest_dir = arg[6:]
        assert(dest_dir in ('wamp-src','wamp-test','lamp-test','lamp-prod'))
    elif arg.startswith('--dest='):
        dest_dir = arg[7:]
        assert(dest_dir in ('wamp-src','wamp-test','lamp-test','lamp-prod'))

pythonwindowsbinarypostcgistuff = '''try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass
'''

if dest_dir in ('lamp-prod'):
    keysnpwds = json.load(open('keysnpwds-prod.json','r'))
elif dest_dir in ('lamp-test','wamp-test'):
    keysnpwds = json.load(open('keysnpwds-test.json','r'))
elif dest_dir=='wamp-src':
    if src_dir in ('lamp-test','wamp-test'):
        keysnpwds = json.load(open('keysnpwds-test.json','r'))
    elif src_dir=='lamp-prod':
        keysnpwds = json.load(open('keysnpwds-prod.json','r'))
    else:
        raise Exception('if source==wamp-src, dest must be wamp-test, lamp-test or lamp-prod')
    # Invert dict ( K:v -> v: k )
    keysnpwds = dict((v, k) for k, v in keysnpwds.iteritems())
else:
    raise Exception('if sdest must be wamp-src, wamp-test, lamp-test or lamp-prod')

print 'Source=%s Destination=%s' % (src_dir, dest_dir)
print 'Run translate.py and minify.sh first'

if not os.path.exists('%s/www/previews' % dest_dir):
    os.mkdir('%s/www/previews' % dest_dir)
    os.chmod('%s/www/previews' % dest_dir,stat.S_IWOTH)

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
                is_new = True
                if not overwrite:
                    f_from.close()
                    continue
            c_from = f_from.read()
            modified=False
            
            # Perform the replacments
            if file.endswith('.php'):
                if src_dir in ('wamp-src','wamp-test','lamp-test') and dest_dir=='lamp-prod':
                    if c_from.find('http://localhost')>-1:
                        modified=True
                        c_from = c_from.replace('http://localhost','http://regepe.com')
                    if c_from.find('.js"')>-1:
                        modified=True
                        c_from = c_from.replace('.js"','.min.js"')
                elif src_dir=='lamp-prod' and dest_dir in ('wamp-src','wamp-test','lamp-test'):
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
                for k,v in keysnpwds.iteritems():
                    try:
                        c_from = c_from.replace(k,v)
                    except UnicodeDecodeError,e:
                        print k,v,file,root
                        raise e
            elif file=='config.py':
                if src_dir in ('wamp-src','wamp-test','lamp-test') and dest_dir=='lamp-prod':
                    if c_from.find("domain = 'localhost'")>-1:
                        modified=True
                        c_from = c_from.replace("domain = 'localhost'","domain = 'regepe.com'")
                elif src_dir=='lamp-prod' and dest_dir in ('wamp-src','wamp-test','lamp-test'):
                    if c_from.find("domain = 'regepe.com'")>-1:
                        modified=True
                        c_from = c_from.replace("domain = 'regepe.com'","domain = 'localhost'")
            elif file.endswith('.py'):
                beginenc = c_from.find('-*- coding:')
                if beginenc>-1:
                    endenc=c_from.find('-*-',beginenc+len('-*- coding:'))
                    encoding = c_from[beginenc+len('-*- coding:'):endenc].strip()
                    print 'encoding "%s"'%encoding
                    c_from = c_from.decode(encoding)
                else:
                    encoding = None
                if src_dir in ('wamp-src','wamp-test') and dest_dir in ('lamp-test','lamp-prod'):
                    if c_from.find('#!c:/Python27/python.exe')>-1:
                        modified=True
                        c_from = c_from.replace('#!c:/Python27/python.exe','#!/usr/bin/python')
                        c_from = c_from.replace(pythonwindowsbinarypostcgistuff,'#pythonwindowsbinarypostcgistuff\n')
                elif src_dir in ('lamp-test','lamp-prod') and dest_dir in ('wamp-src','wamp-test'):
                    if c_from.find('#!/usr/bin/python')>-1:
                        modified=True
                        c_from = c_from.replace('#!/usr/bin/python','#!c:/Python27/python.exe')
                        c_from = c_from.replace('#pythonwindowsbinarypostcgistuff\n',pythonwindowsbinarypostcgistuff)
                for k,v in keysnpwds.iteritems():
                    try:
                        c_from = c_from.replace(k,v)
                    except UnicodeDecodeError,e:
                        print k,v,file,root
                        raise e
            
            f_from.close()
            if not is_new:
                c_to = f_to.read()
                f_to.close()
            if overwrite and (is_new or c_from!=c_to):
                f_to = open_mkdir('%s/%s'%(root.replace(src_dir+'/',dest_dir+'/'),file),'w')
                if encoding==None:
                    f_to.write(c_from)
                else:
                    f_to.write(c_from.encode(encoding))
                f_to.close()
            
            # Compare files
            if not is_new and c_from!=c_to:
                if modified:
                    # Files differs and modification has been done by realign.py
                    print 'D! %s/%s'%(root,file)
                    if showdiffs:
                        print get_diffs(c_from,c_to)
                else:
                    # Files differs and no modification was done by realign.py
                    print 'D  %s/%s'%(root,file)
                    if showdiffs:
                        print get_diffs(c_from,c_to)
        else:
            # Don't know how to handle this file!
            print '!!! %s %s' % (root,file)
