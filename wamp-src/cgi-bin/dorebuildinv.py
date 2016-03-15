#!c:/Python27/python.exe

import cgi
from datetime import datetime

import traceback
from db import DbRebuildAllIfNeeded

def RebuildAllInvCgi():
    f = open('logs/rebuildall.log','w')
    f.write(datetime.now().strftime('%Y/%m/%d %H:%M:%S\n'))
    for done in DbRebuildAllIfNeeded():
        print('Rebuild done for %s<br/>'%done)
        f.write('Rebuild %s\n'%done)
    print('Finished')
    f.write('Finished\n')
    f.close()

print('Content-Type: text/html')
print
try:
    print('<html><head><title>Rebuild all inv db</title></head><body><p>')
    RebuildAllInvCgi()
    print('</p></body></html>')
except Exception, inst:
	print('Error: ' + str(inst))
	print('</p><pre><small>%s</small></pre></body></html>' % traceback.format_exc())
