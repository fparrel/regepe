#!c:/Python27/python.exe

import cgi

from users import CheckSession

def DoCheckSession():
    input = cgi.FieldStorage()
    user = input.getvalue('user').lower()
    sess = input.getvalue('sess')
    ret = CheckSession(user,sess)
    if ret:
        result = 'OK'
    else:
        result = 'Expired'
    print('<answer><result>%s</result><user>%s</user><sess>%s</sess></answer>' % (result,user,sess))


print('Content-Type: text/xml')
print
try:
	DoCheckSession()
except Exception, inst:
	print('<answer><result>Error: %s</result><user>NoUser</user><sess>-1</sess></answer>' % str(inst))
