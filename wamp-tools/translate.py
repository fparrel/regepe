#!/usr/bin/python

# Launch me: ./wamp-tools/translate.py
# Check missing translations in diff.txt
# If needed add line to filter.txt
# Add translations in translations.txt
# Re-launch me
# Check diffs between wamp/www/fr and lamp/www/fr
# Retrofit diffs, upload and commit


import os,re

patstrlit = re.compile('"[^"]*"')
patstrlit2 = re.compile("'[^']*'")
pathtml = re.compile('>[^<]*<')

jsfilter = ['raphael-min.js',]
phpfilter = ['testraphael.php',]

def removeempty(l):
    out = []
    for i in l:
        if len(i.strip())>0:
            out.append(i)
    return out

def processfile(fname,pattern1,pattern2):
    out = []
    print 'Analyse %s'% fname
    f = open(fname,'r')
    for line in f:
        found = map(lambda fnd: fnd[1:-1].strip(),pattern1.findall(line)+pattern2.findall(line))
        found = removeempty(found)
        found = map(lambda fnd: '%s:%s'%(fname,fnd),found)
        out.extend(found)
    f.close()
    return out

def processjs(fname):
    return processfile(fname,patstrlit,patstrlit2)

def processhtml(fname):
    return processfile(fname,pathtml,patstrlit)

def processphp(fname):
    return processhtml(fname)

def processall():
    out = []
    for fname in os.listdir('wamp-src/www/javascript'):
        if fname not in jsfilter:
            out.extend(processjs('wamp-src/www/javascript/%s'%fname))
    for fname in os.listdir('wamp-src/www'):
        if fname.endswith('.html'):
            out.extend(processhtml('wamp-src/www/%s'%fname))
        elif fname.endswith('.php') and fname not in phpfilter:
            out.extend(processphp('wamp-src/www/%s'%fname))
    return out


def createdirifneeded(path):
    dirs=path.split('/')
    curdir=''
    for dir in dirs:
        curdir+='%s/'%dir
        #print curdir
        try:
            os.mkdir(curdir)
        except:
            pass

def copyfile(src,dst):
    print 'copy %s %s' % (src,dst)
    fsrc = open(src,'rb')
    fdst = open(dst,'wb')
    fdst.write(fsrc.read())
    fdst.close()
    fsrc.close()

def parseTranslations(csvfname,list=False):
    f = open(csvfname,'r')
    translations = {}
    out = []
    for line in f:
        try:
            (totrad,traduced)=line.split('\t')
            (fname,totradstr)=totrad.split(':',1)
            traducedstr=traduced[:-1]
        except:
            raise Exception('Cannot parse line %s'%line)
        if list:
            out.append('wamp-src/%s:%s'%(fname,totradstr))
        else:
            if not translations.has_key(fname):
                translations[fname] = []
            translations[fname].append((totradstr,traducedstr))
    f.close()
    if list:
        return out
    else:
        return translations

def buildtraduced(csvfname):
    translations = parseTranslations(csvfname)
    print translations
    createdirifneeded('wamp-src/www/fr/javascript')
    for fname in translations:
        print 'Process %s -> %s'%('wamp-src/' + fname,'wamp-src/' + fname.replace('www/','www/fr/'))
        fin = open('wamp-src/' + fname,'r')
        fout = open('wamp-src/' + fname.replace('www/','www/fr/'),'wb')
        contents = fin.read()
        cptr=0
        for (oldstr,newstr) in translations[fname]:
            contents = contents.replace(oldstr,newstr)
            cptr+=1
        print '%d replacments done'%cptr
        fout.write(contents)
        fout.close()
        fin.close()
    
    #files with no translation
    dirlist = ['www','www/javascript','www/images','www/styles','www/android']
    for path in dirlist:
        createdirifneeded('wamp-src/'+path.replace('www','www/fr'))
        for fname in os.listdir('wamp-src/'+path):
            if fname.endswith('.html') or fname.endswith('.js') or fname.endswith('.php') or fname.endswith('.png') or fname.endswith('.gif') or fname.endswith('.jpg') or fname.endswith('.svg') or fname.endswith('.htc') or fname.endswith('.css') or fname.endswith('.apk'):
                if '%s/%s'%(path,fname) not in translations:
                    copyfile('wamp-src/%s/%s'%(path,fname), 'wamp-src/%s/%s'%(path.replace('www','www/fr'),fname))

def dictToFile(d,cvsfname):
    f = open(cvsfname,'w')
    for fname in d:
        for (totranslate,translation) in d[fname]:
            f.write('%s:%s\t%s\n'%(fname,totranslate,translation))
    f.close()

def listtotraduce(cvsfname):
    f = open(cvsfname,'w')
    for item in processall():
        f.write('%s\n'%item)
    f.close()

def listToDict(l):
    translations = {}
    for i in l:
        (fname,totradstr)=i.split(':',1)
        if not translations.has_key(fname):
            translations[fname] = []
        translations[fname].append((totradstr,None))
    return translations

def dictToList(d):
    out = []
    for fname in d:
        for (totranslate,translation) in d[fname]:
            out.append('%s:%s\t%s'%(fname,totranslate,translation))
    return out

def main():
    print 'Launch me from ./wamp-tools/translate.py'
    totrans = listToDict(processall())
    translated = parseTranslations('wamp-tools/translations.txt')
    filter = parseTranslations('wamp-tools/filter.txt',list=True)
    #print totrans
    #print translated
    diff = {}
    for fname in totrans:
        item = []
        if translated.has_key(fname):
            for (totranslate,translation) in totrans[fname]:
                if '%s:%s' % (fname,totranslate) in filter:
                    continue
                if totranslate.strip():
                    found = False
                    #print translated[fname]
                    for (totranslate2,translation2) in translated[fname]:                    
                        if totranslate==totranslate2:
                            found = True
                            break
                    if not found:
                        item.append((totranslate,None))
            if len(item)>0:
                diff[fname] = item
        else:
            item = []
            for (totranslate,translation) in totrans[fname]:
                if '%s:%s' % (fname,totranslate) in filter:
                    continue
                item.append((totranslate,None))
            if len(item)>0:
                diff[fname] = item
    #print diff
    dictToFile(diff,'wamp-tools/diff.txt')
    buildtraduced('wamp-tools/translations.txt')
    #listtotraduce('totraduce2.csv')

if __name__=='__main__':
    main()

