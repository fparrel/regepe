
from miscranges import frange6,SmartRange
from mathutil import Mean,GeodeticDistGreatCircle,GeodeticDistVincenty,GeodeticCourse,StrangeFilter
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
            #raise Exception('Cannot convert speed if speed is not provided')
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
        self.ComputeSpeedWhenNeeded(force=forcespdcomp)
        self.ComputeCourseWhenNeeded()
        self.FillEleWhenNeeded()
        Log('Track: CheckSpeedUnitAndCorrectIfNeeded')
        self.CheckSpeedUnitAndCorrectIfNeeded()
        if not self.nospeeds:
            self.AddOruxMapPauses()
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
    def CompressPtlistOld(self,nbpts):
        "Return a list of id built by keeping only 'nbpts' points from the list of points"
        idlist = map(int, frange6(0,len(self.ptlist),float(len(self.ptlist))/float(nbpts)))
        return idlist
    def CompressPtlist2(self,nbpts):
        "Return a list of points built by keeping only 'nbpts' points from the list of points"
        idlist = list(SmartRange(0,len(self.ptlist)-1,nbpts))
        #print('CompressPtlist2: len(idlist)=%d' % len(idlist))
        return idlist
    def CompressPtlist(self,nbpts):
        "Return a list of points built by keeping only 'nbpts' points from the list of points"
        idlist = list(map(int, frange6(0,len(self.ptlist),float(len(self.ptlist))/float(nbpts))))
        # always include last point
        if idlist[len(idlist)-1]!=len(self.ptlist)-1:
            idlist.append(len(self.ptlist)-1)
        return idlist
    def MostImportant(self,a,b):
        maxprio = 0
        maxprio_i = -1
        for i in range(a,b):
            if self.ptlist[i].priority>maxprio:
                maxprio = self.ptlist[i].priority
                maxprio_i = i
        if maxprio>0:
            #print('MostImportant'+str(i)+': '+str(self.ptlist[i])+' spd='+str(self.ptlist[i].spd))
            return maxprio_i
        else:
            #print('MostImportant'+str(a))
            return a
    def CompressPtlistPriority(self,nbpts):
        "Return a list of points built by keeping only 'nbpts' points from the list of points"
        idlist = []
        previ = -1
        for i in frange6(0,len(self.ptlist),float(len(self.ptlist))/float(nbpts)):
            if previ>-1:
                idlist.append(self.MostImportant(int(previ),int(i)))
            previ = i
        # always include last point
        if idlist[len(idlist)-1]!=len(self.ptlist)-1:
            idlist.append(len(self.ptlist)-1)
        return idlist
    def CompressPtlistPriority2(self,nbpts):
        "Return a list of points built by keeping only 'nbpts' points from the list of points"
        nbptsinitial = nbpts
        # decrease total number of points by the number of important points
        for i in range(0,len(self.ptlist)):
            if self.ptlist[i].priority>1:
                nbpts -= 1
        if nbptsinitial - nbpts > nbptsinitial / 2:
            Warn('WARNING: CompressPtlistPriority2: use standard compression')
            # If too much important points, use standard compression
            return self.CompressPtlist(nbptsinitial)
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
        #print('CompressPtlistPriority2 len=%d' % len(idlistnew))
        return idlistnew
    def CompressCopy(self,nbpts):
        "Return another Track with only 'nbpts'"
        ptindexlist = self.CompressPtlist(nbpts)
        return Track([self.ptlist[i] for i in ptindexlist],self.bounds,ptindexlist)
    def CompressCopyPriority(self,nbpts):
        "Return another Track with only 'nbpts'"
        ptindexlist = self.CompressPtlistPriority2(nbpts)
        out = Track([self.ptlist[i] for i in ptindexlist],self.bounds,ptindexlist)
        return out
    def __len__(self):
        "Return the number of points in list"
        return len(self.ptlist)
    def ConvertSpeed(self,unit):
        "Convert list of points' speed unit to 'unit'"
        for pt in self.ptlist:
            pt.ConvertSpeed(unit)
    def RemoveStayingPointsFromDistance(self,threshold):
        "Remove the points when GPS is staying at the same place"
        self.ComputeDistancesCache()
        idlistnew = []
        for i in range(0,len(self.ptlist)-1):
            if self.dists[i+1]>threshold:
                idlistnew.append(i+1)
        ptlist_new = [self.ptlist[i] for i in idlistnew]
        if self.dists!=None:
            dists_new=[]
            for i in range(1,len(idlistnew)):
                if idlistnew[i]==idlistnew[i-1]+1:
                    dists_new.append(self.dists[i])
                else:
                    dists_new.append(GeodeticDistVincenty(self.ptlist[idlistnew[i-1]].lat,self.ptlist[idlistnew[i-1]].lon,self.ptlist[idlistnew[i]].lat,self.ptlist[idlistnew[i]].lon))
            self.dists = dists_new
        self.ptlist = ptlist_new
    def RemoveStayingPointsFromSpeed(self,threshold):
        "Remove the points when GPS is staying at the same place"
        idlistnew = []
        for i in range(0,len(self.ptlist)):
            if self.ptlist[i].spd>threshold:
                idlistnew.append(i+1)
        ptlist_new = [self.ptlist[i] for i in idlistnew]
        if self.dists!=None:
            dists_new=[]
            for i in range(1,len(idlistnew)):
                if idlistnew[i]==idlistnew[i-1]+1:
                    dists_new.append(self.dists[i])
                else:
                    dists_new.append(GeodeticDistVincenty(self.ptlist[idlistnew[i-1]].lat,self.ptlist[idlistnew[i-1]].lon,self.ptlist[idlistnew[i]].lat,self.ptlist[idlistnew[i]].lon))
            self.dists = dists_new
        self.ptlist = ptlist_new
    def RemoveStayingPoints3(self,thresholddist,thresholdtime,thresholdspeed):
        "Remove the points when GPS is staying at the same place"
        if (self.nospeeds):
            return
        pauses = []
        removedptsidlist = []
        idlist = list(range(0,len(self.ptlist)))
        j = 0
        for i in range(0,len(self.ptlist)):
            if self.ptlist[j].Distance(self.ptlist[i])>thresholddist or self.ptlist[i].spd>thresholdspeed:
                # Check if the track stayed more than thresholdtime seconds
                #  under thresholdspeed and not moving farther than thresholddist
                #  to initial position
                if TimeDeltaToSeconds(self.ptlist[i].datetime - self.ptlist[j].datetime) > thresholdtime:
                    #print('DEBUG: RemoveStayingPoints3: pause found: %s %s' % (self.ptlist[j].datetime,self.ptlist[i].datetime))
                    #print('DEBUG: dist:%dm time=%ds' % (self.ptlist[j].Distance(self.ptlist[i]),TimeDeltaToSeconds(self.ptlist[i].datetime - self.ptlist[j].datetime)))
                    for k in range(j,i):
                        idlist.remove(k)
                        removedptsidlist.append(k)
                j = i
        removedptsidlistcpy = removedptsidlist[:]
        lastid = -2
        first = True
        for i in removedptsidlist:
            if i!=lastid+1:
                if not first:
                    #print('end pause:'+str(self.ptlist[lastid]))
                    pauses.append((curpausebegin,self.ptlist[lastid]))
                    self.ptlist[lastid].ChangeSpeed(0.0)
                    self.ptlist[lastid].priority = 2
                    try:
                        removedptsidlistcpy.remove(lastid)
                    except ValueError:
                        pass
                #print('begin pause:'+str(self.ptlist[i]))
                curpausebegin = self.ptlist[i]
                self.ptlist[i].ChangeSpeed(0.0)
                self.ptlist[i].priority = 2
                removedptsidlistcpy.remove(i)
                first = False
            lastid = i
        if not first:
            #print('end pause:'+str(self.ptlist[i]))
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
                    dists_new.append(self.dists[i])
                else:
                    dists_new.append(GeodeticDistVincenty(self.ptlist[idlistnew[i-1]].lat,self.ptlist[idlistnew[i-1]].lon,self.ptlist[idlistnew[i]].lat,self.ptlist[idlistnew[i]].lon))
            self.dists = dists_new
        self.ptlist = ptlist_new
        return pauses
    def RemoveStayingPoints4(self,thresholddist,thresholdtime,thresholdspeed):
        "Remove the points when GPS is staying at the same place"
        if (self.nospeeds):
            return
        pauses = []
        removedptsidlist = []
        idlist = list(range(0,len(self.ptlist)))
        j = 0
        i = 0
        #for i in range(0,len(self.ptlist)):
        while i < len(self.ptlist):
            if TimeDeltaToSeconds(self.ptlist[i].datetime - self.ptlist[j].datetime) > thresholdtime:
                # Check if the track stayed more than thresholdtime seconds
                #  under thresholdspeed and not moving farther than thresholddist
                #  to initial position
                if self.ptlist[j].Distance(self.ptlist[i])<thresholddist and max(self.ptlist[k].spd for k in range(j,i+1))<thresholdspeed:
                    while i < len(self.ptlist) and self.ptlist[j].Distance(self.ptlist[i])<thresholddist and self.ptlist[i].spd<thresholdspeed:
                        i += 1
                    i -= 1
                    #print('DEBUG: RemoveStayingPoints4: pause found: %s %s' % (self.ptlist[j].datetime,self.ptlist[i].datetime))
                    #print('DEBUG: dist:%dm time=%ds' % (self.ptlist[j].Distance(self.ptlist[i]),TimeDeltaToSeconds(self.ptlist[i].datetime - self.ptlist[j].datetime)))
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
                    #print('end pause:'+str(self.ptlist[lastid]))
                    pauses.append((curpausebegin,self.ptlist[lastid]))
                    self.ptlist[lastid].ChangeSpeed(0.0)
                    self.ptlist[lastid].priority = 2
                    try:
                        removedptsidlistcpy.remove(lastid)
                    except ValueError:
                        pass
                #print('begin pause:'+str(self.ptlist[i]))
                curpausebegin = self.ptlist[i]
                self.ptlist[i].ChangeSpeed(0.0)
                self.ptlist[i].priority = 2
                removedptsidlistcpy.remove(i)
                first = False
            lastid = i
        if not first:
            #print('end pause:'+str(self.ptlist[i]))
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
                try:
                    vertspd.append((pt.ele-prevpt.ele)/TimeDeltaToSeconds(pt.datetime-prevpt.datetime))
                except ZeroDivisionError:
                    vertspd.append(0.0)
            prevpt = pt
        return vertspd
    def ComputeVertSpeeds2(self):
        "Compute list of instant vertical speeds in m/s"
        ele = StrangeFilter(self.GetElevations())
        out = []
        for i in range(0,len(self)-1):
            t = TimeDeltaToSeconds(self.ptlist[i+1].datetime-self.ptlist[i].datetime)
            if t==0.0:
                vertspd = 0.0
            else:
                vertspd = (ele[i+1]-ele[i])/t
            out.append(vertspd)
        return out
    def ComputeMeanVertSpeeds(self,threshold):
        out = []
        i = 0
        #debuglen = 0
        #print('ComputeMeanVertSpeeds')
        #for pt in self.ptlist:
        #    print(pt)
        #print('first='+str(self.ptlist[0]))
        for up_down in self.GetUpsAndDowns(threshold):
            try:
                vspd = (up_down[1].ele-up_down[0].ele)/TimeDeltaToSeconds(up_down[1].datetime-up_down[0].datetime)
            except ZeroDivisionError:
                vspd = 0.0
            #print('up_down=' + str(up_down[0]) + '-->' + str(up_down[1]) + ' vspd=' + str(vspd))
            buf = []
            while self.ptlist[i]!=up_down[1]:
                buf.append(vspd)
                i += 1
            #print('len(buf)=%d' % (len(buf)))
            #debuglen += len(buf)
            out += buf
        out.append(out[len(out)-1])
        #print('debuglen=%d' % (debuglen))
        #print('last='+str(self.ptlist[len(self.ptlist)-1]))
        #print('ComputeMeanVertSpeeds: len(self.ptlist)=%d len(out)=%d' % (len(self.ptlist),len(out)))
        assert(len(self.ptlist)==len(out))
        return out
    def ComputeSlope(self):
        "Compute list of slopes"
        self.ComputeDistancesCache()
        # Slops already computed, return them
        if len(self.ptlist)>0 and hasattr(self.ptlist[0],"slope"):
            return [lambda pt:pt.slope for pt in self.ptlist]
        # compute slopes
        prevpt = None
        i = 0
        slopes = []
        for pt in self.ptlist:
            if prevpt==None:
                slope = 0.0
            else:
                if self.dists[i]<1.0:
                    slope = 0.0
                else:
                    try:
                        slope = (pt.ele-prevpt.ele)/self.dists[i]
                    except ZeroDivisionError:
                        slope = 0.0
                    # Limit to +-100% (+-45 degrees)
                    if slope>1.0:
                        slope = 1.0
                    elif slope<-1.0:
                        slope = -1.0
            slopes.append(slope)
            pt.slope = slope
            prevpt = pt
            i+=1
        return slopes
    def ComputeSlope2(self):
        "Compute list of slopes"
        self.ComputeDistancesCache()
        ele = StrangeFilter(self.GetElevations())
        out = []
        for i in range(0,len(self)-1):
            dist = self.dists[i+1]
            if dist==0.0:
                slope = 0.0
            else:
                slope = ele[i+1]-ele[i]/dist
            out.append(slope)
        return out
    def ComputeMeanSlope(self,vertthreshold,horithreshold):
        out = []
        i = 0
        for up_down in self.GetUpsAndDowns(vertthreshold):
            if up_down[1].Distance(up_down[0])>=horithreshold:
                try:
                    slope = (up_down[1].ele-up_down[0].ele)/up_down[1].DistancePrecise(up_down[0])
                except ZeroDivisionError:
                    slope = 0.0
            else:
                slope = 0.0
            #if slope>0.1:
            #    print('here')
            #    print(up_down[0])
            #    print(up_down[1])
            #    print('distance = %f' % up_down[1].Distance(up_down[0]))
            buf = []
            while self.ptlist[i]!=up_down[1]:
                buf.append(slope)
                i += 1
            out += buf
        out.append(out[len(out)-1])
        assert(len(self.ptlist)==len(out))
        return out
    def ComputeBikePower(self,weight):
        "Comput list of instant power in watts"
        slope = self.ComputeSlope()
        return [self.ptlist[i].spd * self.ptlist[i].spd * Track.bike_power_friction + self.ptlist[i].spd * bike_power_climbing * slope[i] for i in range(0,len(self.ptlist))]
    def ComputeDistances(self):
        "Compute list of distances from the begin of track segment"
        self.ComputeDistancesCache()
        out = []
        cptr = 0.0
        for i in range(0,len(self.ptlist)):
            cptr+=self.dists[i]
            out.append(cptr)
        return out
    def ComputeEleDiffRaw(self):
        "Compute D+ and D-"
        up = 0.0
        down = 0.0
        prevpt = None
        for pt in self.ptlist:
            if prevpt==None:
                up = 0.0
                down = 0.0
            else:
                d = pt.ele - prevpt.ele
                if d>0.0:
                    up += d
                else:
                    down += -d
            prevpt = pt
        return (up,down)
    def GetUpsAndDowns(self,threshold):
        p1down = self.ptlist[0]
        p2down = self.ptlist[0]
        p1up = self.ptlist[0]
        p2up = self.ptlist[0]
        out = []
        last_up_or_down = 0
        current_up_or_down = 0
        for pt in self.ptlist:
            #print('   '+str(pt))
            #print('   current_up_or_down=%d' % (current_up_or_down))
            #print('   p1down=%s p2down=%s p1up=%s p2up=%s' % (p1down,p2down,p1up,p2up))
            if current_up_or_down==0:
                if pt.ele - p1down.ele < -threshold:
                    current_up_or_down = 1
                elif pt.ele - p1up.ele > threshold:
                    current_up_or_down = 2
            elif current_up_or_down==1:
                if pt.ele < p2down.ele:
                    p2down = pt
                elif pt.ele - p2down.ele > threshold:
                    #print('down('+str(p1down)+','+str(p2down))
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
                    #print('up('+str(p1up)+','+str(p2up))
                    out.append((p1up,p2up,2))
                    p1down = p2up
                    p2down = p2up
                    p1up = p2up
                    last_up_or_down = 2
                    current_up_or_down = 0   
        if last_up_or_down==1:
            p2up = pt
            #print('up('+str(p1up)+','+str(p2up))
            out.append((p1up,p2up,2))
        if last_up_or_down==2:
            p2down = pt
            #print('down('+str(p1down)+','+str(p2down))
            out.append((p1down,p2down,1))
        if last_up_or_down==0:
            #print('flat('+str(p1down)+','+str(pt))
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
            if pt.ele>maxe:
                maxe = pt.ele
            if pt.ele<mine:
                mine = pt.ele
            diff = pt.ele - ele
            if abs(diff) > threshold:
                if diff<0:
                    if lastdiff==1:
                        #print 'up down',lastmine,maxe
                        lastmaxe = maxe
                        dplus += maxe - lastmine
                        #print 'd+: %d' % (maxe - lastmine)
                    lastdiff = -1
                else:
                    if lastdiff==-1:
                        #print 'down up',mine,lastmaxe
                        lastmine = mine
                        dminus += lastmaxe - mine
                        #print 'd-: %d' % (lastmaxe - mine)
                    lastdiff = 1
                ele = pt.ele
                maxe = ele
                mine = ele
        if lastdiff==1:
            #print 'end up',lastmine,pt.ele
            dplus += pt.ele - lastmine
        if lastdiff==-1:
            #print 'end down',lastmaxe,pt.ele
            dminus += lastmaxe - pt.ele
        return (dplus,dminus)
    def ComputeEleDiffOld(self,threshold):
        "Compute D+ and D-"
        p1down = self.ptlist[0]
        p2down = self.ptlist[0]
        p1up = self.ptlist[0]
        p2up = self.ptlist[0]
        down = 0.0
        up = 0.0
        last_up_or_down = 0
        current_up_or_down = 0
        for pt in self.ptlist:
            #print('   '+str(pt))
            #print('   current_up_or_down=%d' % (current_up_or_down))
            #print('   p1down=%s p2down=%s p1up=%s p2up=%s' % (p1down,p2down,p1up,p2up))
            if current_up_or_down==0:
                if pt.ele - p1down.ele < -threshold:
                    current_up_or_down = 1
                elif pt.ele - p1up.ele > threshold:
                    current_up_or_down = 2
            elif current_up_or_down==1:
                if pt.ele < p2down.ele:
                    p2down = pt
                elif pt.ele - p2down.ele > threshold:
                    #print('down('+str(p1down)+','+str(p2down))
                    down += p1down.ele - p2down.ele
                    p1up = p2down
                    p2up = p2down
                    p1down = p2down
                    last_up_or_down = 1
                    current_up_or_down = 0
            elif current_up_or_down==2:
                if pt.ele > p2up.ele:
                    p2up = pt
                elif pt.ele - p2up.ele < -threshold:
                    #print('up('+str(p1up)+','+str(p2up))
                    up += p2up.ele - p1up.ele
                    p1down = p2up
                    p2down = p2up
                    p1up = p2up
                    last_up_or_down = 2
                    current_up_or_down = 0   
        if last_up_or_down==1:
            p2up = pt
            #print('up('+str(p1up)+','+str(p2up))
            down += p1down.ele - p2down.ele
        if last_up_or_down==2:
            p2down = pt
            #print('down('+str(p1down)+','+str(p2down))
            up += p2up.ele - p1up.ele
        if last_up_or_down==0:
            pass
            #print('flat('+str(p1down)+','+str(pt))
        return (up,down)
    def ComputeTimes(self):
        timefirst = self.ptlist[0].datetime
        return map(lambda pt: TimeDeltaToSeconds(pt.datetime-timefirst),self.ptlist)
    def ComputeLengthFromSpd(self):
        "Compute track length by integrating speed"
        if len(self.ptlist)==0:
            return 0.0
        if self.ptlist[0].spdunit!='m/s':
            raise ValueError(gettext('Unit of points speed must be m/s'))
        # if you know how to optimize the following loop (sum,map,list...), send me a mail
        out = 0.0
        for i in range(0,len(self.ptlist)-1):
            out += TimeDeltaToSeconds(self.ptlist[i+1].datetime-self.ptlist[i].datetime)*self.ptlist[i].spd
        return out
    def ComputeDistancesCache(self):
        if self.dists==None or not(len(self.ptlist)==len(self.dists)):
            self.dists=[0.0]
            if len(self.ptlist)>5000: #vincenty is too slow for long tracks
                for i in range(1,len(self.ptlist)):
                    self.dists.append(GeodeticDistGreatCircle(self.ptlist[i-1].lat,self.ptlist[i-1].lon,self.ptlist[i].lat,self.ptlist[i].lon))
            else:
                for i in range(1,len(self.ptlist)):
                    self.dists.append(GeodeticDistVincenty(self.ptlist[i-1].lat,self.ptlist[i-1].lon,self.ptlist[i].lat,self.ptlist[i].lon))
    def ComputeLengthFromDist(self):
        "Compute track length by summing distances"
        self.ComputeDistancesCache()
        out = fsum(self.dists)
        return out
        #out = 0.0
        #for i in range(0,len(self.ptlist)-1):
        #    out += GeodeticDist(self.ptlist[i+1].lat,self.ptlist[i+1].lon,self.ptlist[i].lat,self.ptlist[i].lon)
        #return out
    def ComputePolar(self,nbstep,spdthreshold=0.0,spdunit='m/s',nbptsthreshold=1):
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
        #print('DEBUG: model.py: Track: GetEleFromDEM()')
        # Get from dem
        GetEleFromLatLonList(self.ptlist,True)
    def ComputeSpeedWhenNeededWithFilter(self,force=False):
        self.ComputeDistancesCache()
        self.spdcomputed = False
        # Compute speeds in case it is not provided
        for i in range(0,len(self.ptlist)-1):
            if self.ptlist[i].spd==None or self.ptlist[i].spd<0.0 or force:
                self.spdcomputed = True
                if self.ptlist[i].datetime==None or self.ptlist[i+1].datetime==None:
                    self.ptlist[i].spd = -1.0
                    self.nospeeds = True
                    #print('DEBUG: ComputeSpeedWhenNeeded: nospeeds = True')
                    #raise Exception("Cannot compute speeds if datetime is not provided")
                else:
                    try:
                        self.ptlist[i].spd = self.dists[i+1]/TimeDeltaToSeconds(self.ptlist[i+1].datetime-self.ptlist[i].datetime)
                        self.ptlist[i].spdunit = 'm/s'
                        self.ptlist[i].spd_converted = {'m/s': self.ptlist[i].spd}
                    except ZeroDivisionError:
                        self.ptlist[i].spd = 0.0
                        self.ptlist[i].spdunit = 'm/s'
                        self.ptlist[i].spd_converted = {'m/s': self.ptlist[i].spd}
                #print 'DEBUG: Compute speed "%s"' % self.ptlist[i].spd
        # Handle last point
        if self.ptlist[len(self.ptlist)-1].spd==None:
            if len(self.ptlist)<2:
                self.nospeeds = True
            else:
                self.ptlist[len(self.ptlist)-1].spd = self.ptlist[len(self.ptlist)-2].spd
                self.ptlist[len(self.ptlist)-1].spdunit = self.ptlist[len(self.ptlist)-2].spdunit
                self.ptlist[len(self.ptlist)-1].spd_converted = {'m/s': self.ptlist[len(self.ptlist)-1].spd}
        # Apply filter in case of bad signal
        previous = self.ptlist[0].spd
        if self.spdcomputed:
            for pt in self.ptlist:
                pt.spd = previous + (pt.spd - previous)/5
                pt.spd_converted = {'m/s': pt.spd}
                previous = pt.spd
    def ComputeSpeedWhenNeeded(self,force=False):
        self.ComputeDistancesCache()
        self.spdcomputed = False
        # Compute speeds in case it is not provided
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
                    t=TimeDeltaToSeconds(self.ptlist[i].datetime-self.ptlist[i-1].datetime)
                    if t==0.0:
                        self.ptlist[i].spd = 0.0
                    else:
                        self.ptlist[i].spd = self.dists[i]/t
                    self.ptlist[i].spdunit = 'm/s'
                    self.ptlist[i].spd_converted = {'m/s': self.ptlist[i].spd}
    def ComputeCourseWhenNeeded(self):
        # Compute course in case it is not provided
        if len(self.ptlist)<2:
            self.ptlist[0].course = 0
        all_course_zero = True
        for pt in self.ptlist:
            if pt.course!=0:
                all_course_zero = False
        for i in range(0,len(self.ptlist)-1):
            if self.ptlist[i].course==None or all_course_zero:
                self.ptlist[i].course = GeodeticCourse(self.ptlist[i].lat,self.ptlist[i].lon,self.ptlist[i+1].lat,self.ptlist[i+1].lon)
        if self.ptlist[len(self.ptlist)-1].course==None:
            self.ptlist[len(self.ptlist)-1].course = self.ptlist[len(self.ptlist)-2].course
    def FillEleWhenNeeded(self):
        prevele = 0
        for pt in self.ptlist:
            if pt.ele==None:
                pt.ele = prevele
            prevele = pt.ele
    def ComputedSpeedDontOverWrite(self):
        self.ComputeDistancesCache()
        out = []
        for i in range(0,len(self.ptlist)-1):
            if self.ptlist[i].datetime==None or self.ptlist[i+1].datetime==None:
                return None
            else:
                try:
                    spd = self.dists[i+1]/TimeDeltaToSeconds(self.ptlist[i+1].datetime-self.ptlist[i].datetime)
                except ZeroDivisionError:
                    spd = 0.0
            out.append(spd)
        # Handle last point
        if len(self.ptlist)<2:
            return None
        else:
            out.append(spd)
        return out
    def CheckSpeedUnitAndCorrectIfNeeded(self):
        "Some gpx file contain speed in another unit that standard m/s. Check this"
        spdsfromfile = map(lambda pt: pt.spd,self.ptlist)
        spdsfromcomputation = self.ComputedSpeedDontOverWrite()
        Log('Track::CheckSpeedUnitAndCorrectIfNeeded: after ComputedSpeedDontOverWrite')
        if spdsfromcomputation==None:
            return True
        sumdiff = 0.0
        sumspeed = 0.0
        i = 0
        for spdfile in spdsfromfile:
            if spdfile==None:
                return True
            if spdfile==-1.0:
                return True
            sumdiff += abs(spdfile-spdsfromcomputation[i])
            sumspeed += spdsfromcomputation[i]
            i += 1
        if sumspeed==0.0:
            return True
        #print('DEBUG: CheckSpeedUnit: %s' % (sumdiff/sumspeed))
        if sumdiff/sumspeed>0.8:
            # More than 80% diff
            for j in range(0,i):
                self.ptlist[j].spd = spdsfromcomputation[j]
                self.ptlist[j].spdunit = 'm/s'
            return False
        return True
    def ComputePolarDist(self,nbstep):
        angles = list(SmartRange(0,360,nbstep))
        distances = [0 for a in angles]
        prevpt = None
        for pt in self.ptlist:
            for i in range(0,len(angles)):
                if angles[i]>pt.course:
                    if prevpt!=None:
                        distances[i] += pt.Distance(prevpt)
                    break
            prevpt = pt
        return (angles,distances)
    def IsOnSeveralDays(self):
        try:
            return (self.ptlist[-1].datetime.day!=self.ptlist[0].datetime.day)or(self.ptlist[-1].datetime.month!=self.ptlist[0].datetime.month)or(self.ptlist[-1].datetime.year!=self.ptlist[0].datetime.year)
        except:
            return False
    def hasHeartRate(self):
        return sum(map(lambda pt:hasattr(pt,'hr'),self.ptlist))>len(self.ptlist)/2
    def getHeartRate(self):
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
        out = [0.0]
        dst = 0.0
        for i in range(1,len(self.ptlist)):
            dst += self.ptlist[i].spd * TimeDeltaToSeconds(self.ptlist[i].datetime-self.ptlist[i-1].datetime)
            out.append(dst)
        return out
    def AddOruxMapPauses(self):
        out=[]
        out_dists=[]
        threshold_time = 2
        prevpt = None
        i=0
        for pt in self.ptlist:
            #print prevpt,pt.spd
            if prevpt!=None and pt.spd!=None:
                delta=(pt.datetime - prevpt.datetime).seconds
                if delta > threshold_time and GeodeticDistGreatCircle(prevpt.lat,prevpt.lon,pt.lat,pt.lon)/delta<prevpt.spd*0.2 and GeodeticDistGreatCircle(prevpt.lat,prevpt.lon,pt.lat,pt.lon)/delta<pt.spd*0.2:
                    #print 'poz',delta
                    out.append(Point(prevpt.lat,prevpt.lon,prevpt.ele,0,prevpt.course,prevpt.datetime+timedelta(seconds=1)))
                    out_dists.append(0.0)
                    out.append(Point(pt.lat,pt.lon,pt.ele,0,pt.course,pt.datetime-timedelta(seconds=1)))
                    out_dists.append(0.0)
            out.append(pt)
            out_dists.append(self.dists[i])
            prevpt = pt
            i+=1
        self.ptlist = out
        self.dists = out_dists

if __name__=='__main__':
    from gpxparser import ParseGpxFile
    ptlist = ParseGpxFile('../../lamp-prod/cgi-bin/submit/56d74ad0cb0ec_0.gpx',0,0)
    print len(ptlist)
    track = Track(ptlist)
    print track.ComputeLengthFromDist()
