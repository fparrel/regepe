#!c:/Python27/python.exe

import cgi
import traceback
from db import DbGet

def DbGetCgi():
    form = cgi.FieldStorage()
    mapid = form.getvalue('id')
    ele = form.getvalue('ele')
    try:
        val = DbGet(mapid,ele)
        message = 'OK'
    except Exception, e:
        message = 'Error: ' + str(e)+'\n'+traceback.format_exc()
        val = 'Error'
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<answer>')
    print('<message>%s</message>' % message)
    print('<pageelementid>%s</pageelementid>' % ele)
    print('<value>%s</value>' % val)
    print('</answer>')


print('Content-Type: text/xml')
print
try:
	DbGetCgi()
except Exception, inst:
	print('Error: ' + str(inst))
	print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
