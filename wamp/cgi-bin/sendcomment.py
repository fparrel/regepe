#!c:/Python27/python.exe

import cgi
import os

from db import DbAddComment,CheckValidMapId,CheckValidFreetext
from users import CheckSession,CheckValidUserName

def SendCommentCgi():
    remote_addr = cgi.escape(os.environ['REMOTE_ADDR'])
    form = cgi.FieldStorage()
    mapid = form.getvalue('mapid')
    comment = form.getvalue('comment')
    user = 'unknown'
    if form.has_key('user'):
        user = form.getvalue('user')
        if not CheckValidUserName(user):
            raise Exception('Invalid user name')
        sess = form.getvalue('sess')
        if CheckSession(user,sess):
            pass
        else:
            raise Exception('Invalid session, please re-login')
    else:
        user = remote_addr
    if not CheckValidMapId(mapid):
        raise Exception('Invalid map id')
    if not CheckValidFreetext(comment):
        raise Exception('Invalid map id')
    DbAddComment(mapid,user,comment)
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<result>OK</result>')


print('Content-Type: text/xml')
print
try:
	SendCommentCgi()
except Exception, inst:
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<result>%s</result>' % str(inst))
