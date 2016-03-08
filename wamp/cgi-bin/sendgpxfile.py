#!c:/Python27/python.exe

import cgi
import traceback
from options import options
from orchestrator import BuildMap
from config import maps_root
#debug
from progress import TestPolling
from cgiparser import FormGetFile,FormParseOptions,FormParseInt,FormParseStr
from users import CheckSession
import os,sys

def SendGpxFileCgi():
    #print os.environ
    #print len(sys.stdin.read())
    form = cgi.FieldStorage()
    #print 'DEBUG: SendGpxFileCgi %s<br/>' % form
    inputfile = FormGetFile(form)
    if (inputfile==None):
        raise Exception('Error while submitting track file')
    FormParseOptions(form,options)
    if options['flat']:
        options['usedem'] = False
    if form.has_key('trk_select'):
        trk_id = FormParseInt(form,'trk_select')
    else:
        trk_id = 0
    trk_seg_id = 0
    submit_id = FormParseStr(form,'submit_id')
    desc = FormParseStr(form,'desc')
    if desc=='':
        desc = 'None'
    # Check user
    user = FormParseStr(form,'user')
    if user=='NoUser':
        user = 'unknown'
    else:
        sess = FormParseStr(form,'sess')
        if not CheckSession(user,sess):
            user = 'unknown'
    mapoutfilename = '%s/%s.php' % (maps_root,submit_id)
    print('<PRE>')
    pwd = BuildMap(inputfile,mapoutfilename,trk_id,trk_seg_id,submit_id,desc,user)
    print('Map successfully built')
    #TestPolling(submit_id)
    print('</PRE><BR/>')
    print('<A HREF="/showmap.php?mapid=%s">Goto my map</A><BR/>' % submit_id)
    #print('pwd=%s' % pwd)
    #expire = date.today().strfrime('%a, %d ')
    print('<script type="text/javascript">var date = new Date();date.setTime(date.getTime()+(10*24*60*60*1000));var expires = "; expires="+date.toGMTString();document.cookie = "pwd%s=%s"+expires+"; path=/";</script>' % (submit_id,pwd))
    #TestDispOtherParams(trk_id,trk_seg_id)
    #TestDispOptions(options)
    #TestDispFile(gpxfile)

def TestDispOtherParams(trk_id,trk_seg_id):
	print('trk_id=%d trk_seg_id=%d' % (trk_id,trk_seg_id))

def TestDispOptions(_options):
	print(_options)

def TestDispFile(gpxfile):
	linecount = 0
	while 1:
		line = gpxfile.readline()
		if not line: break
		linecount = linecount + 1
	print('gpx file has %d lines' % linecount)


print('Content-Type: text/html')
print
try:
	SendGpxFileCgi()
except Exception, inst:
    print('<B>Error:</B> ' + str(inst))
    print('<P><small>%s</small></P>' % traceback.format_exc())

