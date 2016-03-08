
# For chart building
from pygooglechart import Chart,SimpleLineChart,Axis,XYLineChart,RadarChart

from miscranges import MyRange,ExtendRange,ExtendRange5
from model import Bounds,Track,Point
from options import options
from conversions import SecondToTimeString,MetersToNauticalMiles,MetersPerSecToSpdunit
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
            return '\tnew Point(%f,%f,"%s",%d,%s,%d,%d,%d)' % (pt.lat,pt.lon,pt.GetDateTimeString(),pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course,pt.hr)
        else:
            return '\tnew Point(%f,%f,"%s",%d,%s,%d,%d)'      % (pt.lat,pt.lon,pt.GetDateTimeString(),pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course)
    else:
        if hasattr(pt,'hr'):
            return '\tnew Point(%f,%f,"%s",%d,%s,%d,%d,%d)' % (pt.lat,pt.lon,pt.GetTimeString(),      pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course,pt.hr)
        else:
            return '\tnew Point(%f,%f,"%s",%d,%s,%d,%d)'      % (pt.lat,pt.lon,pt.GetTimeString(),      pt.ele,spd2str(pt.GetSpeed(spdunit)),pt.course/angle_factor,pt.course)

def BuildTrackPointsString(track,angle_factor,spdunit):
    wdate = track.IsOnSeveralDays()
    return ',\n'.join(map(lambda pt:PtToString(pt,angle_factor,spdunit,wdate),track.ptlist))

def ChartToJsonShort(chart):
    if (chart.charttype in ('title+string','polar')):
        return chart.ToHtml(-1)
    else:
        return '{"type":"%s","title":"%s","name":"%s"}'%(chart.charttype,chart.title,chart.name)

#Used to build a html page from a track segment, its parent gpx, the charts and the figures"
def BuildPage(track,charts,figures,spdunit,mapid='0000',type='ggl'):
    #f = open('PageBuilderTemplate%s.html' % options['map_type'])
    #template = f.read()
    #f.close()
    template = """     $map_type = '%(maptype)s';
$figures = <<<EOD
%(figures)s
EOD;
$charts = <<<EOD
%(charts)s
EOD;
$map_data = <<<EOD
nbpts = %(nbpts)d;
spdunit = '%(spdunit)s';
flat = %(flat)d;
wind = %(wind)d;
maxspd = %(maxspd)d;
mapid = '%(mapid)s';
centerlat=%(centerlat)f;
centerlon=%(centerlon)f;
minlat=%(minlat)f;
minlon=%(minlon)f;
maxlat=%(maxlat)f;
maxlon=%(maxlon)f;

track_points = [
%(trackpoints)s
];

chart = [
%(chartsnameandmarginsize)s
];
EOD;
   """
    xycharts = filter(lambda chart: isinstance(chart,MyXYChart), charts)
    if type=='ggl':
        charts_out = '\n'.join([chartobj.ToHtml(chartid) for (chartid,chartobj) in enumerate(charts)])
        chartsnameandmarginsize = ',\n'.join(['\tnew Chart("%(name)s",%(marginsize)d,%(pt2px)s)' % \
                                              {'name': chart.name, \
                                               'marginsize': chart.marginsize, \
                                               'pt2px': ChartPt2pxToString(chart.pt2px)} for chart in xycharts])
    else:
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


def CompassFromDegrees(deg):
    if deg==0:
        return 'N'
    elif deg==30:
        return 'NNE'
    elif deg==45:
        return 'NE'
    elif deg==60:
        return 'ENE'
    elif deg==90:
        return 'E'
    elif deg==120:
        return 'ESE'
    elif deg==135:
        return 'SE'
    elif deg==150:
        return 'SSE'
    elif deg==180:
        return 'S'
    elif deg==210:
        return 'SSW'
    elif deg==225:
        return 'SW'
    elif deg==240:
        return 'WSW'
    elif deg==270:
        return 'W'
    elif deg==300:
        return 'WNW'
    elif deg==315:
        return 'NW'
    elif deg==330:
        return 'NNW'
    elif deg==360:
        return 'N'
    return ''


class MyChart:
    # imagefileurl
    # name
    # label
    html_template = '<div><h3 onclick="toogleHideShow(\'%(chartname)s\');">%(label)s</h3><div class="chart" id="%(chartname)s"><image src="%(imagesrc)s" style="height: %(imageheight)dpx; width: %(imagewidth)dpx; border: 1px dotted #000;" /></div></div>'
    def __init__(self,imagefileurl,name,label):
        self.imagefileurl = imagefileurl
        self.name = name
        self.label = label
    def ToHtml(self,chartid):
        return html_template % { \
            'imagesrc': self.imagefileurl, \
            'imageheight': self.height, \
            'imagewidth': self.width, \
            'label': self.label, \
            'chartname': self.name}


class MyPolar(MyChart):
    "Build and keep a polar chart"
    html_template = '<div><h3 onclick="toogleHideShow(\'%(chartname)s\');">%(label)s</h3><div class="chart" id="%(chartname)s"><image src="%(imagesrc)s" title="Grid size: %(gridsize)s" style="height: %(imageheight)dpx; width: %(imagewidth)dpx; border: 1px dotted #000;" /></div></div>'
    def __init__(self,data,imagefileurl,name,label,unit_y,type= 'ggl'):
        self.charttype='polar'
        self.name = name
        self.label = label
        self.type = type
        self.width = 400
        self.height = 300
        (self.min_y,self.max_y,self.scaling_y)=ExtendRange5(0,max([max(d) for d in data]))
        chart = RadarChart(self.width,self.height)
        self.data = data
        for d in data:
            chart.add_data(d)
        chart.set_colours(['CC0000','339900']) #,'FFFFFF'
        #chart.set_legend(['max','mean','Grid: %.2f %s' % (scaling_y,unit_y)])
        self.gridsize = '%.2f %s' % (self.scaling_y,unit_y)
        if len(data)==2:
            chart.set_legend(['max','mean'])
        chart.set_axis_labels(Axis.BOTTOM, [SelectValuesModulo(i,30) for i in range(0,359)])
        for y in MyRange(self.scaling_y,self.max_y,self.scaling_y):
            if not self.max_y==0.0:
                chart.add_marker(0,float(y)/self.max_y,'h','AAAAAA',1,-1)
        if len(chart.markers)>5:
            # goole chart doesn't support more than 6 markers
            chart.markers = chart.markers[0:5]
        #if len(chart.markers)<2050:
        #chart.markers.append(('B', 'CC000080', '0', '1.0', '0'))
        chart.markers.append(('B', 'FFEE0080', '1', '1.0', '0'))
        #chart.add_fill_simple('FFDD00')
        #chart.add_horizontal_range('E5ECF9',0,30)
        #index = chart.set_axis_labels(Axis.BOTTOM, range(0,360,30))
        #chart.set_axis_positions(index, range(0,360,30))
        self.imagefileurl = chart.get_url()
    def ToHtml(self,chartid):
        if self.type=='ggl' or self.type=='dyg':
            return MyPolar.html_template % { \
                'imagesrc': self.imagefileurl, \
                'imageheight': self.height, \
                'imagewidth': self.width, \
                'label': self.label, \
                'chartname': self.name, \
                'gridsize': self.gridsize}
        elif self.type=='json':
            datas = '],['.join(map(lambda dataset: ','.join(map(str,dataset)),self.data))
            return '{"type":"polar","name":"%s","label":"%s","data":[[%s]],"range":{"min":%s,"max":%s,"scale":%s}}' % (self.name,self.label,datas,self.min_y,self.max_y,self.scaling_y)
        else:
            raise Exception('Unknown chart type: %s'%self.type)


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
    html_template = '\t<div><h3 onclick="toogleHideShow(\'%(chartname)s\');">%(label)s</h3><div class="chart" id="%(chartname)s">' \
                     '<div id="%(chartname)schartmarkerleft" class="chartmarker">' \
                     '<image src="../images/VertBarLeft.png" style="height: 200px; width: 10px; border: 0px;" oncontextmenu="return false;" ondragstart="return false;" onmousedown="onChartMouseDown(event,this,%(chartid)d);" onmouseup="onChartMouseUp(event,this,%(chartid)d);" />' \
                     '</div>' \
                     '<div id="%(chartname)schartmarkerright" class="chartmarker">' \
                     '<image src="../images/VertBarRight.png" style="height: 200px; width: 10px; border: 0px;" oncontextmenu="return false;" ondragstart="return false;" onmousedown="onChartMouseDown(event,this,%(chartid)d);" onmouseup="onChartMouseUp(event,this,%(chartid)d);" />' \
                     '</div>' \
                     '<div id="%(chartname)smarkercurrentpoint" class="chartmarker">' \
                     '<image src="../images/VertBar.png" style="height: 200px; width: 1px; border: 0px;" oncontextmenu="return false;" ondragstart="return false;" onmousedown="onChartMouseDown(event,this,%(chartid)d);" onmouseup="onChartMouseUp(event,this,%(chartid)d);" />' \
                     '</div>' \
                     '<input id="%(chartname)sinput" type="image" src="%(imagesrc)s" title="Left click and release to select - Right click to change current point" alt="Track data" ' \
                     'style="height: %(imageheight)dpx; width: %(imagewidth)dpx; border: 1px dotted #000;" ' \
                     'onmousedown="onChartMouseDown(event,this,%(chartid)d);" ' \
                     'onmouseup="onChartMouseUp(event,this,%(chartid)d);" ' \
                     'oncontextmenu="return false;" />' \
                     '</div></div>\n'
    def __init__(self,data,imagefileurl,name,label,title,nbpts=None,ptindexlist=None,timerange=False,timestart=None,type='ggl',labelx='',labely=None,unitx='',unity=''):
        Log('MyXYChart: begin %s\n' % label)
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
        
        if type in ('dyg','json'):
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
            return
        
        #print('min_y=%d max_y=%d scaling_y=%d' % (min_y,max_y,scaling_y))
        #max_y = int(ceil(max(datay))) # up rounded max value
        #if min(datay)<0.0:
        #    min_y = int(floor(min(datay)))
        #else:
        #    min_y = 0
        #print('min_y=%d,max_y=%d %f' % (min_y,max_y,max(datay)))
        #self.marginsize = max(len(str(max_y)),len(str(min_y)))*6+6  # Font size of y label is 6 pixels
        #self.marginsize = 30
        self.marginsize = max(max(len(str(max_y)),len(str(min_y)))*7+10,30)  # Font size of y label is 6 pixels
        self.height = 200
        # Build chart
        if len(data)==2 and len(data[0])>1:
            self.width = 800
            (min_x,max_x,scaling_x) = ExtendRange(datax[0],datax[len(datax)-1])
            #print('min_x=%d max_x=%d' % (min_x,max_x))
            min_x = int(floor(datax[0]))
            max_x = int(ceil(datax[len(datax)-1]))
            #print('min_x=%d max_x=%d' % (min_x,max_x))
            chart = XYLineChart(self.width, self.height, x_range=[min_x,max_x], y_range=[min_y,max_y])
            chart.add_data(datax)
            chart.add_data(datay)
            if min_y<0 and max_y>0:
                chart.add_data([0,max_x])
                chart.add_data([0,0])
                chart.set_colours(['339900','FF0000'])
                chart.grid = '%s,%s,%s,%s,%s,%s' % (float(scaling_x*100)/float(max_x-min_x),float(scaling_y*100)/float(max_y-min_y),2,2,float(min_x*100)/float(max_x-min_x),0.0)
            else:
                chart.set_colours(['339900'])
                try:
                    chart.grid = '%s,%s,%s,%s,%s,%s' % (float(scaling_x*100)/float(max_x-min_x),float(scaling_y*100)/float(max_y-min_y),2,2,float(min_x*100)/float(max_x-min_x),float(min_y*100)/float(max_y-min_y))
                except ZeroDivisionError:
                    print 'DEBUG: %s %s %s %s' % (max_x,min_x,max_y,min_y)
            #print('grid=%s' % chart.grid)
            #chart.set_grid ...
            if timerange:
                axis_index = chart.set_axis_labels(Axis.BOTTOM, map(lambda sec: SecondToTimeString(timestart,sec),MyRange(min_x,max_x,scaling_x)))
                chart.set_axis_positions(axis_index, map(lambda x: '%.4f' % (float(x*100)/float(max_x-min_x)),MyRange(min_x,max_x,scaling_x)))  #.4f to no have too long urls
                #for x in MyRange(scaling_x,max_x,scaling_x):
                #    chart.add_marker(0,GetIndexOfClosest(datax,x),'V','AAAAAA',1,-1)
            else:
                axis_index = chart.set_axis_labels(Axis.BOTTOM, MyRange(min_x,max_x,scaling_x))
                chart.set_axis_positions(axis_index, map(lambda x: '%.4f' % (float(x*100)/float(max_x-min_x)),MyRange(min_x,max_x,scaling_x)))  #.4f to no have too long urls
                #for x in MyRange(scaling_x,max_x,scaling_x):
                #    chart.add_marker(0,GetIndexOfClosest(datax,x),'V','AAAAAA',1,-1)
            chart.set_axis_labels(Axis.LEFT, MyRange(min_y,max_y,scaling_y))
            marginright = 30
            graphsize = self.width-self.marginsize-marginright
            #print([GetIndexOfCloserFromOrderedList(i,ptindexlist) for i in range(0,nbpts)])
            if ptindexlist==None:
                #if nbpts==None:
                #    nbpts=len(datax)
                if not(nbpts==len(datax)):
                    raise Exception('nbpts=%s len(datax)=%s'%(nbpts,len(datax)))
                self.pt2px = [int(round(datax[i]*graphsize/(max(datax)-min(datax)))) for i in range(0,nbpts)]
            else:
                dataxrange = max(datax)-min(datax)
                maxj = len(ptindexlist)-1
                self.pt2px = []
                j = 0
                for i in range(0,nbpts):
                    if j<maxj and ptindexlist[j+1]<=i:
                        j += 1
                    self.pt2px.append(int(round(datax[j]*graphsize/dataxrange)))
                #self.pt2px = [int(round(datax[GetIndexOfClosestFromOrderedList(i,ptindexlist)]*graphsize/(max(datax)-min(datax)))) for i in range(0,nbpts)]
            # the following works only if points are equally
            #self.pt2px = [int(round(datax[min(int(round(i*len(datax)/nbpts)),len(datax)-1)]*graphsize/(max(datax)-min(datax)))) for i in range(0,nbpts)]
        else:
            self.pt2px = None
            self.width = len(datay) + self.marginsize
            chart = SimpleLineChart(self.width, self.height, y_range=[min_y,max_y])
            chart.add_data(data)
            chart.set_colours(['0000FF'])
            #print('here %d %d'%(min_y,max_y))
            #sys.exit()
            chart.set_axis_labels(Axis.LEFT, MyRange(min_y,max_y,scaling_y))
            marginright = 0
        chart.markers.append(('B','FFEE0080','0','1.0','0'))
        #chart.add_fill_simple('FFCC00')
        # Set the vertical stripes
        #chart.fill_linear_stripes(Chart.CHART, 0, 'CCCCCC', 0.2, 'FFFFFF', 0.2)
        # Set label
        #chart.set_title(label)
        # Build googlecharts url
        #print '&chma='+str(self.marginsize-2)+','+str(marginright)+',0,0'
        self.imagefileurl = chart.get_url() + '&chma='+str(self.marginsize-2)+','+str(marginright)+',0,0'
        if len(self.imagefileurl)>2069:
            raise ValueError('Too much values (%d) instead of 2069' % (len(self.imagefileurl)))
        Log('MyXYChart: end\n')
        #chart.download(self.imagefileurl)
    def ToHtml(self,chartid):
        if self.type=='ggl':
            return MyXYChart.html_template % {'chartname': self.name, \
                                          'imagesrc': self.imagefileurl, \
                                          'imageheight': self.height, \
                                          'imagewidth': self.width, \
                                          'marginsize': self.marginsize, \
                                          'label': self.label, \
                                          'chartid': chartid}
        elif self.type=='dyg':
            if self.timerange:
                datas = ','.join(['[new Date(%s),%s]'%(self.data[0][i],self.data[1][i]) for i in range(0,len(self.data[0]))])
                vfmtx = ''
            else:
                datas = ','.join(['[%s,%s]'%(self.data[0][i],self.data[1][i]) for i in range(0,len(self.data[0]))])
                vfmtx = 'x:{valueFormatter:function(x){return Math.round(x)+"%s";}},' % self.unitx
            if self.unity in ('m','m/h','W'):
                vfmty = 'y:{valueFormatter:function(x){return Math.round(x)+"%s";}}' % self.unity
            else:
                vfmty = 'y:{valueFormatter:function(x){return x.toFixed(2)+"%s";}}' % self.unity                
            return '<div id="%(chartname)s" class="dygraph-chart"></div>\n<script type="text/javascript">\ndata=[%(data)s];\n%(chartname)s = new Dygraph(document.getElementById("%(chartname)s"),data,{yAxisLabelWidth:64,labelsDivWidth:300,selectionColor:"#FF0000",axes:{%(vfmtx)s %(vfmty)s},ylabel:"%(label)s",labels:["%(labelx)s","%(labely)s"],interactionModel: MyDygraphInteractionModel, hideOverlayOnMouseOut:false, clickCallback: function(e, x, pts) { refreshCurrentPoint(%(chartname)s.getSelection());}});\ndygraphs.push(%(chartname)s);\n</script>\n' % {'data':datas,'chartname': self.name,'label':self.label,'labelx':self.labelx,'labely':self.labely,'vfmtx':vfmtx,'vfmty':vfmty}
        elif self.type=='json':
            if self.timerange:
                datas = ','.join(['[%d,%s]'%(self.data[0][i],self.data[1][i]) for i in range(0,len(self.data[0]))])
            else:
                datas = ','.join(['[%s,%s]'%(self.data[0][i],self.data[1][i]) for i in range(0,len(self.data[0]))])            
            return '{"type":"line","timerange":%(timerange)d,"name":"%(chartname)s","label":"%(label)s","labelx":"%(labelx)s","labely":"%(labely)s","data":[%(data)s]}' % {'data':datas,'chartname': self.name,'label':self.label,'labelx':self.labelx,'labely':self.labely,'timerange':self.timerange}
        else:
            raise Exception('Bad type: %s'%self.type)

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
        if self.type=='json':
            return '{"type":"title+string","title":"%s","name":"%s","contents":[%s]}' % (self.title,self.name,self.s)
        else:
            return ''.join(['<div><h3 onclick="toogleHideShow(\'%(chartname)s\');">%(label)s</h3><div class="chart" id="%(chartname)s">' %{'chartname':self.name,'label':self.title},self.s,'</div></div>'])

def MxSpdFormat(mxspd):
    return "%.2f %s - %.0f m in %s at <a href='javascript:void(0);' onclick='refreshCurrentPoint(%d)'>%s</a>"%(MetersPerSecToSpdunit(mxspd.spd,options['spdunit']),options['spdunit'],mxspd.dst,FormatSeconds(mxspd.time),mxspd.ptid,mxspd.pt.datetime.strftime('%H:%M:%S'))

def MxSpdFormatVert(mxspd):
    return "%d %s - %.0f m in %s at <a href='javascript:void(0);' onclick='refreshCurrentPoint(%d)'>%s</a>"%(MetersPerSecToSpdunit(mxspd.spd,'m/h'),'m/h',mxspd.dst,FormatSeconds(mxspd.time),mxspd.ptid,mxspd.pt.datetime.strftime('%H:%M:%S'))

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
    if not options['flat']:
        (mxspdsdst,mxspdtime,mxspdsdst_vert,mxspdtime_vert) = figures.computeMaxSpeeds()
    else:
        (mxspdsdst,mxspdtime) = figures.computeMaxSpeeds()
    
    out.extend([MaxSpeedToJson('dist',i,'m',mxspdsdst[i]) for i in sorted(mxspdsdst.keys())])
    out.extend([MaxSpeedToJson('time',i,'s',mxspdtime[i]) for i in sorted(mxspdtime.keys())])
    if not options['flat']:
        out.extend([MaxSpeedToJson('dist_vert',i,'m',mxspdsdst_vert[i]) for i in sorted(mxspdsdst_vert.keys())])
        out.extend([MaxSpeedToJson('dist_time',i,'s',mxspdtime_vert[i]) for i in sorted(mxspdtime_vert.keys())])
    
    #for i in sorted(mxspdsdst.keys()):
    #    if i==1852:
    #        out.append('<b>Best %s meters (1 nautical mile)</b>'%i)
    #    else:
    #        out.append('<b>Best %s meters</b>'%i)
    #    out.extend(map(MxSpdFormat,mxspdsdst[i]))
    #for i in sorted(mxspdtime.keys()):
    #    out.append('<b>Best %s seconds</b>'%i)
    #    out.extend(map(MxSpdFormat,mxspdtime[i]))
    #if not options['flat']:
    #    for i in sorted(mxspdsdst_vert.keys()):
    #        out.append('<b>Best vertical speeds on %s meters</b>'%i)
    #        out.extend(map(MxSpdFormatVert,mxspdsdst_vert[i]))
    #    for i in sorted(mxspdtime_vert.keys()):
    #        out.append('<b>Best vertical speed on %s</b>'%FormatSeconds(i))
    #        out.extend(map(MxSpdFormatVert,mxspdtime_vert[i]))
    #return '<br/>'.join(out)
    
    return ','.join(out)

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
    if figures.spdunit=='knots':
        length = '%.3f nautical miles' % (MetersToNauticalMiles(figures.lengthdist))
    else:
        if figures.lengthdist>10000:
            length = '%.3f km' % (figures.lengthdist/1000.0)
        else:
            length = '%d m' % int(round(figures.lengthdist))
    if type in ('ggl','dyg'):
        if len(figures.top10_speeds)>0:
            flatfigures = ['<h3 onclick="toogleHideShow(\'top10speeds\');">Top10 speeds:</h3><div class="box" id="top10speeds"><ul>', \
                            '\n'.join(['<li><a href="javascript:void(0);" onclick="refreshCurrentPoint(%d)">%s</a> - %.2f %s</li>' % (i, pt.datetime.strftime('%H:%M:%S'), pt.spd_converted[figures.spdunit], figures.spdunit) for [i,pt] in figures.top10_speeds]), \
                            '</ul></div>']
        else:
            flatfigures = []
        flatfigures += ['<h3 onclick="toogleHideShow(\'globalfigures\');">Global figures</h3><div class="box" id="globalfigures">']
        if figures.mean_speed>=0.0:
            flatfigures += ['<b>Mean Speed:</b> %.2f %s<br>\n' % (figures.mean_speed, figures.spdunit)]
        if figures.mean_speed_when_in_motion>=0.0:
            flatfigures += ['<b>Mean Speed when in motion:</b> %.2f %s<br>\n' % (figures.mean_speed_when_in_motion, figures.spdunit)]
        flatfigures += ['<b>Length:</b> %s' % length]
        if figures.flat:
            figures = flatfigures + ['</div>']
        else:
            elefigures = ['<b>Min Elevation:</b> %d m<br>\n' % int(round(figures.min_ele)), \
                          '<b>Max Elevation:</b> %d m<br>\n' % int(round(figures.max_ele)), \
                          '<b>D+:</b> %d m<br>\n' % int(round(figures.up)), \
                          '<b>D&minus;:</b> %d m' % int(round(figures.down))]
            figures = flatfigures + ['<br>'] + elefigures + ['</div>']
        return '\n'.join(figures)
    elif type=='json':
        out = []
        if len(figures.top10_speeds)>0:
            out.append('"top10spd": [%s]'%','.join(map(lambda (i,pt): '{"ptidx":%d,"when":"%s","spd":"%.2f %s"}'%(i, pt.datetime.strftime('%H:%M:%S'), pt.spd_converted[figures.spdunit], figures.spdunit), figures.top10_speeds)))
        if figures.mean_speed>=0.0:
            out.append('"meanspeed": "%.2f %s"' % (figures.mean_speed, figures.spdunit))
        if figures.mean_speed_when_in_motion>=0.0:
            out.append('"mean_speed_when_in_motion": "%.2f %s"' % (figures.mean_speed_when_in_motion, figures.spdunit))
        out.append('"length": "%s"'%length)
        if not figures.flat:
            out.append('"minele": "%d m"'%int(round(figures.min_ele)))
            out.append('"maxele": "%d m"'%int(round(figures.max_ele)))
            out.append('"up": "%d m"'%int(round(figures.up)))
            out.append('"down": "%d m"'%int(round(figures.down)))
        if hasattr(figures,'duration'):
            out.append('"duration": "%s"'%(TimeDeltaFormat(figures.duration)))
        return '{%s}'%','.join(out)
    else:
        raise Exception('Unknown type %s'%type)

if __name__=='__main__':
    a=datetime.datetime(2014, 8, 27, 15, 32, 8, 903000)
    b=datetime.datetime(2014, 8, 27, 17, 38, 21, 401000)
    print TimeDeltaFormat(b-a)
