
import gzip
import zlib
from config import maps_root
import os

def ChangeMapId(mapid,mapidnew):
    mapfname = '%s/%s-json.php.gz' % (maps_root,mapid)
    try:
        f = gzip.open(mapfname,'rb')
        contents = f.read()
    except:
        f = open(mapfname,'rb')
        contents = zlib.decompress(f.read())
    f.close()
    contentsnew = contents.replace('mapid = %s'%mapid,'mapid = %s'%mapidnew)
    mapfnamenew = '%s/%s-json.php.gz' % (maps_root,mapidnew)
    f = gzip.open(mapfnamenew,'wb')
    f.write(contentsnew)
    f.close()
    mapdbfname = 'maps/%s.db' % mapid
    f = open(mapdbfname,'rb')
    contents = f.read()
    f.close()
    mapdbfnamenew = 'maps/%s.db' % mapidnew    
    f = open('maps/%s.db' % mapidnew,'wb')
    f.write(contents)
    f.close()
    os.remove(mapfname)
    os.remove(mapdbfname)

ChangeMapId('5757e71ee0c29','5754aac6dd217')
