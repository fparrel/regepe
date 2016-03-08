#!c:/Python27/python.exe

import cgi

from users import SendActivationMail,ReserveUser

def CheckHumain(humaincheck):
    return ((humaincheck.strip().lower()=='terre')or(humaincheck.strip().lower()=='la terre'))

def DoRegisterCgi():
    input = cgi.FieldStorage()
    mail = input.getvalue('mail').lower()
    user = input.getvalue('user').lower()
    pwd1 = input.getvalue('pwd1')
    pwd2 = input.getvalue('pwd2')
    humaincheck = input.getvalue('humaincheck')
    if not CheckHumain(humaincheck):
        raise Exception('V&eacute;rifiez votre r&eacute;ponse &agrave; la question anti-robot')
    if pwd1!=pwd2:
        raise Exception('Les deux mots de passe sont diff&eacute;rents')
    activation_id = ReserveUser(user,mail,pwd1,lang='fr')
    SendActivationMail(mail,user,activation_id,lang='fr')
    print("<P>Un email d'activation a &eacute;t&eacute; envoy&eacute; &agrave; %s</P>" % mail)
    print('<P><a href="../">Retour</a></P>')


print('Content-Type: text/html')
print
try:
	DoRegisterCgi()
except Exception, inst:
	print('Erreur: ' + str(inst))
