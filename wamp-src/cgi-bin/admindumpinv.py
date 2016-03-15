#!c:/Python27/python.exe
#coding=utf-8

from db import DumpDb,DbBuildWordList,DbGet
from textutils import remove_accents
import os,sys

print('Content-Type: text/html')
print

def DoDump():
    for dbname in ('TRACKDESC_INV.db','MAIL_INV.db','STARTPOINT_INV.db'):
        print('<p><b>Dump of %s</b><br/>' % (dbname))
        contents = DumpDb(dbname)
        for (k,v) in contents[1:]:
            print '%s: %s<br/>' % (k,v)
        print('</p>')

def TestRmAccent():
    print 'Test<br/>'
    for dbfile in os.listdir('maps'):
        if dbfile.endswith('.db'):
            desc = DbGet(dbfile[:-3],'trackdesc')
            print desc
            try:
                print remove_accents(desc,'utf-8')
            except Exception,inst:
                print str(inst)
            print 'hereA'
            #print unicodedata.normalize('NFKD', unicode(desc))
            #remove_accents(desc)

print('<html><head><title>admin</title></head><body>')
#print sys.getfilesystemencoding()
#DbBuildWordList('trackdesc')
DoDump()
#TestRmAccent()
print('</body></html>\n')
