#!c:/Python27/python.exe

import cgi
import hashlib
import dbhash
from xml.sax.saxutils import escape

from db import DbPutWithoutPassword
from log import Log

def DbSetMapEleCgi():
    form = cgi.FieldStorage()
    pwdhexvalue = '560ff0101be9750e804656afb15cf1e7ba1d252a'
    if not hashlib.sha1(form.getvalue('pwd')).hexdigest()==pwdhexvalue:
        print 'Error: bad password'
        return
    mapid = form.getvalue('mapid')
    ele = form.getvalue('ele')
    val = form.getvalue('val')
    DbPutWithoutPassword(mapid,ele,val)
    print 'OK'

print('Content-Type: text/plain')
print
try:
    DbSetMapEleCgi()
except Exception, inst:
    import traceback
    print('Error: ' + str(inst))
    print(traceback.format_exc())
