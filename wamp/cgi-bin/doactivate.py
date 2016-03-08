#!c:/Python27/python.exe

import cgi

from users import ActivateUser

display = {'en':'<P>User %s has been created</P>\n<P><a href="../">Back</a></P>',
    'fr':'<P>Le compte utilisateur de %s a &eacute;t&eacute; cr&eacute;e</P>\n<P><a href="../">Retour</a></P>'}

def DoActivateCgi():
    input = cgi.FieldStorage()
    activationid = input.getvalue('activation_id')
    user = input.getvalue('user').lower()
    if input.has_key('lang'):
        lang = input.getvalue('lang')
    else:
        lang = 'en'
    ActivateUser(user,activationid)
    print(display[lang] % user)


print('Content-Type: text/html')
print
try:
	DoActivateCgi()
except Exception, inst:
	print('Error: ' + str(inst))
