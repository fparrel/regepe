#!c:/Python27/python.exe

import cgi

from users import Login

def DoLogin():
    input = cgi.FieldStorage()
    userormail = input.getvalue('user').lower()
    password = input.getvalue('password')
    (user,sessid) = Login(userormail,password)
    print('<result>')
    if user==None:
        print('<user>NoUser</user>')
        print('<sess>-1</sess>')
    else:
        print('<user>%s</user>' % user)
        print('<sess>%s</sess>' % sessid)
    print('</result>')


print('Content-Type: text/xml')
print
try:
	DoLogin()
except Exception, inst:
	print('<result><user>NoUser</user><sess>-1</sess><error>%s</error></result>' % str(inst))
