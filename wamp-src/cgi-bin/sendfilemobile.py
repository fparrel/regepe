#!c:/Python27/python.exe

import sys
import os
import urlparse
from generate_id import uniqid
from config import maps_root
from log import Log
from users import CheckSession
from orchestrator import BuildMap2
import traceback
from options import options

us2spdu = {'METRIC':'km/h','IMPERIAL':'mph','NAUTIC':'knots'}

def SendFileCgiMobile():
    Log('SendFileCgiMobile: begin\n')
    qs_dict = urlparse.parse_qs(os.environ['QUERY_STRING'])
    ip_addr = os.environ['REMOTE_ADDR']
    user = qs_dict['user'][0]
    sess = qs_dict['sess'][0]
    unitsystem = qs_dict['unit'][0]
    options['maxspd']=True
    if qs_dict.has_key('type'):
        if qs_dict['type'][0]=='nautic':
            options['flat']=True
            options['wind']=True
        elif qs_dict['type'][0]=='snowkite':
            options['flat']=False
            options['wind']=True
    options['spdunit'] = us2spdu[unitsystem]
    if user=='null':
        user = 'unknown'
        desc = 'Send from mobile app by %s' % ip_addr
    else:
        if not CheckSession(user,sess):
            raise Exception('Cannot identify user %s %s'%(user,sess))
        desc = 'Send from mobile app by %s' % user
    mapid = uniqid()
    Log('SendFileCgiMobile: u=%s s=%s m=%s d=%s\n' % (user,sess,mapid,desc))
    mapoutfilename = '%s/%s.php' % (maps_root,mapid)
    Log('SendFileCgiMobile: before BuildMap2')
    pwd = BuildMap2(sys.stdin,mapoutfilename,0,0,mapid,desc,user)
    Log('SendFileCgiMobile: after BuildMap2')
    print('"res":"success",')
    print('"mapid":"%s",'%mapid)
    print('"pwd":"%s"'%pwd)
    #while 1:
    #    line = sys.stdin.readline()
    #    if not line:
    #        break
    #    print line

def escape(s):
	return s.replace("\"","\\\"").replace("\n","\\n")

print('Content-Type: text/plain')
print
try:
    print('{')
    SendFileCgiMobile()
    print('}\n')
except Exception, inst:
    print('"error":"%s",' % escape(repr(inst)))
    print('"tb":"%s"' % escape(traceback.format_exc()))
    print('}\n')
