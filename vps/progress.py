
import anydbm
import sys

def GetProgress(submitid):
    db = anydbm.open("data/PROGRESS.db", "c")
    if not db.has_key(submitid):
        raise Exception('Submitid unknow %s' % submitid)
    out = db[submitid]
    db.close()
    return out

def SetProgress(submitid,progress):
    sys.stderr.write('SetProgress(%s,%s)\n'%(submitid,progress))
    db = anydbm.open("data/PROGRESS.db", "c")
    db[submitid] = progress
    db.close()


## FOR TEST

from time import sleep

def TestPolling(submitid):
    SetProgress(submitid,'State=begin')
    for i in range(0,10):
        sleep(1)
        SetProgress(submitid,'State=%d'%i)
    SetProgress(submitid,'State=end')
    SetProgress(submitid,'Done')
    sleep(1)
    print('end of test')

def DumpProgress():
    db = anydbm.open("PROGRESS.db", "r")
    for k,v in db.iteritems():
        print('%s %s' % (k,v))
    db.close()    

def main():
    #SetProgress(1234,'In progress')
    #print(GetProgress(1234))
    DumpProgress()

if __name__ == '__main__':
   main()
