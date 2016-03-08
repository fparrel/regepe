#!c:/Python27/python.exe

import cgi
import traceback
from options import options
from orchestrator import BuildMap2
from config import maps_root
from progress import TestPolling  #debug
from cgiparser import FormGetFile,FormParseOptions,FormParseInt,FormParseStr
from users import CheckSession
import os,sys
from log import Log

try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass

def CheckSubmitId(submit_id):
    return submit_id.isalnum()

success = {'en':'Map successfully built\n</p><p><a href="/showmap.php?mapid=%s">Goto my map</a></p></body></html>',
    'fr':'Carte construite\n</p><p><a href="/fr/showmap.php?mapid=%s">Voir la carte</a></p></body></html>'}

def SendGpxFileCgi():
    Log('SendGpxFileCgi: FieldStorage\n')
    form = cgi.FieldStorage()
    Log('SendGpxFileCgi: parse\n')
    if form.has_key('lang'):
        lang = form.getvalue('lang')
    else:
        lang = 'en'
    inputfile = []
    if form.has_key('gpx_file[]'):
        # if 'gpx_file[]' has attribute file -> one element
        if hasattr(form['gpx_file[]'],'file'):
            form['gpx_file[]'].file.seek(0, os.SEEK_END)
            if form['gpx_file[]'].file.tell()!=0:
                form['gpx_file[]'].file.seek(0,0)
                inputfile.append(form['gpx_file[]'].file)
        # else it is a list
        else:
            for gpx_file in form['gpx_file[]']:
                inputfile.append(gpx_file.file)
    if form.has_key('fromurl'):
        fromurl = FormParseStr(form,'fromurl')
        if len(fromurl)>0:
            inputfile.append(fromurl)
    if len(inputfile)<1:
        raise Exception('Error while uploading file')
    FormParseOptions(form,options)
    if options['flat']:
        options['usedem'] = False
    if form.has_key('trk_select'):
        trk_id = FormParseInt(form,'trk_select')
    else:
        trk_id = 0
    trk_seg_id = 0
    submit_id = FormParseStr(form,'submit_id')
    if not CheckSubmitId(submit_id):
        raise Exception('Bad submit_id')
    desc = FormParseStr(form,'desc')
    if desc=='':
        desc = 'None'
    # Check user
    Log('SendGpxFileCgi: Check user\n')
    user = FormParseStr(form,'user')
    if user=='NoUser':
        user = 'unknown'
    else:
        sess = FormParseStr(form,'sess')
        if not CheckSession(user,sess):
            user = 'unknown'
    mapoutfilename = '%s/%s.php' % (maps_root,submit_id)
    Log('SendGpxFileCgi: BuildMap2\n')
    cptr = 0
    for fin in inputfile:
        try:
            fout = open("submit/%s_%d.gpx"%(submit_id,cptr),"w")
            fout.write(fin.read())
            fin.seek(0)
            fout.close()
        except:
            pass
        cptr+=1
    pwd = BuildMap2(inputfile,mapoutfilename,trk_id,trk_seg_id,submit_id,desc,user)
    Log('SendGpxFileCgi: end\n')
    if lang!='en':
        langpath = '%s/'%lang
    else:
        langpath = ''
    print(success[lang] % submit_id)
    print('''<script type="text/javascript">
    var date = new Date();
    date.setTime(date.getTime()+(10*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
    document.cookie = "pwd%s=%s"+expires+"; path=/";
    location.href=\'/%sshowmap-flot.php?mapid=%s\';
    </script>''' % (submit_id,pwd,langpath,submit_id))


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
    print('<html><head></head><body><p>')
    SendGpxFileCgi()
except Exception, inst:
    print('<b>Error:</b> ' + str(inst))
    print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())

