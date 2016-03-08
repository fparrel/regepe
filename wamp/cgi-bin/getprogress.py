#!c:/Python27/python.exe

import cgi

from progress import GetProgress


print('Content-Type: text/html')
print
input = cgi.FieldStorage()
if not input.has_key('submitid'):
    print('Error: you must provide a submitid')
else:
    submitid = input.getvalue('submitid')
    try:
        progress = GetProgress(submitid)
        print(progress)
    except Exception, e:
        print('Error: ' + str(e))
