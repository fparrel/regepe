#!c:/Python27/python.exe

import cgi
import os
from db import DbChkPwd,DbDelMap,DbGet
from config import maps_root
from cgiparser import FormParseStr
from users import CheckSession


def DelMapCgi():
    # Get input args
    form = cgi.FieldStorage()
    mapids = FormParseStr(form,'mapids').split(',')
    for mapid in mapids:
        # Check rights
        if form.has_key('user') and form.has_key('sess'):
            user = form.getvalue('user')
            sess = form.getvalue('sess')
            if CheckSession(user,sess):
                map_user = DbGet(mapid,'trackuser')
                if len(map_user)>0 and map_user==user:
                    pass
                else:
                    raise Exception('Map %s does not belong to user %s, but to user %s' % (mapid,user,map_user))
            else:
                raise Exception('Invalid session, please re-login')
        
        # Delete map
        #print('DEBUG: Delete in db')
        DbDelMap(mapid)
        mapfile = '%s/%s.php' % (maps_root,mapid)
        #print('DEBUG: Delete in maps %s' % mapfile)
        if os.access(mapfile,os.F_OK):
            os.remove(mapfile)
        else:
            os.remove(mapfile+'.gz')
    print('<p>Maps deleted</p>')
    print('<P><a href="../">Back to home</a></P>')


print('Content-Type: text/html')
print
try:
	DelMapCgi()
except Exception, inst:
    print('<P><b>Error:</b> %s' % str(inst))
    print('<P><a href="../">Back to home</a></P>')

