#!c:/Python27/python.exe

import cgi

from users import SendActivationMail,ReserveUser,ActivateUser,Login

def DoRegisterCgi():
    input = cgi.FieldStorage()
    mail = input.getvalue('mail').lower()
    user = input.getvalue('user').lower()
    password = input.getvalue('password')
    activation_id = ReserveUser(user,mail,password)
    #SendActivationMail(mail,user,activation_id)
    ActivateUser(user,activation_id)
    (user,sessid) = Login(user,password)
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
	DoRegisterCgi()
except Exception, inst:
	print('<result><user>NoUser</user><sess>-1</sess><error>%s</error></result>' % str(inst))
