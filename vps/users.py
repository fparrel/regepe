import anydbm
import re
import os
from uuid import uuid4
from mail import sendmail
from db import RebuildNeeded,TriggerRebuildOfInv,DbBuildInvert,DumpDb
from config import domain

VALID_USERNAME_PATTERN = re.compile('^[a-z0-9_]+$')
VALID_EMAIL_PATTERN = re.compile('^[a-z0-9_A-Z\.]+@[a-z0-9_A-Z\.]+$')

def CheckValidUserName(user):
    return (VALID_USERNAME_PATTERN.match(user)!=None) and len(user)>0 and len(user)<20 and user.lower() not in ('nouser','unknown','anonymous')

def CheckValidPassword(pwd):
    return (len(pwd)>4 and len(pwd)<100)

def CheckValidEmail(email):
    return (VALID_EMAIL_PATTERN.match(email)!=None) and len(email)>4 and len(email)<100

subjects = {'en': 'ReGePe (Replay your GPS Tracks) account creation',
    'fr': 'Creation de compte ReGePe.com'}
bodies = {'en':  'Your accound will be created when you visit http://%s/activate/%s/%s',
    'fr': "Votre compte utilisateur sera cree si vous cliquez sur l'hyperlien suivant http://%s/activate/%s/%s&lang=fr"} #TODO

def SendActivationMail(mail,user,activation_id,lang='en'):
    subject = subjects[lang]
    body = bodies[lang] % (domain,user,activation_id)
    sendmail(mail,subject,body)

subjectsforgotpwd = {'en': 'ReGePe (Replay your GPS Tracks) forgoten password reminder',
    'fr': 'Rappel du mot de passe de compte ReGePe.com'}
bodiesforgotpwd = {'en':  'You receive this mail because someone, has requested a forgotten password reminder from %s.\nYour password is %s',
    'fr': "Vous recevez ce mail car quelqu'un a demande une reinitialisation de votre mot de passe depuis l'ip %s. Votre mot de passe est %s"}

def SendForgotPasswordMail(user,lang='en'):
    dbfile = 'data/users/%s.db' % user
    db = anydbm.open(dbfile, 'r')
    mail = db['mail']
    pwd = db['pwd']
    db.close()
    subject = subjectsforgotpwd[lang]
    body = bodiesforgotpwd[lang] % (domain,pwd)
    sendmail(mail,subject,body)
    return mail

def GetUserByEmail(mail):
    if RebuildNeeded('mail') or not os.access('data/MAIL_INV.db',os.F_OK):
        DbBuildInvert('users','mail',lambda value: [value])
    dbinv = anydbm.open('data/MAIL_INV.db','r')
    if dbinv.has_key(mail):
        value = dbinv[mail]
    else:
        value = None
    dbinv.close()
    return value

invalidusername = {'en':'Invalid user name "%s"',
    'fr':"Nom d'utilisateur non conforme: '%s'"}

passwordtooshort = {'en':'The password you have chosen is too short',
    'fr':'Le mot de passe choisi est trop court'}

passwordtoolong = {'en':'The password you have chosen is too long',
    'fr':'Le mot de passe choisi est trop long'}

invalidemail = {'en':'Invalid email "%s"',
    'fr':'Email non conforme: "%s"'}

useralreadyexists = {'en':'User %s already exists',
    'fr':'Le nom d\'utilisateur %s est d&eacute;j&agrave; utilis&eacute;'}

mailalreadyassociated = {'en':'Mail %s already associated with an user',
    'fr':'L\'email %s est d&eacute;j&agrave; associ&eacute; avec un utilisateur'}

def ReserveUser(user,mail,pwd,lang='en'):
    if not CheckValidUserName(user):
        raise Exception(invalidusername[lang] % user)
    if len(pwd)<5:
        raise Exception(passwordtooshort[lang])
    if len(pwd)>99:
        raise Exception(passwordtoolong[lang])
    if not CheckValidEmail(mail):
        raise Exception(invalidemail[lang] % mail)
    chk = ChkAlreadyExists(mail,user)
    if chk=='user':
        raise Exception(useralreadyexists[lang] % user)
    elif chk=='mail'!=None:
        raise Exception(mailalreadyassociated[lang] % mail)
    elif chk!='none':
        raise Exception('Problem with ChkAlreadyExists')
    dbfile = 'data/users/%s.db' % user
    activation_id = str(uuid4())
    db = anydbm.open(dbfile, 'c')
    db['activation_id'] = activation_id
    db['mail'] = mail
    db['pwd'] = pwd
    db.close()
    TriggerRebuildOfInv('mail')
    return activation_id

def ActivateUser(user,activationid):
    if not CheckValidUserName(user):
        raise Exception('Invalid user name "%s"' % user)
    dbfile = 'data/users/%s.db' % user
    if not os.access(dbfile,os.F_OK):
        raise Exception('User %s doesn\'t exists' % user)
    db = anydbm.open(dbfile, 'r')
    activation_id_from_db = db['activation_id']
    db.close()
    if (activation_id_from_db=='Active'):
        raise Exception('User "%s" already activated' % (user))
    if (activation_id_from_db!=activationid):
        raise Exception('Bad activation id "%s" for user "%s"' % (activationid,user))
    db = anydbm.open(dbfile, 'c')
    db['activation_id'] = 'Active'
    db.close()

def GetUserFromUserOrEmail(userormail):
    if not (CheckValidUserName(userormail) or CheckValidEmail(userormail)):
        raise Exception('Invalid user name or email')
    dbfile = 'data/users/%s.db' % userormail
    if os.access(dbfile,os.F_OK):
        user = userormail
    else:
        user = GetUserByEmail(userormail)
        if user==None:
            raise Exception('Cannot found user from email "%s"' % userormail)
    return user

MAX_NB_SESSIONS = 8

def Login(userormail,password):
    if not (CheckValidUserName(userormail) or CheckValidEmail(userormail)):
        raise Exception('Invalid user name or email')
    if not CheckValidPassword(password):
        raise Exception('Invalid password')
    dbfile = 'data/users/%s.db' % userormail
    if os.access(dbfile,os.F_OK):
        user = userormail
    else:
        user = GetUserByEmail(userormail)
        if user==None:
            raise Exception('Cannot found user from email "%s"' % userormail)
    dbfile = 'data/users/%s.db' % user
    if not os.access(dbfile,os.F_OK):
        raise Exception('Cannot found user "%s"' % user)
    db = anydbm.open(dbfile, 'r')
    pwd_from_db = db['pwd']
    activation_id_from_db = db['activation_id']
    db.close()
    if activation_id_from_db!='Active':
        raise Exception('User not activated')
    if pwd_from_db!=password:
        raise Exception('Bad password')
    session_id = str(uuid4())
    db = anydbm.open(dbfile, 'c')
    if not db.has_key('nb_sessions'):
        nb_sessions = 0
    else:
        nb_sessions = (int(db['nb_sessions'])+1)%MAX_NB_SESSIONS
    db['nb_sessions'] = str(nb_sessions)
    if nb_sessions==0:
        k='session_id'
    else:
        k='session_id%d'%nb_sessions
    db[k] = session_id
    db.close()
    return (user,session_id)

def CheckSession(user,session_id):
    if not CheckValidUserName(user):
        raise Exception('Invalid user name "%s"' % user)
    dbfile = 'data/users/%s.db' % user
    if not os.access(dbfile,os.F_OK):
        raise Exception('User %s doesn\'t exists' % user)
    db = anydbm.open(dbfile, 'r')
    for i in range(0,MAX_NB_SESSIONS):
        if i==0:
            k='session_id'
        else:
            k='session_id%d'%i
        if db.has_key(k):
            session_id_from_db = db[k]
            if (session_id_from_db==session_id):
                db.close()
                return True
    db.close()
    return False

def ChkAlreadyExists(mail,user):
    if not CheckValidUserName(user):
        raise Exception('Invalid user name "%s"' % user)
    if not CheckValidEmail(mail):
        raise Exception('Invalid email "%s"' % mail)
    dbfile = 'data/users/%s.db' % user
    if os.access(dbfile,os.F_OK):
        return 'user'
    if GetUserByEmail(mail)!=None:
        return 'mail'
    return 'none'

def DumpUser(user):
    dbfile = 'data/users/%s.db' % user
    db = anydbm.open(dbfile, 'r')
    if db.has_key('mail'):
        print 'mail=%s' % db['mail']
    if db.has_key('activation_id'):
        print 'activation_id=%s' % db['activation_id']
    for i in range(0,MAX_NB_SESSIONS):
        if i==0:
            k='session_id'
        else:
            k='session_id%d'%i
        if db.has_key(k):
            print '%s=%s' % (k,db[k])
    if db.has_key('nb_sessions'):
        print 'nb_sessions=%s'%(db['nb_sessions'])
    #if db.has_key('pwd'):
    #    print 'pwd=%s'%db['pwd']
    db.close()

## UNIT TESTS ##

def main():
    #GetUserByEmail('test')
    #DumpDb('MAIL_INV.db')
    #DumpUser('fredi')
    #return
    #print CheckValidUserName('fparrel_0')
    #actid = ReserveUser('fparrel2','mypassword')
    #print actid
    #ActivateUser('fparrel2',actid)
    (user,session_id) = Login('fparrel2','mypassword')
    (user,session_id2) = Login('fparrel2','mypassword')
    print CheckSession(user,session_id)
    print CheckSession(user,session_id2)
    print CheckSession(user,'lol')
    DumpUser('fparrel2')

if __name__=='__main__':
    main()
