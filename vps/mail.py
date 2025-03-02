from config import config
import os
from log import Warn,Log

HOST = 'localhost'

def sendmail(email,subject,body):
    Log('sendmail to %s'%email)
    from_addr = 'info@%s' % config['domain']
    cmd = 'echo "From: %s\nTo: %s\nSubject: %s\n\n%s" | /usr/sbin/sendmail -t' % (from_addr,email, subject, body)
    try:
        retv = os.system(cmd.encode('utf8'))
        Log('sendmail retv=%d'%retv)
    except Exception as err:
        Warn('sendmail error: %s'%err)
