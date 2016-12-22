import datetime
import sys

def open_mkdir(fname,row):
    try:
        return open(fname,row)
    except:
        import os
        # If error, check directory, then create if needed then open file
        path = os.path.dirname(fname)
        #print 'path='+path
        if not os.path.exists(path):
            #print 'mkdir -p '+path
            os.makedirs(path)
        return open(fname,row)

def Log(s,uid=""):
    sys.stderr.write('Log: %s\n'%s)
    f = open_mkdir('logs/log.log','a')
    f.write('[%s] %14s %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),uid,s))
    f.close()

def Warn(s,uid=""):
    f = open_mkdir('logs/warn.log','a')
    f.write('[%s] %14s %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),uid,s))
    f.close()
