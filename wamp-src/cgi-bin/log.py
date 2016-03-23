import time

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

def Log(s):
    f = open_mkdir('logs/log.log','a')
    f.write('[%s] %s' % (time.time(),s))
    #f.write('[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S'),s))
    f.close()

def Warn(s):
    f = open_mkdir('logs/warn.log','a')
    f.write('[%s] %s' % (time.time(),s))
    f.close()
