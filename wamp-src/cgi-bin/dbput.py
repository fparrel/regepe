#!c:/Python27/python.exe

import cgi

from db import DbPut,DbPutWithoutPassword,DbGet
from users import CheckSession

def DbPutCgi():
    form = cgi.FieldStorage()
    mapid = form.getvalue('id')
    pwd = form.getvalue('pwd')
    ele = form.getvalue('ele')
    val = form.getvalue('val')
    try:
        if form.has_key('user') and form.has_key('sess'):
            user = form.getvalue('user')
            sess = form.getvalue('sess')
            if CheckSession(user,sess):
                map_user = DbGet(mapid,'trackuser')
                if len(map_user)>0 and map_user==user:
                    DbPutWithoutPassword(mapid,ele,val)
                    message = 'OK'
                else:
                    raise Exception('Map %s does not belong to user %s, but to user %s' % (mapid,user,map_user))
            else:
                raise Exception('Invalid session, please re-login')
        else:
            DbPut(mapid,pwd,ele,val)
            message = 'OK'
    except Exception, e:
        message = 'Error: ' + str(e)
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
	DbPutCgi()
except Exception, inst:
	print('Error: ' + str(inst))
