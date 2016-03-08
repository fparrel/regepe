from config import maps_root
import os
import shutil

def Backup(mapid,type):
    if type==None:
        mapfname = '%s/%s.php' % (maps_root,mapid)
    else:
        mapfname = '%s/%s-%s.php' % (maps_root,mapid,type)
    if not os.access(mapfname,os.F_OK):
        backupfname = mapfname+'.bak.gz'
        mapfname = mapfname+'.gz'
    else:
        backupfname = mapfname+'.bak'
    #print 'copy(%s,%s)'%(mapfname,backupfname)
    shutil.copy2(mapfname,backupfname)

if __name__=='__main__':
    Backup('5357dd0ae32ac',None)
    Backup('5357dd0ae32ac','json')
