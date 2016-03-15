#!c:/Python27/python.exe

import cgi

from users import SendActivationMail,ReserveUser

def CheckHumain(humaincheck):
    return ((humaincheck.strip().lower()=='earth')or(humaincheck.strip().lower()=='the earth'))

def DoRegisterCgi():
    input = cgi.FieldStorage()
    mail = input.getvalue('mail').lower()
    user = input.getvalue('user').lower()
    pwd1 = input.getvalue('pwd1')
    pwd2 = input.getvalue('pwd2')
    humaincheck = input.getvalue('humaincheck')
    if not CheckHumain(humaincheck):
        raise Exception('Humain check error')
    if pwd1!=pwd2:
        raise Exception('Password check error')
    activation_id = ReserveUser(user,mail,pwd1)
    SendActivationMail(mail,user,activation_id)
    print('<P>An activation mail has been sent to %s</P>' % mail)
    print('<P><a href="../">Back</a></P>')


print('Content-Type: text/html')
print
try:
	DoRegisterCgi()
except Exception, inst:
	print('Error: ' + str(inst))
