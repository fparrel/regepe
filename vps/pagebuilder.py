
from miscranges import ExtendRange,ExtendRange5
from conversions import MetersToNauticalMiles
from log import Log
import datetime
import time
from figures import Figures
from math import floor,ceil

## PAGE BUILDER CLASSES AND FUNCTION ##

def ChartPt2pxToString(pt2px):
    if pt2px==None:
        return 'null'
    else:
        return '['+','.join([str(val) for val in pt2px])+']'

def spd2str(spd):
    if spd==None:
        return '-1.0'
    else:
        return '%.2f' % spd


def PtToString(pt,angle_factor,spdunit,wdate):
    if wdate:
        if hasattr(pt,'hr'):
            return '\t[%f,%f,"%s",%d,%s,%d,%d,%d]' % (pt.lat,pt.lon,pt.GetDateTimeString(),pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course,pt.hr)
        else:
            return '\t[%f,%f,"%s",%d,%s,%d,%d]'      % (pt.lat,pt.lon,pt.GetDateTimeString(),pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course)
    else:
        if hasattr(pt,'hr'):
            return '\t[%f,%f,"%s",%d,%s,%d,%d,%d]' % (pt.lat,pt.lon,pt.GetTimeString(),      pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course,pt.hr)
        else:
            return '\t[%f,%f,"%s",%d,%s,%d,%d]'      % (pt.lat,pt.lon,pt.GetTimeString(),      pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course)

def BuildTrackPointsString(track,angle_factor,spdunit):
    wdate = track.IsOnSeveralDays()
    return ',\n'.join(map(lambda pt:PtToString(pt,angle_factor,spdunit,wdate),track.ptlist))

def ChartToJsonShort(chart):
    if (chart.charttype in ('title+string','polar')):
        return chart.ToHtml(-1)
    else:
        return '{"type":"%s","title":"%s","name":"%s"}'%(chart.charttype,chart.title,chart.name)

def BuildPage(track,charts,figures,spdunit,mapid,options):
    template = """{"type":"%(maptype)s","figures":%(figures)s,"chartdata":[%(chartsnameandmarginsize)s],
"nbpts": %(nbpts)d,
"spdunit": "%(spdunit)s",
"flat": %(flat)d,
"wind": %(wind)d,
"maxspd": %(maxspd)d,
"mapid": "%(mapid)s",
"centerlat":%(centerlat)f,
"centerlon":%(centerlon)f,
"minlat":%(minlat)f,
"minlon":%(minlon)f,
"maxlat":%(maxlat)f,
"maxlon":%(maxlon)f,
"points":[
%(trackpoints)s
],
"charts": [
%(charts)s
]}
   """
    xycharts = filter(lambda chart: isinstance(chart,MyXYChart), charts)
    charts_out = ',\n'.join(map(ChartToJsonShort,charts))
    chartsnameandmarginsize = ',\n'.join([chartobj.ToHtml(chartid) for (chartid,chartobj) in enumerate(charts)])
    [centerlat,centerlon] = track.bounds.GetCenter()
    nbpts = len(track.ptlist)
    angle_factor = 15 #arrowid = angle/angle_factor
    return template % { 'maptype': options['map_type'], \
                                    'figures': BuildFigures(figures,type), \
                                    'charts': charts_out, \
                                    'nbpts': nbpts, \
                                    'centerlat': centerlat, \
                                    'centerlon': centerlon, \
                                    'minlat': track.bounds.minlat, \
                                    'minlon': track.bounds.minlon, \
                                    'maxlat': track.bounds.maxlat, \
                                    'maxlon': track.bounds.maxlon, \
                                    'trackpoints': BuildTrackPointsString(track,angle_factor,spdunit), \
                                    'spdunit': spdunit, \
                                    'chartsnameandmarginsize': chartsnameandmarginsize, \
                                    'minspeed': min(map(lambda pt: pt.spd, track.ptlist)), \
                                    'maxspeed': max(map(lambda pt: pt.spd, track.ptlist)), \
                                    'flat': options['flat'], \
                                    'wind': options['wind'], \
                                    'maxspd': options['maxspd'], \
                                    'mapid': mapid}


def SelectValuesModulo(val,mod):
    if val % mod == 0:
        return val
    else:
        return ''


class MyChart:
    # imagefileurl
    # name
    # label
    def __init__(self,imagefileurl,name,label):
        self.imagefileurl = imagefileurl
        self.name = name
        self.label = label
    def ToHtml(self,chartid):
        pass


class MyPolar(MyChart):
    "Build and keep a polar chart"
    def __init__(self,data,imagefileurl,name,label,unit_y,type= 'ggl'):
        self.charttype='polar'
        self.name = name
        self.label = label
        self.type = type
        self.width = 400
        self.height = 300
        (self.min_y,self.max_y,self.scaling_y)=ExtendRange5(0,max([max(d) for d in data]))
        self.data = data
        self.gridsize = '%.2f %s' % (self.scaling_y,unit_y)
    def ToHtml(self,chartid):
        datas = '],['.join(map(lambda dataset: ','.join(map(str,dataset)),self.data))
        return '{"type":"polar","name":"%s","label":"%s","data":[[%s]],"range":{"min":%s,"max":%s,"scale":%s}}' % (self.name,self.label,datas,self.min_y,self.max_y,self.scaling_y)


class MyXYChart(MyChart):
    "Build and keep a xy line chart"
    # marginsize: position of the graph from the left of picture
    # height: heigth of the picture
    # width: width of the picture
    # name: name of the chart in page
    # imagefileurl: url of image
    # label: title of the chart
    # pt2px: for each point of chart, return the corresponding pixel X
    # WARNING: Limit is around 970 points
    def __init__(self,data,imagefileurl,name,label,title,nbpts=None,ptindexlist=None,timerange=False,timestart=None,type='ggl',labelx='',labely=None,unitx='',unity=''):
        Log('MyXYChart: begin %s' % label)
        self.charttype='line'
        self.imagefileurl = imagefileurl
        self.name = name
        self.label = label
        self.title = title
        self.type = type
        # Simple chart or XY chart ?
        if len(data)==2 and len(data[0])>1:
            datax = data[0]
            datay = data[1]
        else:
            #print('DEBUG: simple chart')
            datay = data
        # Compute min and max Y values
        (min_y,max_y,scaling_y) = ExtendRange(min(datay),max(datay))
        if max_y-min_y==0:
            max_y = min_y + 1.0
            scaling_y = 0.2

        self.marginsize = 0
        self.pt2px = None
        self.data = list(data)
        self.timerange = timerange
        self.labelx = labelx
        self.unitx = unitx
        self.unity = unity
        if labely==None:
            self.labely = label
        else:
            self.labely = labely
        if timerange:
            self.data[0] = map(lambda secf: 1000*time.mktime((timestart + datetime.timedelta(seconds=int(secf))).timetuple()),data[0])
            #self.data[0] = map(int,data[0])
    def ToHtml(self,chartid):
        if self.timerange:
            datas = ','.join(['[%d,%s]'%(self.data[0][i],self.data[1][i]) for i in range(0,len(self.data[0]))])
        else:
            datas = ','.join(['[%s,%s]'%(self.data[0][i],self.data[1][i]) for i in range(0,len(self.data[0]))])            
        return '{"type":"line","timerange":%(timerange)d,"name":"%(chartname)s","label":"%(label)s","labelx":"%(labelx)s","labely":"%(labely)s","data":[%(data)s]}' % {'data':datas,'chartname': self.name,'label':self.label,'labelx':self.labelx,'labely':self.labely,'timerange':self.timerange}

class ChartString:
    def __init__(self,s):
        self.s = s
    def ToHtml(self,chartid):
        return self.s

class ChartStringWithTitle:
    def __init__(self,s,name,title,type='ggl'):
        self.charttype='title+string'
        self.s = s
        self.name = name
        self.title = title
        self.type = type
    def ToHtml(self,chartid):
        return '{"type":"title+string","title":"%s","name":"%s","contents":[%s]}' % (self.title,self.name,self.s)

def FormatSeconds(secs):
    if secs==0:
        return '0 seconds'
    out=['','','']
    if secs>59:
        minutes = secs / 60
        if minutes>59:
            hours = minutes / 60
            minutes = minutes % 60
            if hours>0:
                out[0] = '%d h' %hours
        if minutes>0:
            out[1] = '%d min' %minutes
        secs = secs % 60
    if secs>0:
        out[2] = '%d seconds'%secs
    return ' '.join(out)

def MaxSpeedToJson(type,i,iunit,mxspds):
    return '{"type":"%s","interval_value":%d,"interval_unit":"%s","maxspds":[%s]}'%(type,i,iunit,','.join(map(lambda mxspd:mxspd.tojson(),mxspds)))

def BuildMaxSpeeds(figures):
    out = []
    if not figures.options['flat']:
        (mxspdsdst,mxspdtime,mxspdsdst_vert,mxspdtime_vert) = figures.computeMaxSpeeds()
    else:
        (mxspdsdst,mxspdtime) = figures.computeMaxSpeeds()
    
    out.extend([MaxSpeedToJson('dist',i,'m',mxspdsdst[i]) for i in sorted(mxspdsdst.keys())])
    out.extend([MaxSpeedToJson('time',i,'s',mxspdtime[i]) for i in sorted(mxspdtime.keys())])
    if not figures.options['flat']:
        out.extend([MaxSpeedToJson('dist_vert',i,'m',mxspdsdst_vert[i]) for i in sorted(mxspdsdst_vert.keys())])
        out.extend([MaxSpeedToJson('dist_time',i,'s',mxspdtime_vert[i]) for i in sorted(mxspdtime_vert.keys())])

    return ','.join(out)

def BuildRuns(figures,threshold=3.0):
    return ','.join(map(lambda m:m.tojson(), figures.computeRuns(threshold)))


def TimeDeltaFormat(t):
    duration_min = (t.seconds/60)%60
    duration_hours = t.seconds/3600
    duration_sec = t.seconds%60
    out=[]
    if t.days>0:
        return '%d d %d:%.2d:%.2d'%(t.days,duration_hours,duration_min,duration_sec)
    if duration_hours>0:
        return '%d:%.2d:%.2d'%(duration_hours,duration_min,duration_sec)
    if duration_min>0:
        return '%d:%.2d'%(duration_min,duration_sec)
    else:
        return '%d seconds'%(duration_sec)

def BuildFigures(figures,type='ggl'):
    if figures.options['spdunit']=='knots':
        length = '%.3f nautical miles' % (MetersToNauticalMiles(figures.lengthdist))
    else:
        if figures.lengthdist>10000:
            length = '%.3f km' % (figures.lengthdist/1000.0)
        else:
            length = '%d m' % int(round(figures.lengthdist))
    out = []
    if len(figures.top10_speeds)>0:
        out.append('"top10spd": [%s]'%','.join(map(lambda (i,pt): '{"ptidx":%d,"when":"%s","spd":"%.2f %s"}'%(i, pt.datetime.strftime('%H:%M:%S'), pt.spd_converted[figures.options['spdunit']], figures.options['spdunit']), figures.top10_speeds)))
    if figures.mean_speed>=0.0:
        out.append('"meanspeed": "%.2f %s"' % (figures.mean_speed, figures.options['spdunit']))
    if figures.mean_speed_when_in_motion>=0.0:
        out.append('"mean_speed_when_in_motion": "%.2f %s"' % (figures.mean_speed_when_in_motion, figures.options['spdunit']))
    out.append('"length": "%s"'%length)
    if not figures.options['flat']:
        out.append('"minele": "%d m"'%int(round(figures.min_ele)))
        out.append('"maxele": "%d m"'%int(round(figures.max_ele)))
        out.append('"up": "%d m"'%int(round(figures.up)))
        out.append('"down": "%d m"'%int(round(figures.down)))
    if hasattr(figures,'duration'):
        out.append('"duration": "%s"'%(TimeDeltaFormat(figures.duration)))
    return '{%s}'%','.join(out)

if __name__=='__main__':
    a=datetime.datetime(2014, 8, 27, 15, 32, 8, 903000)
    b=datetime.datetime(2014, 8, 27, 17, 38, 21, 401000)
    print TimeDeltaFormat(b-a)
