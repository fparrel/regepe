#!c:/Python27/python.exe

import cgi
import os
import traceback
from mapparser import ParseMap
from model import Track
from orchestrator import ProcessTrkSegWithProgress
from db import DbChkPwd,DbPut,DbGet,DbPutWithoutPassword
from config import maps_root
from cgiparser import FormParseInt,FormParseStr
from users import CheckSession
from log import Log
from backup import Backup

notyourmap = {'en':'Map %s does not belong to user %s, but to user %s',
    'fr':'La trace %s n\'appartient pas &agrave; l\'utilisateur %s, mais &agrave; l\'utilisateur %s'}

invalidsession = {'en':'Invalid session, please re-login',
    'fr':'Session expir&eacute;e, merci de vous re-connecter'}

nocookie = {'en':"You do not have the map's password in your browser's cookies",
    'fr':'Vous n\'avez pas le mot de passe de cette trace dans vos cookies'}

success = {'en':'Done</p>\n<p><a href="/showmap.php?mapid=%s">Back to map</a></p></body></html>',
    'fr':'Fait</p>\n<p><a href="/showmap.php?mapid=%s">Retourner &agrave; la trace</a></p></body></html>'}

def CutMapCgi():
    # Get input args
    form = cgi.FieldStorage()
    if form.has_key('lang'):
        lang = form.getvalue('lang')
    else:
        lang = 'en'
    mapid = FormParseStr(form,'mapid')
    pwd = FormParseStr(form,'pwd')
    action = FormParseStr(form,'action')
    if form.has_key('type'):
        type = form.getvalue('type')
    else:
        type = None
    
    if((action=='clear')or(action=='crop')):
        firstptid = FormParseInt(form,'fisrtptid')
        lastptid = FormParseInt(form,'lastptid')
    elif(action=='delptlist'):
        delptlist = map(int,FormParseStr(form,'ptlist').split(','))
    
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
            return
    
    Log("CutMapCgi: parse map %s\n" % mapid)
    
    # Parse map
    if type==None:
        mapfname = '%s/%s.php' % (maps_root,mapid)
    else:
        mapfname = '%s/%s-%s.php' % (maps_root,mapid,type)
    if os.access(mapfname,os.F_OK):
        ptlist = ParseMap(mapfname,False)
    else:
        ptlist = ParseMap(mapfname+'.gz',True)
    
    # Perform action
    startpointchanged = False
    if (action=='clear'):
        ptlist = ptlist[:firstptid] + ptlist[lastptid:]
        if firstptid<1:
            startpointchanged = True
    elif (action=='crop'):
        ptlist = ptlist[firstptid:lastptid]
        if firstptid>0:
            startpointchanged = True
    elif (action=='delptlist'):
        for ptid in delptlist:
            if ptid==0:
                startpointchanged = True
            ptlist.pop(ptid)
    else:
        raise Exception('Invalid Action')
    
    Log("CutMapCgi: rebuild: Track %s\n" % mapid)
    
    # Rebuild map
    track = Track(ptlist)
    if type==None:
        mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    else:
        mapoutfilename = '%s/%s-%s.php' % (maps_root,mapid,type)
    
    Backup(mapid,type)
    
    Log("CutMapCgi: rebuild: ProcessTrkSegWithProgress %s\n" % mapid)
    if type==None:
        ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True)
    else:
        ProcessTrkSegWithProgress(track,mapoutfilename,mapid,light=True,type=type)
    
    # If start point has changed, then update the database
    if startpointchanged:
        DbPutWithoutPassword(mapid,'startpoint','%.4f,%.4f' % (track.ptlist[0].lat,track.ptlist[0].lon))
    # Recompute thumbnail
    previewfile = '%s/../previews/%s.png' % (maps_root,mapid)
    if os.access(previewfile,os.F_OK):
        os.remove(previewfile)
    
    Log("CutMapCgi: finished %s\n" % mapid)
    
    # Redirect to map
    print(success[lang] % mapid)
    if lang=='en':
        langpath = ''
    else:
        langpath = '%s/' % lang
    if type==None:
        print('<script type="text/javascript">location.href=\'/%sshowmap.php?mapid=%s\';</script>' % (langpath,mapid))
    else:
        print('<script type="text/javascript">location.href=\'/%sshowmap-flot.php?mapid=%s\';</script>' % (langpath,mapid))


print('Content-Type: text/html')
print
try:
    print('<html><head></head><body><p>')
    CutMapCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
