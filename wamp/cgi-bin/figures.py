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
        return '%.0f m in %s sec between %s and %s course %.0f deg' %(self.dst,self.time,str(self.ptfrom),str(self.ptto),self.course)
    def tojson(self):
        return '{"type":"%s","dst":%.0f,"dst_unit":"m","time":%s,"time_unit":"s","from_id":%d,"to_id":%d,"when_from":"%s","course":%.0f}'%(self.type,self.dst,self.time,self.ptfromid,self.pttoid,self.ptfrom.datetime.strftime('%H:%M:%S'),self.course)

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
    def computeMaxSpeeds(self,fromspd=True):
        if fromspd:
            dsts = self.trkseg.ComputeEqDistancesFromSpd()
        else:
            dsts = self.trkseg.ComputeDistances()
        if not options['flat']:
            eles = map(lambda pt:pt.ele,self.trkseg.ptlist)
        tms = map(lambda pt:pt.datetime,self.trkseg.ptlist)
        #maxspds = dict([(Figures.max_spd_dists[i],[0 for i in range(0,10)]) for i in range(0,len(Figures.max_spd_dists))])
        maxspds = [[MaxSpdZero for i in range(0,6)] for i in range(0,len(Figures.max_spd_dists))]
        maxspds_vert = [[MaxSpdZero for i in range(0,6)] for i in range(0,len(Figures.max_spd_dists_vert))]
        jees=[0 for i in range(0,len(Figures.max_spd_dists))]
        jees_vert=[0 for i in range(0,len(Figures.max_spd_dists))]
        maxspdstime = [[MaxSpdZero for i in range(0,6)] for i in range(0,len(Figures.max_spd_times))]
        maxspdstime_vert = [[MaxSpdZero for i in range(0,6)] for i in range(0,len(Figures.max_spd_times_vert))]
        jeestime=[0 for i in range(0,len(Figures.max_spd_times))]
        jeestime_vert=[0 for i in range(0,len(Figures.max_spd_times_vert))]
        for i in range(0,len(self.trkseg.ptlist)):
            for maxspds_idx in range(0,len(maxspds)):
                if dsts[i]-dsts[jees[maxspds_idx]]>=Figures.max_spd_dists[maxspds_idx]:
                    j = jees[maxspds_idx]
                    spd = (dsts[i]-dsts[j])/TimeDeltaToSeconds(tms[i]-tms[j])
                    if spd>maxspds[maxspds_idx][-1].spd:
                        for k in range(0,len(maxspds[maxspds_idx])):
                            if spd>maxspds[maxspds_idx][k].spd:
                                newspd = MaxSpd(spd,(dsts[i]-dsts[j]),TimeDeltaToSeconds(tms[i]-tms[j]),self.trkseg.ptlist[j],self.trkseg.ptlist[i],j,i,GeodeticCourse(self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon,self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon),"dist")
                                if k>0:
                                    maxspds[maxspds_idx] = maxspds[maxspds_idx][:k]+[newspd]+maxspds[maxspds_idx][k+1:]
                                else:
                                    maxspds[maxspds_idx] = [newspd]+maxspds[maxspds_idx][k+1:]
                                break
                    jees[maxspds_idx] = i
            for maxspds_idx in range(0,len(maxspdstime)):
                if TimeDeltaToSeconds(tms[i]-tms[jeestime[maxspds_idx]])>=Figures.max_spd_times[maxspds_idx]:
                    j = jeestime[maxspds_idx]
                    spd = (dsts[i]-dsts[j])/TimeDeltaToSeconds(tms[i]-tms[j])
                    if spd>maxspdstime[maxspds_idx][-1].spd:
                        for k in range(0,len(maxspdstime[maxspds_idx])):
                            if spd>maxspdstime[maxspds_idx][k].spd:
                                newspd = MaxSpd(spd,(dsts[i]-dsts[j]),TimeDeltaToSeconds(tms[i]-tms[j]),self.trkseg.ptlist[j],self.trkseg.ptlist[i],j,i,GeodeticCourse(self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon,self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon),"dist")
                                if k>0:
                                    maxspdstime[maxspds_idx] = maxspdstime[maxspds_idx][:k]+[newspd]+maxspdstime[maxspds_idx][k+1:]
                                else:
                                    maxspdstime[maxspds_idx] = [newspd]+maxspdstime[maxspds_idx][k+1:]
                                break
                    jeestime[maxspds_idx] = i
            if not options['flat']:
                for maxspds_idx in range(0,len(maxspds_vert)):
                    if eles[i]-eles[jees_vert[maxspds_idx]]>=Figures.max_spd_dists_vert[maxspds_idx]:
                        j = jees_vert[maxspds_idx]
                        spd = (eles[i]-eles[j])/TimeDeltaToSeconds(tms[i]-tms[j])
                        if spd>maxspds_vert[maxspds_idx][-1].spd:
                            for k in range(0,len(maxspds_vert[maxspds_idx])):
                                if spd>maxspds_vert[maxspds_idx][k].spd:
                                    newspd = MaxSpd(spd,(eles[i]-eles[j]),TimeDeltaToSeconds(tms[i]-tms[j]),self.trkseg.ptlist[j],self.trkseg.ptlist[i],j,i,GeodeticCourse(self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon,self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon),"vert")
                                    if k>0:
                                        maxspds_vert[maxspds_idx] = maxspds_vert[maxspds_idx][:k]+[newspd]+maxspds_vert[maxspds_idx][k+1:]
                                    else:
                                        maxspds_vert[maxspds_idx] = [newspd]+maxspds_vert[maxspds_idx][k+1:]
                                    break
                        jees_vert[maxspds_idx] = i
                for maxspds_idx in range(0,len(maxspdstime_vert)):
                    if TimeDeltaToSeconds(tms[i]-tms[jeestime_vert[maxspds_idx]])>=Figures.max_spd_times_vert[maxspds_idx]:
                        j = jeestime_vert[maxspds_idx]
                        spd = (eles[i]-eles[j])/TimeDeltaToSeconds(tms[i]-tms[j])
                        if spd>maxspdstime_vert[maxspds_idx][-1].spd:
                            for k in range(0,len(maxspdstime_vert[maxspds_idx])):
                                if spd>maxspdstime_vert[maxspds_idx][k].spd:
                                    newspd = MaxSpd(spd,(eles[i]-eles[j]),TimeDeltaToSeconds(tms[i]-tms[j]),self.trkseg.ptlist[j],self.trkseg.ptlist[i],j,i,GeodeticCourse(self.trkseg.ptlist[j].lat,self.trkseg.ptlist[j].lon,self.trkseg.ptlist[i].lat,self.trkseg.ptlist[i].lon),"vert")
                                    if k>0:
                                        maxspdstime_vert[maxspds_idx] = maxspdstime_vert[maxspds_idx][:k]+[newspd]+maxspdstime_vert[maxspds_idx][k+1:]
                                    else:
                                        maxspdstime_vert[maxspds_idx] = [newspd]+maxspdstime_vert[maxspds_idx][k+1:]
                                    break
                        jeestime_vert[maxspds_idx] = i
        out = [dict([(Figures.max_spd_dists[i],filter(lambda maxspd: maxspd!=MaxSpdZero, maxspds[i])) \
                            for i in range(0,len(Figures.max_spd_dists))]), \
                    dict([(Figures.max_spd_times[i],filter(lambda maxspd: maxspd!=MaxSpdZero, maxspdstime[i])) \
                            for i in range(0,len(Figures.max_spd_times))])]
        if not options['flat']:
            out.extend([dict([(Figures.max_spd_dists_vert[i],filter(lambda maxspd: maxspd!=MaxSpdZero, maxspds_vert[i])) \
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


def unittests():
    from gpxparser import ParseGpxFile
    ptlist = ParseGpxFile('../../work/testfiles/downwind.gpx',0,0)
    print len(ptlist)
    track = Track(ptlist)
    figures = Figures(track,'km/h',False)
    options['flat']=True
    (mxspdsdst,mxspdtime) = figures.computeMaxSpeeds()
    for i in mxspdsdst:
        print 'Best %s meters'%i
        for mxspd in mxspdsdst[i]:
            print mxspd
    for i in mxspdtime:
        print 'Best %s seconds'%i
        for mxspd in mxspdtime[i]:
            print mxspd

if __name__=='__main__':
    unittests()
