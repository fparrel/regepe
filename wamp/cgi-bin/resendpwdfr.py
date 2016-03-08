#!c:/Python27/python.exe

import cgi

from users import GetUserFromUserOrEmail,SendForgotPasswordMail

def CheckHumain(humaincheck):
    return ((humaincheck.strip().lower()=='terre')or(humaincheck.strip().lower()=='la terre'))

def DoResendPasswordCgi():
    input = cgi.FieldStorage()
    user_mail = input.getvalue('user_mail').lower()
    humaincheck = input.getvalue('humaincheck')
    if not CheckHumain(humaincheck):
        raise Exception('V&eacute;rifiez votre r&eacute;ponse &agrave; la question anti-robot')
    user = GetUserFromUserOrEmail(user_mail)
    mail = SendForgotPasswordMail(user,lang='fr')
    print('<P>Un email de rappel du mot de passe a &eacute;t&eacute; envoy&eacute; &agrave; %s</P>' % mail)
    print('<P><a href="../">Retour</a></P>')


print('Content-Type: text/html')
print
try:
	DoResendPasswordCgi()
except Exception, inst:
	print('Erreur: ' + str(inst))
