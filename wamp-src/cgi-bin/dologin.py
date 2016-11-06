#!c:/Python27/python.exe

import cgi
import traceback

from users import Login
from log import Warn

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
except Exception, e:
    print('<result><user>NoUser</user><sess>-1</sess><error>%s</error></result>' % e)
    Warn('Error with login %s %s\n'%(e,traceback.format_exc()))
