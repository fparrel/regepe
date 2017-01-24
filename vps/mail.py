from config import config
import os

HOST = 'localhost'

def sendmailold(email,subject,body):
    server = smtplib.SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmail('info@%s'%config['domain'], email, 'Subject: %s\n\n%s'%(subject,body))
    server.quit()

def sendmail(email,subject,body):
    from_addr = 'info@%s' % config['domain']
    cmd = 'echo "From: %s\nTo: %s\nSubject: %s\n\n%s" | /usr/sbin/sendmail -t' % (from_addr,email, subject, body)
    try:
        os.system(cmd)
    except Exception, err:
        print "<br /> An error: %s" %err
