import anydbm
from wordspliter import SplitWords
from filelock import FileLock
from mydate import getCurrentDate
import os
import re
# i18n
from flask_babel import gettext

DBTYPES = ('users','maps')

ELELIST = {'maps':('trackdesc','trackuser','startpoint','date','winddir','demized'),'users':('mail',)}

if not os.path.isdir('data'):
	os.mkdir('data')
for dbtype in DBTYPES:
	path='data/%s'%dbtype
	if not os.path.isdir(path):
		os.mkdir(path)

def TriggerRebuildOfInv(ele):
    if os.access('data/.rebuilt'+ele,os.F_OK):
        try:
            os.rmdir('data/.rebuilt'+ele)
        except:
            pass

def RebuildNeeded(ele):
    return not os.access('data/.rebuilt'+ele,os.F_OK)

def RearmRebuild(ele):
    if not os.access('data/.rebuilt'+ele,os.F_OK):
        os.mkdir('data/.rebuilt'+ele)


def DbChkPwd(mapid,inputpwd):
    dbfile = 'data/maps/%s.db' % mapid
    db = anydbm.open(dbfile, 'r')
    rightpwd = db['pwd']
    ret = (inputpwd==rightpwd)
    db.close()
    return ret


def DbPutWithoutPassword(mapid,ele,val):
    # Check ele
    if ele not in ELELIST['maps']:
        raise Exception(gettext('Invalid element'))
    # Target map db
    dbfile = 'data/maps/%s.db' % mapid
    # Write value
    db = anydbm.open(dbfile, 'c')
    db[ele] = val
    db.close()
    # Trigger rebuild
    TriggerRebuildOfInv(ele)


def DbPut(mapid,pwd,ele,val):
    # Check ele
    if ele not in ELELIST['maps']:
        raise Exception(gettext('Invalid element'))
    # Target map db
    dbfile = 'data/maps/%s.db' % mapid
    # Check pwd
    db = anydbm.open(dbfile, 'r')
    rightpwd = db['pwd']
    db.close()
    if pwd != rightpwd:
        raise Exception(gettext('Bad password'))
    DbPutWithoutPassword(mapid,ele,val)


def DbGet(mapid,ele):
    # Check ele
    if ele not in ELELIST['maps']:
        raise Exception(gettext('Invalid element'))
    # Target map db
    dbfile = 'data/maps/%s.db' % mapid
    # Read value
    try:
        db = anydbm.open(dbfile, 'r')
    except Exception as e:
        raise Exception(gettext('Cannot open %s: %s') %(dbfile,e))
    try:
        value = db[ele]
    except KeyError:
        value = ''
    db.close()
    return value

def DbGetMulitple(mapid,elelst):
    # Target map db
    dbfile = 'data/maps/%s.db' % mapid
    # Read values
    try:
        db = anydbm.open(dbfile, 'r')
    except Exception as e:
        raise Exception(gettext('Cannot open %s: %s') %(dbfile,e))
    out = {}
    for ele in elelst:
        try:
            out[ele] = db[ele]
        except KeyError:
            out[ele] = ''
    db.close()
    return out

def DbSetPassword(mapid,pwd):
    # Target map db
    dbfile = 'data/maps/%s.db' % mapid
    # Write password
    try:
        db = anydbm.open(dbfile, 'c')
    except:
        import os
        os.mkdir('maps')
        db = anydbm.open(dbfile, 'c')
    db['pwd'] = pwd
    db.close()


def DbBuildWordList(ele):
    DbBuildInvert('maps',ele,lambda value: SplitWords(value.lower()))


def DbRebuildAllIfNeeded(force = [], verbose = False):
    if verbose:
        print('Rebuild all...')
    if RebuildNeeded('date') or 'date' in force:
        if verbose:
            print('Rebuild date...')
        DbBuildInvert('maps','date',lambda value: [value])
        yield('maps/date')
    if RebuildNeeded('trackdesc') or 'trackdesc' in force:
        if verbose:
            print('Rebuild desc...')
        DbBuildWordList('trackdesc')
        yield('maps/trackdesc')
    if RebuildNeeded('startpoint') or 'startpoint' in force:
        if verbose:
            print('Rebuild startpoint...')
        DbBuildInvert('maps','startpoint',lambda value: [value])
        yield('maps/startpoint')
    if RebuildNeeded('trackuser') or 'trackuser' in force:
        if verbose:
            print('Rebuild user...')
        DbBuildInvert('maps','trackuser',lambda value: [value])
        yield('maps/trackuser')

def DbSearchWord(ele,word):
    if RebuildNeeded(ele):
        DbBuildWordList(ele)
    # Check ele
    if ele not in ELELIST['maps']:
        raise Exception(gettext('Invalid element'))
    # Search
    dbinv = anydbm.open('data/'+ele.upper()+'_INV.db','r')
    if dbinv.has_key(word):
        out = dbinv[word].split(',')
    else:
        out = []
    dbinv.close()
    return out


def DbBuildInvert(dbtype,ele,invfunc):
    if dbtype not in DBTYPES:
        raise Exception(gettext('Invalid database type'))
    # Check ele
    if ele not in ELELIST[dbtype]:
        raise Exception(gettext('Invalid element'))
    # Target inv db
    dbfileinv = 'data/'+ele.upper()+'_INV.db'
    # Lock and open inv db
    lock = FileLock(dbfileinv,5)
    lock.acquire()
    dbinv = anydbm.open(dbfileinv,'n')
    # List dir
    for dbfile in os.listdir('data/'+dbtype):
        mapid = dbfile[:-3]
        db = anydbm.open('data/%s/%s' % (dbtype,dbfile),'r')
        if db.has_key(ele):
            value = db[ele]
            for word in invfunc(value):
                if dbinv.has_key(word):
                    dbinv[word] = dbinv[word] + (',%s' % mapid)
                else:
                    dbinv[word] = '%s' % mapid
        db.close()
    dbinv.close()
    lock.release()
    # Rebuild is no more needed
    RearmRebuild(ele)


def DbSearchLatLonRange(minlat,minlon,maxlat,maxlon):
    if RebuildNeeded('startpoint'):
        DbBuildInvert('maps','startpoint',lambda value: [value])
    dbinv = anydbm.open('data/STARTPOINT_INV.db','c')
    out = []
    for latlonstr,mapidsstr in dbinv.iteritems():
        (lat,lon) = map(float,latlonstr.split(','))
        mapids = []
        if minlat<=lat and maxlat>=lat and minlon<=lon and maxlon>=lon:
            mapids.extend(mapidsstr.split(','))
        if len(mapids)>0:
            out.append((lat,lon,mapids))
    dbinv.close()
    return out


def DbGetAllMaps():
    if RebuildNeeded('startpoint'):
        DbBuildInvert('maps','startpoint',lambda value: [value])
    dbinv = anydbm.open('data/STARTPOINT_INV.db','c')
    out = []
    for latlonstr,mapidsstr in dbinv.iteritems():
        (lat,lon) = map(float,latlonstr.split(','))
        out.append((lat,lon,mapidsstr.split(',')))
    dbinv.close()
    return out


def DbDelMap(mapid):
    dbfile = 'data/maps/%s.db' % mapid
    os.remove(dbfile)
    for ele in ELELIST['maps']:
        TriggerRebuildOfInv(ele)


def DbGetMapsOfUser(user):
    if RebuildNeeded('trackuser'):
        DbBuildInvert('maps','trackuser',lambda value: [value])
    dbinv = anydbm.open('data/TRACKUSER_INV.db','r')
    if not dbinv.has_key(user):
        return []
    out = dbinv[user].split(',')
    dbinv.close()
    return out


def DbGetListOfDates():
    if RebuildNeeded('date'):
        DbBuildInvert('maps','date',lambda value: [value])
    dbinv = anydbm.open('data/DATE_INV.db','c')
    out = {}
    for k,v in dbinv.iteritems():
        out[k] = v.split(',')
    dbinv.close()
    return out


def DbAddComment(mapid,user,comment):
    mapfile = 'data/maps/%s.db' % mapid
    if not os.access(mapfile,os.F_OK):
        raise Exception(gettext('Invalid map id %s') % mapid)
    d = getCurrentDate()
    lock = FileLock(mapfile,5)
    lock.acquire()
    db = anydbm.open(mapfile,'r')
    if db.has_key('last_comment_id'):
        last_comment_id = int(db['last_comment_id'])
    else:
        last_comment_id = 0
    db.close()
    last_comment_id += 1
    if last_comment_id>99999:
        lock.release()
        raise Exception(gettext('Max comments reached'))
    db = anydbm.open(mapfile,'c')
    db['last_comment_id'] = str(last_comment_id)
    db['comment%.5d'%last_comment_id] = '%s,%s,%s' % (d,user,comment)
    db.close()
    lock.release()

def DbGetComments(mapid):
    mapfile = 'data/maps/%s.db' % mapid
    if not os.access(mapfile,os.F_OK):
        raise Exception(gettext('Invalid map id %s') % mapid)
    db = anydbm.open(mapfile,'r')
    out = []
    for k in sorted(db):
        if k.startswith('comment'):
            out.append(db[k].split(',',2))
    db.close()
    return out

VALID_MAPID_PATTERN = re.compile('^[a-z0-9_]+$')

def CheckValidMapId(mapid):
    return (VALID_MAPID_PATTERN.match(mapid)!=None) and len(mapid)>0 and len(mapid)<20

def CheckValidFreetext(text):
    return len(text)>0 and len(text)<1024 and text.find('<')==-1 and text.find('>')==-1

def DbGetNearbyPoints(lati,loni):
    if RebuildNeeded('startpoint'):
        DbBuildInvert('maps','startpoint',lambda value: [value])
    dbinv = anydbm.open('data/STARTPOINT_INV.db','r')
    out_closest = {}
    out_farest = {}
    for latlonstr,mapidsstr in dbinv.iteritems():
        lat,lon = map(float,latlonstr.split(','))
        d = (lati - lat)*(lati - lat) + (loni - lon)*(loni - lon)
        if d < 0.02:
            if not out_closest.has_key(d):
                out_closest[d] = mapidsstr.split(',')
            else:
                out_closest[d].extend(mapidsstr.split(','))
        elif d < 1.0:
            if not out_farest.has_key(d):
                out_farest[d] = mapidsstr.split(',')
            else:
                out_farest[d].extend(mapidsstr.split(','))
    dbinv.close()
    out = []
    for i in sorted(out_closest)[:32]:
        out.extend(out_closest[i])
    if len(out)<16:
        for i in sorted(out_farest)[:16-len(out)]:
            out.extend(out_farest[i][:16-len(out)])
    return out

## FOR TEST

def DumpDb(dbfile):
    out = []
    db = anydbm.open(dbfile, "r")
    for k,v in db.iteritems():
        out.append((k,v))
    db.close()
    return out

def DumpAllMaps():
    for mapdbfile in os.listdir('data/maps'):
        yield DumpDb('data/maps/%s' % mapdbfile)

def main():
    print(DbGetNearbyPoints(45.0,0.0))
    l = DbGetListOfDates()
    for k,v in l.iteritems():
        print('%s %s' % (k,v))
    DumpAllMaps()
    list(DbRebuildAllIfNeeded(force=['date','trackdesc','startpoint'],verbose=True))
    for dbfile in os.listdir('data/'):
        if dbfile.endswith('_INV.db'):
            print(dbfile)
            print(DumpDb('data/%s' % dbfile))
    DumpDb('data/TRACKDESC_INV.db')
    DumpDb('data/STARTPOINT_INV.db')

if __name__ == '__main__':
   main()
