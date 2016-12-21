
import anydbm
from urllib import urlopen
from log import Log


## Geonames.org functions ##

#http://ws.geonames.org/astergdem?lats=50.01,50.02&lngs=10.2,10.3 (up to 20 pts)

def GetEleFromLatLonFromServer(lat,lon):
    "Give elevation from latitude and longitude using geonames.org web service"
    query_str = 'http://api.geonames.org/astergdem?username=fredi&lat=%f&lng=%f' % (lat,lon)
    try:
        f = urlopen(query_str)
        ele = int(f.read())
    except IOError:
        raise Exception('Sorry, outage on DEM server, please resend the map without the DEM option checked')
    return ele

def GetEleFromLatLon(lat,lon):
    db = anydbm.open("data/DEM.db", "c")
    dbkey = '%.4f,%.4f' % (lat,lon)
    if db.has_key(dbkey):
        if not db.has_key('stats_callcnt'):
            db['stats_callcnt'] = '1'
        else:
            db['stats_callcnt'] = str(int(db['stats_callcnt'])+1)
        ele = int(db[dbkey])
    else:
        ele = GetEleFromLatLonFromServer(lat,lon)
        db[dbkey] = str(ele)
    db.close()
    return ele

def LogError(s):
    f = open('dem.log','a')
    f.write(s)
    f.close()

def PerformQuery(pts,retr_list,db):
    
    # Build Query String (ex: http://ws.geonames.org/astergdem?lats=45.01,45.02&lngs=7.2,7.3)
    query_url = 'http://api.geonames.org/astergdem?username=fredi&lats=' + ','.join(map(lambda (lat,lon,index_pts): '%.4f' % lat,retr_list)) + '&lngs=' + ','.join(map(lambda (lat,lon,index_pts): '%.4f' % lon,retr_list))
    
    # Perform HTTP request
    try:
        retr_eles = map(int,urlopen(query_url).read()[:-2].split('\r\n'))
    except:
        LogError('DEM server returned: %s\n' % urlopen(query_url).read())
        #raise Exception('DEM server returned: %s' % urlopen(query_url).read())
        #DEM Server error->keep current elevations
        return
    
    # Update elevations of bufferized points
    index_retr_eles = 0
    for lat,lon,index_pts_inner_loop in retr_list:
        
        pts[index_pts_inner_loop].ele = retr_eles[index_retr_eles]
        
        # Put data in cache
        db['%.4f,%.4f' % (lat,lon)] = str(retr_eles[index_retr_eles])
        
        index_retr_eles+=1


# Input/Output: pts: objects with lat and lon attributes, ele will be set (or overwritten)
# Return: none
def GetEleFromLatLonList(pts,interpolate=True):
    
    Log('GetEleFromLatLonList nbpts=%s\n' % len(pts))
    
    # Open cache for r/w (create if file don't yet exists)
    db = anydbm.open("data/DEM.db", "c")
    
    # List of (lat,lon,index) for building query string
    retr_list = []
    
    # Counter for saving the index in pts list
    index_pts = 0
    
    for pt in pts:
        
        # Check if data is already on cache
        db_key = '%.4f,%.4f' % (pt.lat,pt.lon)
        if db.has_key(db_key):
            
            # Get data from cache
            pt.ele = int(db[db_key])
            
        else:
            
            # Add in retr_list
            retr_list.append((pt.lat,pt.lon,index_pts))
            
            if len(retr_list)==20:
                
                PerformQuery(pts,retr_list,db)
                
                # Empty retrieve list
                retr_list = []
                
        index_pts+=1
    
    # Perform query for last retr_list
    if len(retr_list)>1:
        PerformQuery(pts,retr_list,db)
    
    # Flush and close cache
    db.close()
    
    if interpolate:
        
        # Interpolate
        curele = pts[0].ele
        curidx = 0
        for i in range(0,len(pts)):
            if pts[i].ele!=curele:
                
                # build linear interpolation
                for j in range(curidx+1,i):
                    pts[j].ele = int(float(pts[curidx].ele) + float(j-curidx)*float(pts[i].ele-pts[curidx].ele)/float(i-curidx))
                curele = pts[i].ele
                curidx = i


## UNIT TEST CODE ##

def DumpDemDb():
    db = anydbm.open("DEM.db", "r")
    for k,v in db.iteritems():
        print('%s %s' % (k,v))
    db.close()

def TestCase1():
	print(GetEleFromLatLon(43.8467283,7.1270533))
	print(GetEleFromLatLon(43.8467250,7.1270500))
	print(GetEleFromLatLon(43.8549017,7.1351717))

def PrintStatsCallCnt():
	db = anydbm.open("DEM.db", "r")
	if not db.has_key('stats_callcnt'):
		print('0')
	else:
		print(db['stats_callcnt'])
	db.close()


def main():
	PrintStatsCallCnt()
	TestCase1()
	DumpDemDb()
	raw_input('Press Enter')

if __name__ == '__main__':
   main()
