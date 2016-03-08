#!c:/Python27/python.exe

import cgi
from db import DbPutWithoutPassword

print('Content-Type: text/html')
print
form = cgi.FieldStorage()
mapid = form.getvalue('mapid')
ele = form.getvalue('ele')
val = form.getvalue('val')
print '<p>mapid=+%s+<br/>ele=+%s+<br/>val=+%s+<br/></p>' % (mapid,ele,val)
DbPutWithoutPassword(mapid,ele,val)
print '<p>Done</p>'
