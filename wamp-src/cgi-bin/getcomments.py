#!c:/Python27/python.exe

import cgi
from db import DbGetComments,CheckValidMapId

def GetCommentsCgi():
    form = cgi.FieldStorage()
    mapid = form.getvalue('mapid')
    if not CheckValidMapId(mapid):
        raise Exception('Invalid map id')
    comments = DbGetComments(mapid)
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<result>')
    for (date,user,comment) in comments:
        print('<comment user="%s" date="%s">%s</comment>' % (user,date,comment))
    print('</result>')


print('Content-Type: text/xml')
print
try:
	GetCommentsCgi()
except Exception, inst:
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<result>%s</result>' % str(inst))
