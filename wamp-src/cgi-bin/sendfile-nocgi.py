#!c:/Python27/python.exe

import traceback
from options import options
from orchestrator import BuildMap2
from config import maps_root
from progress import TestPolling  #debug
import os,sys
from log import Log

def CheckSubmitId(submit_id):
    return submit_id.isalnum()

success = {'en':'Map successfully built\n</p><p><a href="/showmap.php?mapid=%s">Goto my map</a></p></body></html>',
    'fr':'Carte construite\n</p><p><a href="/fr/showmap.php?mapid=%s">Voir la carte</a></p></body></html>'}

def SendFile(inputfile,options,submit_id,desc,user='unknwow',trk_id=0,fromurl='',lang='en'):
    Log('SendFile: parse\n')
    if len(inputfile)<1:
        raise Exception('Error while uploading file')
    if options['flat']:
        options['usedem'] = False
    trk_seg_id = 0
    if not CheckSubmitId(submit_id):
        raise Exception('Bad submit_id')
    # Check user
    Log('SendGpxFileCgi: Check user\n')
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


