from model import Track
from log import Log
from mathutil import FindLocalMaximums,Mean,GeodeticCourse
from conversions import TimeDeltaToSeconds
from options import options

class MaxSpd:
    def __init__(self,spd,dst,time,ptfrom,ptto,ptfromid,pttoid,course,type):
        self.spd=spd
        self.dst=dst
        self.time=time
        self.ptfrom=ptfrom
        self.ptto=ptto
        self.ptfromid=ptfromid
        self.pttoid=pttoid
        self.course=course
        self.type=type
    def __str__(self):
        return '%.2f km/h %.1f m in %s sec between %s and %s course %.0f deg' %(self.spd*3.6,self.dst,self.time,str(self.ptfrom),str(self.ptto),self.course)
    def tojson(self):
        return '{"type":"%s","dst":%.0f,"dst_unit":"m","time":%s,"time_unit":"s","from_id":%d,"to_id":%d,"when_from":"%s","course":%.0f}'%(self.type,self.dst,self.time,self.ptfromid,self.pttoid,self.ptfrom.datetime.strftime('%H:%M:%S'),self.course)
    def intersect(self,other):
        if self.ptfromid==MaxSpdZero.ptfromid or self.pttoid==MaxSpdZero.pttoid:
            return False
        if other.ptfromid==MaxSpdZero.ptfromid or other.pttoid==MaxSpdZero.pttoid:
            return False
        return not(self.ptfromid>=other.pttoid or self.pttoid<=other.ptfromid)

MaxSpdZero = MaxSpd(0,0,0,None,None,-1,-1,0.0,None)

class Figures:
    "Compute and keeps figures from a track segment"
    # top10_speeds: list of fastest 10 points
    # mean_speed: mean speed
    # spdunit: unit of mean speed
    # min_ele: minimum altitude in meters
    # max_ele: maximum altitude in meters
    # lengthspd: length of track segment in meters computed by integrating speed against time
    # lengthdist: length of track segment in meters computed by sum of distances between points
    # up: D+
    # down: D-
    # flat: flat or not
    # duration: total duration of track
    max_spd_dists = [50,100,200,500,1852]
    max_spd_dists_vert = [50,100,200,500]
    max_spd_times = [2,5,10,60]
    max_spd_times_vert = [60,600,1800,3600,7200]
    def addMaxSpeed(self,newspd,maxspds):
        for k in range(0,len(maxspds)):
            if maxspds[k].intersect(newspd):
                # If intersect with another speed and is greater, replace it, else that mean that we have already a maxspeed for the zone, so ignore it
                if newspd.spd>maxspds[k].spd:
                   maxspds[k]=newspd
                break
            else:
                # Insert into the top speeds
                if newspd.spd>maxspds[k].spd:
                    maxspds.insert(k,newspd)
                    maxspds.pop()
                    # Remove following speeds that intersect with this one (because they will be of a lower speed)
                    for l in range(k+1,len(maxspds)):
                        if maxspds[l].intersect(newspd):
                            maxspds[l]=MaxSpdZero
                    break
        return maxspds

    def computeMaxSpeeds(self,fromspd=True,nbmax=6):

        # Get distances
        if fromspd and not self.trkseg.spdcomputed:
            dsts = self.trkseg.ComputeEqDistancesFromSpd()
        else:
            dsts = self.trkseg.ComputeDistances()
        if not options['flat']:
            eles = map(lambda pt:pt.ele,self.trkseg.ptlist)

        # Get times
        tms = map(lambda pt:pt.datetime,self.trkseg.ptlist)

        assert(len(tms)==len(dsts)==len(self.trkseg.ptlist))

        # Initialize output with zero speed and index zero
        maxspdsdist = [[MaxSpdZero for i in range(0,nbmax)] for i in range(0,len(Figures.max_spd_dists))]
        maxspdstime = [[MaxSpdZero for i in range(0,nbmax)] for i in range(0,len(Figures.max_spd_times))]
        if not options['flat']:
            maxspdsdist_vert = [[MaxSpdZero for i in range(0,nbmax)] for i in range(0,len(Figures.max_spd_dists_vert))]
            maxspdstime_vert = [[MaxSpdZero for i in range(0,nbmax)] for i in range(0,len(Figures.max_spd_times_vert))]

        for i in range(0,len(self.trkseg.ptlist)):

            # Over time
            for maxspds_idx in range(0,len(maxspdstime)):
                for j in range(i,len(self.trkseg.ptlist)):
                    if TimeDeltaToSeconds(tms[j]-tms[i])>=Figures.max_spd_times[maxspds_idx]:
                        spd = (dsts[j]-dsts[i])/TimeDeltaToSeconds(tms[j]-tms[i])
                        if spd>maxspdstime[maxspds_idx][-1].spd:
                            self.addMaxSpeed(MaxSpd(spd,(dsts[j]-dsts[i]),TimeDeltaToSeconds(tms[j]-tms[i]),self.trkseg.ptlist[i],self.trkseg.ptlist[j],i,j,GeodeticCourse(self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon,self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon),"dist"),maxspdstime[maxspds_idx])
                        break

            # Over distance
            for maxspds_idx in range(0,len(maxspdsdist)):
                for j in range(i,len(self.trkseg.ptlist)):
                    if dsts[j]-dsts[i]>=Figures.max_spd_dists[maxspds_idx]:
                        spd = (dsts[j]-dsts[i])/TimeDeltaToSeconds(tms[j]-tms[i])
                        if spd>maxspdsdist[maxspds_idx][-1].spd:
                            self.addMaxSpeed(MaxSpd(spd,(dsts[j]-dsts[i]),TimeDeltaToSeconds(tms[j]-tms[i]),self.trkseg.ptlist[i],self.trkseg.ptlist[j],i,j,GeodeticCourse(self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon,self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon),"dist"),maxspdsdist[maxspds_idx])
                        break

            if not options['flat']:
                # Vertical over time
                for maxspds_idx in range(0,len(maxspdstime_vert)):
                    for j in range(i,len(self.trkseg.ptlist)):
                        if TimeDeltaToSeconds(tms[j]-tms[i])>=Figures.max_spd_times_vert[maxspds_idx]:
                            spd = (eles[j]-eles[i])/TimeDeltaToSeconds(tms[j]-tms[i])
                            if spd>maxspdstime_vert[maxspds_idx][-1].spd:
                                self.addMaxSpeed(MaxSpd(spd,(eles[j]-eles[i]),TimeDeltaToSeconds(tms[j]-tms[i]),self.trkseg.ptlist[i],self.trkseg.ptlist[j],i,j,GeodeticCourse(self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon,self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon),"vert"),maxspdstime_vert[maxspds_idx])
                            break
                # Vertical over distance
                for maxspds_idx in range(0,len(maxspdsdist_vert)):
                    for j in range(i,len(self.trkseg.ptlist)):
                        if eles[j]-eles[i]>=Figures.max_spd_dists_vert[maxspds_idx]:
                            spd = (eles[j]-eles[i])/TimeDeltaToSeconds(tms[j]-tms[i])
                            if spd>maxspdsdist_vert[maxspds_idx][-1].spd:
                                self.addMaxSpeed(MaxSpd(spd,(eles[j]-eles[i]),TimeDeltaToSeconds(tms[j]-tms[i]),self.trkseg.ptlist[i],self.trkseg.ptlist[j],i,j,GeodeticCourse(self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon,self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon),"vert"),maxspdsdist_vert[maxspds_idx])
                            break

        # Return output merged without the zeros
        out = [dict([(Figures.max_spd_dists[i],filter(lambda maxspd: maxspd!=MaxSpdZero, maxspdsdist[i])) \
                            for i in range(0,len(Figures.max_spd_dists))]), \
                    dict([(Figures.max_spd_times[i],filter(lambda maxspd: maxspd!=MaxSpdZero, maxspdstime[i])) \
                            for i in range(0,len(Figures.max_spd_times))])]
        if not options['flat']:
            out.extend([dict([(Figures.max_spd_dists_vert[i],filter(lambda maxspd: maxspd!=MaxSpdZero, maxspdsdist_vert[i])) \
                            for i in range(0,len(Figures.max_spd_dists_vert))]), \
                            dict([(Figures.max_spd_times_vert[i],filter(lambda maxspd: maxspd!=MaxSpdZero, maxspdstime_vert[i])) \
                            for i in range(0,len(Figures.max_spd_times_vert))])])
        return out

    def __init__(self,trkseg,spdunit,flat):
        self.trkseg = trkseg
        self.flat = flat
        if not flat:
            # Compute altitude extremums
            self.min_ele = min([pt.ele for pt in trkseg.ptlist])
            self.max_ele = max([pt.ele for pt in trkseg.ptlist])
            # Compute D+ and D-
            (self.up,self.down) = trkseg.ComputeEleDiff(20)
        if trkseg.nospeeds:
            self.top10_speeds = []
            self.mean_speed = -1.0
            self.mean_speed_when_in_motion = -1.0
            self.spdunit = spdunit
            # For avoiding another 'if nospeeds' switch
            # trkseg.ConvertSpeed(spdunit)
            self.lengthdist = trkseg.ComputeLengthFromDist()
            return
        # Compute top 10 speeds
        Log('Figures: FindLocalMaximums\n')
        top10_speed_ids = FindLocalMaximums(trkseg.ptlist,lambda pt: pt.spd,None,0)
        #top10_speed_ids = FindLocalMaximums(trkseg.ptlist,lambda pt: pt.spd,Mean,3)
        top10_speed_ids = top10_speed_ids[0:10]
        self.top10_speeds = [[i,trkseg.ptlist[i]] for i in top10_speed_ids]
        self.top10_speeds.sort(key=lambda a: a[1].datetime)
        # Compute mean speed
        Log('Figures: ConvertSpeed\n')
        trkseg.ConvertSpeed(spdunit)
        speeds = [pt.spd_converted[spdunit] for pt in trkseg.ptlist]
        Log('Figures: Means\n')
        self.mean_speed = Mean(speeds)
        self.spdunit = spdunit
        # Mean speed when in motion
        speeds_in_motion = []
        for spd in speeds:
            if spd>0.5:
                speeds_in_motion.append(spd)
        try:
            self.mean_speed_when_in_motion = Mean(speeds_in_motion)
        except ZeroDivisionError:
            self.mean_speed_when_in_motion = -1.0
        # Compute duration
        self.duration = trkseg.ptlist[-1].datetime - trkseg.ptlist[0].datetime
        # Compute length
        Log('Figures: ComputeLengthFromSpd\n')
        self.lengthspd = trkseg.ComputeLengthFromSpd()
        Log('Figures: ComputeLengthFromDist\n')
        self.lengthdist = trkseg.ComputeLengthFromDist()
        Log('Figures: end\n')
    def __str__(self):
        return 'Figures object'
    def computeOneSpd(self,when_from,when_to,fromspd=True):
        if fromspd:
            dsts = self.trkseg.ComputeEqDistancesFromSpd()
        else:
            dsts = self.trkseg.ComputeDistances()
        tms = map(lambda pt:pt.datetime,self.trkseg.ptlist)
        idx=0
        for pt in self.trkseg.ptlist:
            if pt.datetime == when_from:
                j = idx
            if pt.datetime == when_to:
                i = idx
            idx+=1
        spd = (dsts[i]-dsts[j])/TimeDeltaToSeconds(tms[i]-tms[j])
        return MaxSpd(spd,(dsts[i]-dsts[j]),TimeDeltaToSeconds(tms[i]-tms[j]),self.trkseg.ptlist[j],self.trkseg.ptlist[i],j,i,GeodeticCourse(self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon,self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon),"dist")

def unittests():
    from gpxparser import ParseGpxFile
    #ptlist = ParseGpxFile('../../work/testfiles/downwind.gpx',0,0)
    ptlist = ParseGpxFile('../../lamp-prod/cgi-bin/submit/56d74ad0cb0ec_0.gpx',0,0)
    print len(ptlist)
    track = Track(ptlist)
    figures = Figures(track,'knots',False)
    options['flat']=True
    (mxspdsdst,mxspdtime) = figures.computeMaxSpeeds(fromspd=True,nbmax=10)
    for i in mxspdsdst:
        print 'Best %s meters'%i
        for mxspd in mxspdsdst[i]:
            print mxspd
    for i in mxspdtime:
        print 'Best %s seconds'%i
        for mxspd in mxspdtime[i]:
            print mxspd
    print track.ptlist[0].datetime
    from datetime import datetime
    print figures.computeOneSpd(datetime(year=2016,month=1,day=10,hour=11,minute=50,second=15),datetime(year=2016,month=1,day=10,hour=11,minute=50,second=15+11),fromspd=False)

if __name__=='__main__':
    unittests()
