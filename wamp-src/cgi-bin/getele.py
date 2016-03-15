#!c:/Python27/python.exe

import cgi
from dem2 import GetEleFromLatLonList,GetEleFromLatLon

def DoGetEleCgi():
    input = cgi.FieldStorage()
    lat = float(input.getvalue('lat'))
    lon = float(input.getvalue('lon'))
    ele = GetEleFromLatLon(lat,lon)
    print '%s' % ele

print('Content-Type: text/html')
print
try:
	DoGetEleCgi()
except Exception, inst:
	print('Error: ' + str(inst))

