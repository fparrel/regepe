
from miscranges import frange6,SmartRange
from mathutil import Mean,GeodeticDistGreatCircle,GeodeticDistVincenty,GeodeticCourse
from conversions import TimeDeltaToSeconds,MetersPerSecToSpdunit
from powercomp import BikePower
from mymath import fsum

# Digital Elevation Model API
from dem import GetEleFromLatLonList

from log import Log,Warn
from datetime import timedelta

# i18n
from flask_babel import gettext

class Bounds:
    "Keeps map bounds"
    # minlat
    # minlon
    # maxlat
    # maxlon
    def __init__(self):
        self.minlat = None
        self.maxlat = None
        self.minlon = None
        self.maxlon = None
    def Extend(self,*args):
        "Extends bounds from another bounds object or from lat,lon"
        l = len(args)
        if l==2:
            self.ExtendPoint(args[0],args[1])
        elif l==1:
            self.ExtendBounds(args[0])
    def ExtendPoint(self,lat,lon):
        "Extends bounds from a point (lat,lon)"
        # First point
        if self.minlat==None:
            self.minlat = lat
            self.maxlat = lat
            self.minlon = lon
            self.maxlon = lon
        if self.minlat > lat: self.minlat = lat
        if self.minlon > lon: self.minlon = lon
        if self.maxlat < lat: self.maxlat = lat
        if self.maxlon < lon: self.maxlon = lon
    def ExtendBounds(self,otherbounds):
        "Extends bounds from another Bounds object"
        # First point
        if self.minlat==None:
            self.minlat = otherbounds.minlat
            self.maxlat = otherbounds.maxlat
            self.minlon = otherbounds.minlon
            self.maxlon = otherbounds.maxlon            
        if self.minlat > otherbounds.minlat: self.minlat = otherbounds.minlat
        if self.minlon > otherbounds.minlon: self.minlon = otherbounds.minlon
        if self.maxlat < otherbounds.maxlat: self.maxlat = otherbounds.maxlat
        if self.maxlon < otherbounds.maxlon: self.maxlon = otherbounds.maxlon
    def GetCenter(self):
        "Return center ([lat,lon]) of the map"
        return [(self.minlat + self.maxlat)/2,(self.minlon + self.maxlon)/2]


class Point:
    "Keeps a point got from a gpx file (trkpt tag)"
    # lat: latitude in degrees
    # lon: longitude in degrees
    # ele: elevation in meters (above sea level or geoid?)
    # spd: speed in m/s
    # spdunit: 'm/s', 'knots' or 'km/h'
    # spd_converted: speed in other units than m/s (dict)
    # course: course in degrees
    # datetime: date and time
    # priority: is the point important
    # hr: heart rate
    spd_converter = {'knots': 1.94384449, 'km/h': 3.6, 'mph': 2.23693629}
    def __init__(self,lat,lon,ele,spd,course,datetime,spdunit='m/s',hr=None):
        "Create a Point"
        self.lat = lat
        self.lon = lon
        self.ele = ele
        if spd==None:
            self.spd = None
            self.spdunit = None
            self.spd_converted = {'m/s': None}
        else:
            if spdunit=='m/s':
                self.spd = spd
                self.spdunit = 'm/s'
                self.spd_converted = {'m/s': self.spd}
            elif spdunit in ('km/h','kph'):
                self.spd = spd / 3.6
                self.spdunit = 'm/s'
                self.spd_converted = {'km/h': spd, 'm/s': self.spd}
            elif spdunit=='knots':
                self.spd = spd * 0.514444444
                self.spdunit = 'm/s'
                self.spd_converted = {'knots': spd, 'm/s': self.spd}
            elif spdunit=='mph':
                self.spd = spd * 0.44704
                self.spdunit = 'm/s'
                self.spd_converted = {'mph': spd, 'm/s': self.spd}
            else:
                raise Exception(gettext("Unknown speed unit: %s") % spdunit)
        self.course = course
        self.datetime = datetime
        self.priority = 0
        if hr!=None:
            self.hr=hr
    def ConvertSpeed(self,unit):
        "Convert speed in the given unit"
        if self.spd==None:
            self.spd_converted[unit] = -1.0
            Warn('Cannot convert speed if speed is not provided')
        elif not self.spd_converted.has_key(unit):
            if self.spdunit=='m/s' or self.spdunit==None:
                self.spd_converted[unit] = self.spd * Point.spd_converter[unit]
            else:
                raise ValueError(gettext('Speed conversion from %s to %s not supported') % (self.spdunit,unit))
    def Distance(self,other):
        "Return distance in meters from self to other"
        return GeodeticDistGreatCircle(self.lat,self.lon,other.lat,other.lon)
    def DistancePrecise(self,other):
        "Return distance in meters from self to other"
        return GeodeticDistVincenty(self.lat,self.lon,other.lat,other.lon)
    def GetTimeString(self):
        "Return time converted to a 'HH:MM:SS' string"
        if self.datetime==None:
            return None
        return self.datetime.strftime('%H:%M:%S')
    def GetDateTimeString(self):
        "Return time converted to a 'HH:MM:SS' string"
        if self.datetime==None:
            return None
        return self.datetime.strftime('%Y-%m-%d %H:%M:%S')        
    def __str__(self):
        "String representation of point for debugging purpose"
        return 'Point(datetime=%s)' % (self.GetTimeString())
    def ChangeSpeed(self,newspd):
        "Change speed to newspd in m/s and redo neeeded convertions"
        self.spd = newspd
        for unit in self.spd_converted:
            if self.spdunit=='m/s':
                if unit=='m/s':
                    self.spd_converted[unit] = self.spd
                else:
                    self.spd_converted[unit] = self.spd * Point.spd_converter[unit]
            else:
                raise ValueError(gettext('Speed conversion from %s to %s not supported') % (self.spdunit,unit))
    def GetSpeed(self,unit):
        if not self.spd_converted.has_key(unit):
            self.ConvertSpeed(unit)
        return self.spd_converted[unit]


class Track:
    "Keeps a Track (list of points)"
    # ptlist: list of points
    # bounds: bounds of the list of points
    # ptindexlist: if the trkseg is the compression of another trkseg, list of id of ptlist in the ptlist of the orginial trkseg
    # nospeeds: true if track contains no speed/time data
    # spdcomputed: have the speed been computed or taken from input file
    # dists: distance between this point and the previous one (zero for first point)
    bike_power_friction = 0.016975308641975308641975308641975
    bike_power_climbing = 0.0272
    def __init__(self,ptlist,bounds=None,ptindexlist=None,forcespdcomp=False):
        "Create a Track from a list of Points and a Bounds"
        self.dists=None
        self.bounds = Bounds()
        if not bounds==None:
            self.bounds.Extend(bounds)
        else:
            for pt in ptlist:
                self.bounds.Extend(pt.lat,pt.lon)
        if(len(ptlist)<1):
            raise Exception(gettext('Empty track'))
        self.ptlist = ptlist
        self.ptindexlist = ptindexlist
        self.nospeeds = False
        Log('Track: ComputeSpeed/Course/FillEleWhenNeeded')
        self.__ComputeSpeedWhenNeeded(force=forcespdcomp)
        self.__ComputeCourseWhenNeeded()
        self.__FillEleWhenNeeded()
        Log('Track: CheckSpeedUnitAndCorrectIfNeeded')
        self.__CheckSpeedUnitAndCorrectIfNeeded()
        if not self.nospeeds:
            self.__AddOruxMapPauses()
    def GetSpeeds(self,spdunit):
        "Return the list of speeds in 'spdunit'"
        if spdunit=='m/s':
            return [pt.spd for pt in self.ptlist]
        if spdunit not in self.ptlist[0].spd_converted:
            self.ConvertSpeed(spdunit)
        return [pt.spd_converted[spdunit] for pt in self.ptlist]
    def GetElevations(self):
        "Return the list of elevations in meters"
        return [pt.ele for pt in self.ptlist]
    def __CompressPtlistLinear(self,nbpts):
        "Return a list of points built by keeping only 'nbpts' points from the list of points"
        idlist = list(map(int, frange6(0,len(self.ptlist),float(len(self.ptlist))/float(nbpts))))
        # always include last point
        if idlist[len(idlist)-1]!=len(self.ptlist)-1:
            idlist.append(len(self.ptlist)-1)
        return idlist
    def __CompressPtlistPriority2(self,nbpts):
        "Return a list of points built by keeping only 'nbpts' points from the list of points"
        nbptsinitial = nbpts
        # decrease total number of points by the number of important points
        for i in range(0,len(self.ptlist)):
            if self.ptlist[i].priority>1:
                nbpts -= 1
        if nbptsinitial - nbpts > nbptsinitial / 2:
            Warn('CompressPtlistPriority2: use standard compression')
            # If too much important points, use standard compression
            return self.__CompressPtlistLinear(nbptsinitial)
        idlist = list(map(int, frange6(0,len(self.ptlist),float(len(self.ptlist))/float(nbpts))))
        # Add important points
        idlistnew = []
        j = 0
        for i in range(0,len(self.ptlist)):
            if i==idlist[j] or self.ptlist[i].priority>1:
                idlistnew.append(i)
                if i==idlist[j] and j<len(idlist)-1:
                    j += 1
        # always include last point
        if idlistnew[len(idlistnew)-1]!=len(self.ptlist)-1:
            idlistnew.append(len(self.ptlist)-1)
        assert(len(idlistnew)>=len(idlist))
        return idlistnew
    def CompressCopyPriority(self,nbpts):
        "Return another Track with only 'nbpts'"
        ptindexlist = self.__CompressPtlistPriority2(nbpts)
        return Track([self.ptlist[i] for i in ptindexlist],self.bounds,ptindexlist)
    def __len__(self):
        "Return the number of points in list"
        return len(self.ptlist)
    def ConvertSpeed(self,unit):
        "Convert list of points' speed unit to 'unit'"
        for pt in self.ptlist:
            pt.ConvertSpeed(unit)
    def RemoveStayingPoints4(self,thresholddist,thresholdtime,thresholdspeed):
        "Remove the points when GPS is staying at the same place"
        if (self.nospeeds):
            return
        pauses = []
        removedptsidlist = []
        idlist = list(range(0,len(self.ptlist)))
        j = 0
        i = 0
        while i < len(self.ptlist):
            if TimeDeltaToSeconds(self.ptlist[i].datetime - self.ptlist[j].datetime) > thresholdtime:
                # Check if the track stayed more than thresholdtime seconds
                #  under thresholdspeed and not moving farther than thresholddist
                #  to initial position
                if self.ptlist[j].Distance(self.ptlist[i])<thresholddist and max(self.ptlist[k].spd for k in range(j,i+1))<thresholdspeed:
                    while i < len(self.ptlist) and self.ptlist[j].Distance(self.ptlist[i])<thresholddist and self.ptlist[i].spd<thresholdspeed:
                        i += 1
                    i -= 1
                    # Pause found between j and i
                    for k in range(j,i):
                        idlist.remove(k)
                        removedptsidlist.append(k)
                j = i
            i += 1
        removedptsidlistcpy = removedptsidlist[:]
        lastid = -2
        first = True
        for i in removedptsidlist:
            if i!=lastid+1:
                if not first:
                    pauses.append((curpausebegin,self.ptlist[lastid]))
                    self.ptlist[lastid].ChangeSpeed(0.0)
                    self.ptlist[lastid].priority = 2
                    try:
                        removedptsidlistcpy.remove(lastid)
                    except ValueError:
                        pass
                curpausebegin = self.ptlist[i]
                self.ptlist[i].ChangeSpeed(0.0)
                self.ptlist[i].priority = 2
                removedptsidlistcpy.remove(i)
                first = False
            lastid = i
        if not first:
            pauses.append((curpausebegin,self.ptlist[i]))
            self.ptlist[i].ChangeSpeed(0.0)
            self.ptlist[i].priority = 2
            try:
                removedptsidlistcpy.remove(i)
            except ValueError:
                pass
        idlistnew = []
        for i in range(0,len(self.ptlist)):
            if i not in removedptsidlistcpy:
                idlistnew.append(i)
        ptlist_new = [self.ptlist[i] for i in idlistnew]
        if self.dists!=None:
            dists_new=[]
            for i in range(1,len(idlistnew)):
                if idlistnew[i]==idlistnew[i-1]+1:
                    dists_new.append(self.dists[idlistnew[i]])
                else:
                    dists_new.append(GeodeticDistVincenty(self.ptlist[idlistnew[i-1]].lat,self.ptlist[idlistnew[i-1]].lon,self.ptlist[idlistnew[i]].lat,self.ptlist[idlistnew[i]].lon))
            self.dists = dists_new
        self.ptlist = ptlist_new
        return pauses
    def ComputeInstantVertSpeeds(self):
        "Compute list of instant vertical speeds in m/s"
        prevpt = None
        for pt in self.ptlist:
            if prevpt==None:
                vertspd = [0.0]
            else:
                t = TimeDeltaToSeconds(pt.datetime-prevpt.datetime)
                if t>0.0:
                    vertspd.append((pt.ele-prevpt.ele)/t)
                else:
                    vertspd.append(0.0)
            prevpt = pt
        return vertspd
    def ComputeMeanVertSpeeds(self,threshold):
        ''''Compute mean vertical speed for each up/down segment (ascent or descent). Put this value for each point of the segment'''	
        out = []
        i = 0
        for first_pt,last_pt,_ in self.__GetUpsAndDowns(threshold):
            t = TimeDeltaToSeconds(last_pt.datetime - first_pt.datetime)
            if t > 0.0:
                vspd = (last_pt.ele - first_pt.ele) / t
            else:
                vspd = 0.0
            while self.ptlist[i] != last_pt:
                out.append(vspd)
                i += 1
        out.append(out[-1])
        assert(len(self.ptlist)==len(out))
        return out
    def ComputeMeanSlope(self,vertthreshold,horithreshold):
        ''''Compute mean slope for each up/down segment (ascent or descent). Put this value for each point of the segment'''	
        out = []
        i = 0
        for first_pt,last_pt,_ in self.__GetUpsAndDowns(vertthreshold):
            if last_pt.Distance(first_pt) >= horithreshold:
                d = last_pt.DistancePrecise(first_pt)
                if d > 0.0:
                    slope = (last_pt.ele - first_pt.ele) / d
                else:
                    # zero distance is interpreted as flat
                    slope = 0.0
            else:
                slope = 0.0
            while self.ptlist[i] != last_pt:
                out.append(slope)
                i += 1
        out.append(out[-1])
        assert(len(self.ptlist)==len(out))
        return out
    def ComputeDistances(self):
        "Compute list of distances from the begin of track segment"
        self.__ComputeDistancesCache()
        out = []
        cptr = 0.0
        for i in range(0,len(self.ptlist)):
            cptr+=self.dists[i]
            out.append(cptr)
        return out
    def __GetUpsAndDowns(self,threshold):
        p1down = self.ptlist[0]
        p2down = self.ptlist[0]
        p1up = self.ptlist[0]
        p2up = self.ptlist[0]
        out = []
        last_up_or_down = 0
        current_up_or_down = 0
        for pt in self.ptlist:
            if current_up_or_down==0:
                if pt.ele - p1down.ele < -threshold:
                    current_up_or_down = 1
                elif pt.ele - p1up.ele > threshold:
                    current_up_or_down = 2
            elif current_up_or_down==1:
                if pt.ele < p2down.ele:
                    p2down = pt
                elif pt.ele - p2down.ele > threshold:
                    # down detected
                    out.append((p1down,p2down,1))
                    p1up = p2down
                    p2up = p2down
                    p1down = p2down
                    last_up_or_down = 1
                    current_up_or_down = 0
            elif current_up_or_down==2:
                if pt.ele > p2up.ele:
                    p2up = pt
                elif pt.ele - p2up.ele < -threshold:
                    # up detected
                    out.append((p1up,p2up,2))
                    p1down = p2up
                    p2down = p2up
                    p1up = p2up
                    last_up_or_down = 2
                    current_up_or_down = 0
        if last_up_or_down==1:
            p2up = pt
            # add last up
            out.append((p1up,p2up,2))
        if last_up_or_down==2:
            p2down = pt
            # add last down
            out.append((p1down,p2down,1))
        if last_up_or_down==0:
            # add last flat
            out.append((p1down,pt,0))
        return out
    def ComputeEleDiff(self,threshold):
        "Compute D+ and D-"
        ele = self.ptlist[0].ele
        maxe = ele
        mine = ele
        dminus = 0
        dplus = 0
        lastdiff = 0
        lastmine = mine
        lastmaxe = maxe
        for pt in self.ptlist:
            if pt.ele > maxe:
                maxe = pt.ele
            if pt.ele < mine:
                mine = pt.ele
            diff = pt.ele - ele
            # we consider that we change from ascent/descent only if elevation diff is enough
            if abs(diff) > threshold:
                if diff < 0:
                    if lastdiff == 1:
                        # up -> down => add to D+
                        lastmaxe = maxe
                        dplus += maxe - lastmine
                    lastdiff = -1
                else:
                    if lastdiff == -1:
                        # down -> up => add to D-
                        lastmine = mine
                        dminus += lastmaxe - mine
                    lastdiff = 1
                ele = pt.ele
                maxe = ele
                mine = ele
        if lastdiff==1:
            # finished in up => add to D+
            dplus += pt.ele - lastmine
        if lastdiff==-1:
            # finished in down => add to D-
            dminus += lastmaxe - pt.ele
        return (dplus,dminus)
    def ComputeTimes(self):
        '''For each point, compute time elasped since the first point in seconds'''
        timefirst = self.ptlist[0].datetime
        return map(lambda pt: TimeDeltaToSeconds(pt.datetime-timefirst),self.ptlist)
    def ComputeLengthFromSpd(self):
        "Compute track length by integrating speed"
        if len(self.ptlist)<2:
            return 0.0
        if self.ptlist[0].spdunit!='m/s':
            raise ValueError(gettext('Unit of points speed must be m/s'))
        return fsum(TimeDeltaToSeconds(self.ptlist[i+1].datetime - self.ptlist[i].datetime) * self.ptlist[i].spd for i in range(len(self.ptlist) - 1))
    def __ComputeDistancesCache(self):
        # If cache is empty or points have been added or removed
        if self.dists==None or len(self.ptlist)!=len(self.dists):
            self.dists=[0.0]
            if len(self.ptlist)>5000: # Vincenty more precise but too slow for long tracks
                for i in range(1,len(self.ptlist)):
                    self.dists.append(GeodeticDistGreatCircle(self.ptlist[i-1].lat,self.ptlist[i-1].lon,self.ptlist[i].lat,self.ptlist[i].lon))
            else:
                for i in range(1,len(self.ptlist)):
                    self.dists.append(GeodeticDistVincenty(self.ptlist[i-1].lat,self.ptlist[i-1].lon,self.ptlist[i].lat,self.ptlist[i].lon))
    def ComputeLengthFromDist(self):
        "Compute track length by summing distances"
        self.__ComputeDistancesCache()
        out = fsum(self.dists)
        return out
    def ComputePolar(self,nbstep,spdthreshold=0.0,spdunit='m/s',nbptsthreshold=1):
        '''Compute a Polar (speeds by angle) returns a tuple: (angles, mean seepds, max speeds)'''
        maxspds = []
        meanspds = []
        angles = []
        for angle in SmartRange(0,360,nbstep):
            if angle>0:
                maxspd = 0.0
                sectorspds = []
                for pt in self.ptlist:
                    if pt.course >= prevangle and pt.course < angle and pt.spd>=spdthreshold:
                        sectorspds.append(pt.spd)
                        if pt.spd>maxspd:
                            maxspd = pt.spd
                if len(sectorspds)>=nbptsthreshold:
                    meanspd = Mean(sectorspds)
                else:
                    meanspd = 0.0
                angles.append(prevangle)
                if spdunit=='m/s':
                    meanspds.append(meanspd)
                    maxspds.append(maxspd)
                else:
                    meanspds.append(MetersPerSecToSpdunit(meanspd,spdunit))
                    maxspds.append(MetersPerSecToSpdunit(maxspd,spdunit))
            prevangle = angle
        return (angles,meanspds,maxspds)
    def ComputeBikePower2(self,vertthreshold,horithreshold,weight=80.0):
        slopes = self.ComputeMeanSlope(vertthreshold,horithreshold)
        out = []
        powerintegbuffer = [0.0]
        for i in range(0,len(self.ptlist)):
            out.append(BikePower(powerintegbuffer,self.ptlist[i].spd, slopes[i], weight))
        return out
    def GetEleFromDEM(self):
        '''Gets elevations from Digital Elevation Model instead of getting it from GPS input file'''
        # Get from dem
        GetEleFromLatLonList(self.ptlist,True)
    def ApplySpeedFilter(self):
        # Apply filter in case of bad signal
        previous = self.ptlist[0].spd
        if self.spdcomputed:
            for pt in self.ptlist:
                pt.spd = previous + (pt.spd - previous)/5
                pt.spd_converted = {'m/s': pt.spd}
                previous = pt.spd
    def __ComputeSpeedWhenNeeded(self, force=False):
        '''Compute speeds in case it is not provided or if force argument is True'''
        if self.nospeeds:
            return	
        self.__ComputeDistancesCache()
        self.spdcomputed = False
        i = 0
        if self.ptlist[i].spd==None or self.ptlist[i].spd<0.0 or force:
            self.ptlist[i].spd = 0.0
            self.ptlist[i].spdunit = 'm/s'
            self.ptlist[i].spd_converted = {'m/s': self.ptlist[i].spd}
        for i in range(1,len(self.ptlist)):
            if self.ptlist[i].spd==None or self.ptlist[i].spd<0.0 or force:
                self.spdcomputed = True
                if self.ptlist[i].datetime==None or self.ptlist[i-1].datetime==None:
                    self.ptlist[i].spd = -1.0
                    self.nospeeds = True
                else:
                    t = TimeDeltaToSeconds(self.ptlist[i].datetime - self.ptlist[i-1].datetime)
                    if t > 0.0:
                        self.ptlist[i].spd = self.dists[i] / t
                    else:
                        # avoid division by zero: infinite speed is set to zero
                        self.ptlist[i].spd = 0.0
                    self.ptlist[i].spdunit = 'm/s'
                    self.ptlist[i].spd_converted = {'m/s': self.ptlist[i].spd}
    def __ComputeCourseWhenNeeded(self):
        'Compute course in case it is not provided'
        if len(self.ptlist) < 2:
            self.ptlist[0].course = 0
        all_course_zero = True
        for pt in self.ptlist:
            if pt.course != 0:
                all_course_zero = False
        for i in range(0,len(self.ptlist)-1):
            if self.ptlist[i].course==None or all_course_zero:
                self.ptlist[i].course = GeodeticCourse(self.ptlist[i].lat,self.ptlist[i].lon,self.ptlist[i+1].lat,self.ptlist[i+1].lon)
        if self.ptlist[-1].course==None:
            if len(self.ptlist) > 1:
                self.ptlist[-1].course = self.ptlist[-2].course
            else:
                self.ptlist[-1].course = 0
    def __FillEleWhenNeeded(self):
        # TODO : add interpolation
        prevele = 0
        for pt in self.ptlist:
            if pt.ele==None:
                pt.ele = prevele
            prevele = pt.ele
    def __ComputedSpeedDontOverWrite(self):
        self.__ComputeDistancesCache()
        out = []
        for i in range(0,len(self.ptlist)-1):
            if self.ptlist[i].datetime==None or self.ptlist[i+1].datetime==None:
                return None
            else:
                d = TimeDeltaToSeconds(self.ptlist[i+1].datetime-self.ptlist[i].datetime)
                if d > 0:
                    spd = self.dists[i+1] / d
                else:
                    # infinite speed is set to zero
                    spd = 0.0
            out.append(spd)
        # Handle last point
        if len(self.ptlist)<2:
            return None
        else:
            out.append(spd)
        return out
    def __CheckSpeedUnitAndCorrectIfNeeded(self):
        "Some gpx file contain speed in another unit that standard m/s. Check this"
        spdsfromfile = map(lambda pt: pt.spd,self.ptlist)
        spdsfromcomputation = self.__ComputedSpeedDontOverWrite()
        Log('Track::CheckSpeedUnitAndCorrectIfNeeded: after ComputedSpeedDontOverWrite')
        if spdsfromcomputation==None:
            return True
        sumdiff = 0.0
        sumspeed = 0.0
        i = 0
        for spdfromfile in spdsfromfile:
            if spdfromfile == None or spdfromfile == -1.0:
                return True
            sumdiff += abs(spdfromfile - spdsfromcomputation[i])
            sumspeed += spdsfromcomputation[i]
            i += 1
        # first check is to prevent division by zero
        if sumspeed > 0.0 and sumdiff / sumspeed > 0.8:
            # More than 80% diff => overwrite speeds by the ones from computation
            for j in range(0,i):
                self.ptlist[j].spd = spdsfromcomputation[j]
                self.ptlist[j].spdunit = 'm/s'
            return False
        return True
    def ComputePolarDist(self,nbstep):
        '''For each angle between 0 and 360, compute the distance covered in this direction.
           Usefull for computing polar diagrams when we have no time/speed information.
           Return a tuple of two lists: angles and distances'''
        angles = list(SmartRange(0,360,nbstep))
        distances = [0 for _ in angles]
        prevpt = None
        for pt in self.ptlist:
            for i in range(0,len(angles)):
                if angles[i] > pt.course:
                    if prevpt != None:
                        distances[i] += pt.Distance(prevpt)
                    break
            prevpt = pt
        return (angles,distances)
    def IsOnSeveralDays(self):
        if len(self.ptlist)>0 and hasattr(self.ptlist[-1],'datetime') and hasattr(self.ptlist[0],'datetime'):
            return (self.ptlist[-1].datetime.day!=self.ptlist[0].datetime.day)or(self.ptlist[-1].datetime.month!=self.ptlist[0].datetime.month)or(self.ptlist[-1].datetime.year!=self.ptlist[0].datetime.year)
        else:
            # if there is no datetime, we display the track as if it wasn't on several days
            return False
    def hasHeartRate(self):
        return sum(map(lambda pt:hasattr(pt,'hr'),self.ptlist))>len(self.ptlist)/2
    def getHeartRate(self):
        # TODO replace it by same algorithm as in fitparser
        prev_hr = None
        for pt in self.ptlist:
            if not hasattr(pt,'hr'):
                if prev_hr==None:
                    for pt2 in self.ptlist:
                        if hasattr(pt2,'hr'):
                            prev_hr = pt2.hr
                            break
                pt.hr = prev_hr
            prev_hr = pt.hr
        return map(lambda pt: pt.hr,self.ptlist)
    def ComputeEqDistancesFromSpd(self):
        '''Compute distance for each point from the beginning of the track, by integrating speed.
           Usefull for computations around speed which may be more precise than using distances'''
        out = [0.0]
        dst = 0.0
        for i in range(1,len(self.ptlist)):
            dst += self.ptlist[i].spd * TimeDeltaToSeconds(self.ptlist[i].datetime-self.ptlist[i-1].datetime)
            out.append(dst)
        return out
    def __AddOruxMapPauses(self):
        '''Some devices/applications detect and stop adding corresponding points in the track. 
           The issue is that it adds next moving point far away from where the pause was, making 
           the pause interpreted like a slow move to the next moving point. Correct it by adding 
           two points with zero speed for each detected pause'''
        out = []
        out_dists = []
        threshold_time = 2
        prevpt = None
        i = 0
        for pt in self.ptlist:
            # compute only from the second point
            if prevpt != None and pt.spd != None:
                delta = (pt.datetime - prevpt.datetime).seconds
                # pause detection: must last more than 2 seconds and the computed speed must be less than 20% of the speed of the two points
                if delta > threshold_time and GeodeticDistGreatCircle(prevpt.lat,prevpt.lon,pt.lat,pt.lon)/delta < min(prevpt.spd*0.2, pt.spd*0.2):
                    out.append(Point(prevpt.lat,prevpt.lon,prevpt.ele,0,prevpt.course,prevpt.datetime+timedelta(seconds=1)))
                    out_dists.append(0.0)
                    out.append(Point(pt.lat,pt.lon,pt.ele,0,pt.course,pt.datetime-timedelta(seconds=1)))
                    out_dists.append(0.0)
            out.append(pt)
            out_dists.append(self.dists[i])
            prevpt = pt
            i += 1
        self.ptlist = out
        self.dists = out_dists

def unittests():
    from gpxparser import ParseGpxFile
    ptlist = ParseGpxFile('uploads/10998bc80447c_0.gpx', 0, 0)
    track = Track(ptlist)
    print len(track)

    # Call each method of Track class
    track.GetSpeeds('m/s')
    track.GetElevations()
    track.CompressCopyPriority(10)
    print len(track)
    track.ConvertSpeed('km/h')
    track.RemoveStayingPoints4(10, 10, 1)
    print len(track)
    track.ComputeInstantVertSpeeds()
    track.ComputeMeanVertSpeeds(10)
    track.ComputeMeanSlope(10, 10)
    track.ComputeDistances()
    track.ComputeEleDiff(10)
    track.ComputeTimes()
    track.ComputeLengthFromSpd()
    track.ComputeLengthFromDist()
    track.ComputePolar(10)
    track.ComputeBikePower2(10, 10)
    track.ComputePolarDist(10)
    track.IsOnSeveralDays()
    track.hasHeartRate()
    track.getHeartRate()
    track.ComputeEqDistancesFromSpd()
    track.ApplySpeedFilter() #unused
    #track.GetEleFromDEM()

if __name__=='__main__':
    unittests()
