#!c:/Python27/python.exe

import cgi
from db import DbGet

def GetDescCgi():
	form = cgi.FieldStorage()
	mapid = form.getvalue('id')
	trackdesc = DbGet(mapid,'trackdesc')
	print trackdesc.replace('\n',' ')

print('Content-Type: text/html')
print
try:
	GetDescCgi()
except Exception, inst:
	print('Error: ' + str(inst))
