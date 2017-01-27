from config import config
import os
from log import Warn,Log

HOST = 'localhost'

def sendmailold(email,subject,body):
    server = smtplib.SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmail('info@%s'%config['domain'], email, 'Subject: %s\n\n%s'%(subject,body))
    server.quit()

def sendmail(email,subject,body):
    Log('sendmail to %s'%email)
    from_addr = 'info@%s' % config['domain']
    cmd = 'echo "From: %s\nTo: %s\nSubject: %s\n\n%s" | /usr/sbin/sendmail -t' % (from_addr,email, subject, body)
    try:
        retv = os.system(cmd.encode('utf8'))
        Log('sendmail retv=%d'%retv)
    except Exception, err:
        Warn('sendmail error: %s'%err)
