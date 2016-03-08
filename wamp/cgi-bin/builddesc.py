#!c:/Python27/python.exe

import cgi,os

from db import DbGet
from config import descriptions_root

def BuildDesc(mapid):
    trackdesc = DbGet(mapid,'trackdesc')
    #print '../desc/%s.txt %s'%(mapid,trackdesc)
    f = open('%s/%s.txt'%(descriptions_root,mapid),'wb')
    f.write(trackdesc)
    f.close()

def BuildDescCgi():
    form = cgi.FieldStorage()
    if form.has_key('id'):
        mapid_list = [form.getvalue('id')]
    else:
        mapid_list = []
        for fname in os.listdir('maps'):
            if fname.endswith('.db'):
                mapid_list.append(fname[:-3])
    for mapid in mapid_list:
        BuildDesc(mapid)
    print 'Done'


print('Content-Type: text/html')
print
try:
	BuildDescCgi()
except Exception, inst:
	print('Error: ' + str(inst))
