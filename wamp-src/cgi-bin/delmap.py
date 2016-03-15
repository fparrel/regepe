#!c:/Python27/python.exe

import cgi
import os
from db import DbChkPwd,DbDelMap,DbGet
from config import maps_root
from cgiparser import FormParseStr
from users import CheckSession


mapdeleted = {'en':'<p>Map deleted</p>\n<P><a href="../">Back to home</a></P>',
    'fr':'<p>Trace supprim&eacute;e</p>\n<P><a href="../fr/">Retour</a></P>'}

notyourmap = {'en':'Map %s does not belong to user %s, but to user %s',
    'fr':'La trace %s n\'appartient pas &agrave; l\'utilisateur %s, mais &agrave; l\'utilisateur %s'}

invalidsession = {'en':'Invalid session, please re-login',
    'fr':'Session expir&eacute;e, merci de vous re-connecter'}

nocookie = {'en':"You do not have the map's password in your browser's cookies",
    'fr':'Vous n\'avez pas le mot de passe de cette trace dans vos cookies'}

def DelMapCgi():
    # Get input args
    form = cgi.FieldStorage()
    if form.has_key('lang'):
        lang = form.getvalue('lang')
    else:
        lang = 'en'
    mapid = FormParseStr(form,'mapid')
    pwd = FormParseStr(form,'pwd')
    
    # Check rights
    if form.has_key('user') and form.has_key('sess'):
        user = form.getvalue('user')
        sess = form.getvalue('sess')
        if CheckSession(user,sess):
            map_user = DbGet(mapid,'trackuser')
            if len(map_user)>0 and map_user==user:
                pass
            else:
                raise Exception(notyourmap[lang] % (mapid,user,map_user))
        else:
            raise Exception(invalidsession[lang])
    else:
        if not DbChkPwd(mapid,pwd):
            raise Exception(nocookie[lang])
    
    # Delete map
    #print('DEBUG: Delete in db')
    DbDelMap(mapid)
    mapfile = '%s/%s.php' % (maps_root,mapid)
    #print('DEBUG: Delete in maps %s' % mapfile)
    if os.access(mapfile,os.F_OK):
        os.remove(mapfile)
    else:
        os.remove(mapfile+'.gz')
    print(mapdeleted[lang])


print('Content-Type: text/html')
print
try:
	DelMapCgi()
except Exception, inst:
    print('<P><b>Error:</b> %s' % str(inst))
    print('<P><a href="../">Back to home</a></P>')

