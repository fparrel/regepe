
# Script that convert data from cgi-bin architecture to nginx uwsgi flask architecture

import os
import gzip
import json

# Parses "value = [.*\n]* EOD;"
def parsekeyequalvaluemultiline2(k):
    global b,idx,idx2
    idx=b.find(k+' =',idx2)
    if idx==-1:
        idx=b.find(k+'=',idx2)
    idx2=b.find('EOD;',idx)
    return b[idx+len(k)+2:idx2]

# Parses "value = <<<EOD [.*\n]* EOD;"
def parsekeyequalvaluemultiline1(k):
    global b,idx,idx2
    idx=b.find(k+' = <<<EOD',idx2)
    if idx==-1:
        idx=b.find(k+'=<<<EOD',idx2)
    if idx==-1:
        raise Exception('parse error')
    idx2=b.find('EOD;',idx)
    return b[idx+len(k)+9:idx2].strip()

# Parses "key\s?=\s?value;"
def parsekeyequalvalue(k):
    global b,idx,idx2
    idx=b.find(k+' =',idx2)
    offset=2
    if idx==-1:
        idx=b.find(k+'=',idx2)
        offset=1
    idx2=b.find(';',idx)
    return b[idx+len(k)+offset:idx2].strip()

# Parses "\tnew Point(lat,lon,time,ele,spd,arrow_id,course),?"
def parsepoint(s):
    s=s.strip().rstrip(')')
    v = s[10:].split(',')
    return (float(v[0]),float(v[1]),v[2][1:-1],int(v[3]),float(v[4]),int(v[5]),int(v[6]))

for fname in os.listdir('../lamp-prod/www/maps'):
    if fname.endswith('-json.php.gz'):
        print(fname)
        # Open old file
        f = gzip.open('../lamp-prod/www/maps/'+fname,'rb')
        b = f.read()
        f.close()
        # Intialize begin and end of value indexes
        idx=0
        idx2=0
        # Parse values
        map_type = parsekeyequalvalue('$map_type')[1:-1]
        assert(map_type in ('GeoPortal','GMaps'))
        figures=json.loads(parsekeyequalvaluemultiline1('$figures'))
        charts=json.loads('[%s]'%parsekeyequalvaluemultiline1('$charts'))
        nbpts = int(parsekeyequalvalue('nbpts'))
        spdunit = parsekeyequalvalue('spdunit')[1:-1]
        flat = int(parsekeyequalvalue('flat'))
        wind = int(parsekeyequalvalue('wind'))
        maxspd = int(parsekeyequalvalue('maxspd'))
        mapid = parsekeyequalvalue('mapid')[1:-1]
        centerlat = float(parsekeyequalvalue('centerlat'))
        centerlon = float(parsekeyequalvalue('centerlon'))
        minlat = float(parsekeyequalvalue('minlat'))
        minlon = float(parsekeyequalvalue('minlon'))
        maxlat = float(parsekeyequalvalue('maxlat'))
        maxlon = float(parsekeyequalvalue('maxlon'))
        track_points = list(map(parsepoint,parsekeyequalvalue('track_points').lstrip('[').rstrip(']').split('),')))
        chartdata = json.loads(parsekeyequalvaluemultiline2('chart').rstrip().rstrip(';'))
        # Build output dictionary
        mapdict={'mapid':mapid,'type':map_type,'figures':figures,'charts':charts,'nbpts':nbpts,'spdunit':spdunit,'flat':flat,'wind':wind,'maxspd':maxspd,'centerlat':centerlat,'centerlon':centerlon,'minlat':minlat,'minlon':minlon,'maxlat':maxlat,'maxlon':maxlon,'points':track_points,'chartdata':chartdata}
        # Write output in compressed json
        f=gzip.open('data/mapdata/%s.json.gz'%mapid,'wb')
        json.dump(mapdict,f)
        f.close()
