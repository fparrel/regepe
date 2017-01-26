import os
import shutil

if not os.path.isdir('data'):
    os.mkdir('data')
if not os.path.isdir('data/backup'):
    os.mkdir('data/backup')

def Backup(mapid):
    shutil.copy2('data/mapdata/%s.json.gz'%mapid,'data/backup/%s.json.gz'%mapid)
    shutil.copy2('data/maps/%s.db'%mapid,'data/backup/%s.db'%mapid)
