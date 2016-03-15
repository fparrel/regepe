#!c:/Python27/python.exe

import cgi

from users import ChkAlreadyExists

def DoRegisterCgi():
    input = cgi.FieldStorage()
    mail = input.getvalue('mail').lower()
    user = input.getvalue('user').lower()
    print('<result>%s</result>' % ChkAlreadyExists(mail,user))


print('Content-Type: text/xml')
print
try:
	DoRegisterCgi()
except Exception, inst:
	print('Error: ' + str(inst))
