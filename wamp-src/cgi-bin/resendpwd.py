#!c:/Python27/python.exe

import cgi

from users import GetUserFromUserOrEmail,SendForgotPasswordMail

def CheckHumain(humaincheck):
    return ((humaincheck.strip().lower()=='earth')or(humaincheck.strip().lower()=='the earth'))

def DoResendPasswordCgi():
    input = cgi.FieldStorage()
    user_mail = input.getvalue('user_mail').lower()
    humaincheck = input.getvalue('humaincheck')
    if not CheckHumain(humaincheck):
        raise Exception('Humain check error')
    user = GetUserFromUserOrEmail(user_mail)
    mail = SendForgotPasswordMail(user)
    print('<P>A password reminder mail has been sent to %s</P>' % mail)
    print('<P><a href="../">Back</a></P>')


print('Content-Type: text/html')
print
try:
	DoResendPasswordCgi()
except Exception, inst:
	print('Error: ' + str(inst))
