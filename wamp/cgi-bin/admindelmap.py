#!c:/Python27/python.exe

import cgi
import os
from db import DbDelMap
from config import maps_root

print('Content-Type: text/html')
print
form = cgi.FieldStorage()
mapid = form.getvalue('mapid')

DbDelMap(mapid)
mapfile = '%s/%s.php' % (maps_root,mapid)
if os.access(mapfile,os.F_OK):
    os.remove(mapfile)
else:
    os.remove(mapfile+'.gz')
print('<p>Map deleted</p>')
