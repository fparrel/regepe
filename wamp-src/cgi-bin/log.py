import time

def Log(s):
    f = open('logs/log.log','a')
    f.write('[%s] %s' % (time.time(),s))
    #f.write('[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S'),s))
    f.close()

def Warn(s):
    f = open('logs/warn.log','a')
    f.write('[%s] %s' % (time.time(),s))
    f.close()
