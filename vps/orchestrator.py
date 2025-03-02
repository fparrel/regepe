
# For argv
import sys

# For compression
import gzip

# Misc conversions
from conversions import MetersPerSecToMetersPerHour

# Misc math and util functions
from mathutil import Mean,Filter

from gpxparser import ParseGpxFile
from kmlparser import ParseKmlFile
from nmeaparser import ParseNmeaFile
from rgpparser import ParseRegepeFile
from jsonparser import ParseJsonFile
from garminparser import ParseJsonGarminFile,ParseJsonGarmingFileCourse
from movescountparser import ParseJsonMoveCountFile
from stravaparser import UrlOpenStrava,ParseJsonStravaFile
from sportstrackliveparser import ParseSportsTrackLiveFile
from sbpparser import ParseSbpFile
from fitparser import ParseFitFile
from igcparser import ParseIgcFile
from model import Track
from pagebuilder import BuildPage,MyPolar,MyXYChart,ChartString,ChartStringWithTitle,BuildMaxSpeeds,BuildRuns
from progress import SetProgress
from db import DbSetPassword,DbPut
from unzip import unzipOne
from log import Log,Warn

import uuid
import datetime

import os
import StringIO

# For local time computing
from tz import GetTimeZone
from datetime import timedelta

from urllib2 import urlopen
from urlparse import urlparse,parse_qsl

from figures import Figures

import traceback

from flask_babel import gettext


def ProcessTrkSegWithProgress(track,mapid,submitid,light,options):
    if not light:
        SetProgress(submitid,gettext('Remove staying points'))
    nbptsbefore = len(track)
    if not light:
        pauses = track.RemoveStayingPoints4(3.0,30,0.2)
        #Log('pauses=%s\n'%',\n'.join(map(lambda ptpair: '%s->%s'%(ptpair[0].datetime,ptpair[1].datetime),pauses)))
        Log('RemoveStayingPoints4 %d points -> %d points' % (nbptsbefore,len(track)),submitid)
        SetProgress(submitid,'%d points -> %d points' % (nbptsbefore,len(track)))
    if not options['flat'] and options['usedem'] and not light:
        SetProgress(submitid,gettext('Getting elevations from DEM'))
        track.GetEleFromDEM()
    #print('DEBUG: %d points -> %d points' % (nbptsbefore,len(track)))
    #for pt in track.ptlist:
    #    print('DEBUG:ProcessTrkSegWithProgress: la=%s lg=%s e=%s s=%s c=%s t=%s' % (pt.lat,pt.lon,pt.ele,pt.spd,pt.course,pt.datetime))
    if not light:
        SetProgress(submitid,gettext('Computing figures'))
    figures = Figures(track,options)
    charts = []
    if type=='dyg':
        charts.append(ChartString('<script type="text/javascript">var dygraphs=[];</script>'))
    if len(track)>400 and type=='ggl':
        Log("ProcessTrkSegWithProgress: CompressCopyPriority",submitid)
        trksegcompressed = track.CompressCopyPriority(400)
    else:
        trksegcompressed = track
    if not track.nospeeds:
        if not light:
            SetProgress(submitid,gettext('Building speed chart'))
        try:
            Log('ProcessTrkSegWithProgress: spd chart',submitid)
            data = (trksegcompressed.ComputeTimes(),trksegcompressed.GetSpeeds(options['spdunit']))
            dummy=gettext('Speed') # For allowing translation in jinja2 template
            charts.append(MyXYChart(data,'','spdtimechart','Speed (%s)'%(options['spdunit']),'Speed',len(track),trksegcompressed.ptindexlist,True,track.ptlist[0].datetime,type=type,labely='Spd',unity=options['spdunit']))
        except Exception, e:
            Warn('Cannot make speed against time chart %s %s\n'%(e,traceback.format_exc()))
        # Speed against distance
        #charts.append(MyXYChart((trksegcompressed.ComputeDistances(),trksegcompressed.GetSpeeds(options['spdunit'])),'','spddistchart','Speed in '+options['spdunit']+' against distance in m',len(track),trksegcompressed.ptindexlist))
    if not options['flat']:
        if not light:
            SetProgress(submitid,gettext('Building vert charts'))
        try:
            # Elevation
            #dists = trksegcompressed.ComputeDistances()
            #eles = trksegcompressed.GetElevations()
            #chart = MyXYChart([dists,eles],'','eledistchart','Elevation in m against distance in m',len(track),trksegcompressed.ptindexlist)
            #charts.append(chart)
            Log("ProcessTrkSegWithProgress: vert charts",submitid)
            dummy=gettext('Profile') # For allowing translation in jinja2 template
            charts.append(MyXYChart([trksegcompressed.ComputeDistances(),trksegcompressed.GetElevations()],'','eledistchart','Profile (m)','Profile',len(track),trksegcompressed.ptindexlist,type=type,labelx='Dst',labely='Ele',unitx='m',unity='m'))
            if not track.nospeeds:
                # Vert speed
                #charts.append(MyXYChart([trksegcompressed.ComputeDistances(),map(MetersPerSecToMetersPerHour,trksegcompressed.ComputeMeanVertSpeeds(10.0))],'','vertspdchart','Vertical Speed in m/h against distance in m',len(track),trksegcompressed.ptindexlist))
                # Vert speed against time
                dummy=gettext('Vertical Speed') # For allowing translation in jinja2 template
                charts.append(MyXYChart((trksegcompressed.ComputeTimes(),map(MetersPerSecToMetersPerHour,Filter(trksegcompressed.ComputeInstantVertSpeeds(),Mean,10))),'','vspdtimechart','Vertical Speed (m/h)','Vertical Speed',len(track),trksegcompressed.ptindexlist,True,track.ptlist[0].datetime,type=type,labely='Spd',unity='m/h'))
            # Slope
            #Log("Before slope chart %s\n"%submitid)
            #charts.append(MyXYChart([trksegcompressed.ComputeDistances(),map(lambda x:ApplyThreshold(float(x*100),50.0),trksegcompressed.ComputeMeanSlope(10.0,trksegcompressed.ComputeLengthFromDist()*0.001))],'','slopechart','Slope in percent against distance in m',len(track),trksegcompressed.ptindexlist))
            if not track.nospeeds:
                # Power
                dummy=gettext('Power') # For allowing translation in jinja2 template
                charts.append(MyXYChart([trksegcompressed.ComputeDistances(),trksegcompressed.ComputeBikePower2(10.0,trksegcompressed.ComputeLengthFromDist()*0.001)],'','bikepowerchart','Bike Power (W)','Power',len(track),trksegcompressed.ptindexlist,type=type,labelx='Dst',labely='Pw',unitx='m',unity='W'))
        except Exception, e:
            Warn('Cannot make vert charts %s\n'%e)
            if not light:
                SetProgress(submitid,gettext('Warning: asking for vertical anlysis on flat track'))
    # Add a dummy chart for allowing selection in case there is no chart
    if options['flat'] and track.nospeeds:
        if options['wind']:
            dummy=gettext('Course') # For allowing translation in jinja2 template
            charts.append(MyXYChart([trksegcompressed.ComputeDistances(),map(lambda pt:pt.course,trksegcompressed.ptlist)],'','coursechart','Course (&deg;)','Course',len(track),trksegcompressed.ptindexlist,type=type))
    if options['wind']:
        Log("ProcessTrkSegWithProgress: polar charts",submitid)
        if not light:
            SetProgress(submitid,gettext('Building polar'))
        if track.nospeeds:
            (angles,distances) = track.ComputePolarDist(360)
            charts.append(MyPolar((distances,),'','polarchart','Distance (m) / Absolute course (&deg;)','m',type=type))
        else:
            try:
                (angles,meanspds,maxspds) = track.ComputePolar(360,1.0,options['spdunit'],1)
                charts.append(MyPolar((maxspds,meanspds),'','polarchart','Mean and Max speed (%s) / Absolute course (&deg;)'%(options['spdunit']),options['spdunit'],type=type))
            except Exception, e:
                Warn('Cannot build polar: %s\n'%e)
    if not light:
        SetProgress(submitid,gettext('Building map'))
    Log("ProcessTrkSegWithProgress: BuildPage",submitid)

    if not track.nospeeds and options['maxspd']:
        Log("ProcessTrkSegWithProgress: BuildMaxSpeeds",submitid)
        try:
            dummy=gettext('Max speed analysis') # For allowing translation in jinja2 template
            charts.append(ChartStringWithTitle(BuildMaxSpeeds(figures),'maxspd','Max speed analysis',type=type))
        except Exception, e:
            Warn('Cannot BuildMaxSpeeds: %s\n'%e)

    if not track.nospeeds:
        runs_threshold = 3.0
        if 'slowruns' in options and options['slowruns']:
            runs_threshold = 1.0
        Log("ProcessTrkSegWithProgress: BuildRuns",submitid)
        try:
            dummy=gettext('Runs analysis') # For allowing translation in jinja2 template
            charts.append(ChartStringWithTitle(BuildRuns(figures,runs_threshold),'runs','Runs analysis',type=type))
        except Exception, e:
            Warn('Cannot BuildRuns: %s\n'%e)

    if track.hasHeartRate():
        try:
            dummy=gettext('Heart Rate') # For allowing translation in jinja2 template
            charts.append(MyXYChart((trksegcompressed.ComputeTimes(),trksegcompressed.getHeartRate()),'','hrtimechart','Heart Rate (bps)','Heart Rate',len(track),trksegcompressed.ptindexlist,True,track.ptlist[0].datetime,type=type,labely='Hr',unity='bps'))
        except Exception, e:
            Warn('Cannot Build heart rate %s\n'%e)

    Log("ProcessTrkSegWithProgress: BuildPage",submitid)
    out = BuildPage(track,charts,figures,options['spdunit'],mapid,options)

    #f = open(fname_out,'w')
    #f.write(out)
    Log("ProcessTrkSegWithProgress: compress and write",submitid)
    try:
        f = gzip.open('data/mapdata/%s.json.gz'%mapid,'wb')
    except:
        import os
        os.mkdir('data/mapdata')
        f = gzip.open('data/mapdata/%s.json.gz'%mapid,'wb')
    f.write(out)
    f.close()

GPX = 1
KML = 2
NMEA = 3
KMZ = 4
RGP = 5
JSON = 6
JSON_GARMIN = 7
JSON_GARMIN_COURSE = 13
JSON_MOVESCOUNT = 8
SBP = 9
JSON_STRAVA = 10
FIT = 11
XML_SPORTSTRACKLIVE = 12
IGC = 13
UNKNOWN = 0
EMPTY = -1


def GetFileType(inputfile):
    # Warning: you must do seek(0,0) if you want to parse the file
    fithdr = inputfile.read(14)
    if len(fithdr)>12 and fithdr[8:12]=='.FIT':
        return FIT
    else:
        inputfile.seek(0,0)
    for i in range(0,10):
        line = inputfile.readline()
        if not line:
            if i==0:
                return EMPTY
            else:
                break
        #print 'GetFileType line: "%s"'%line[3:5]
        if line.find('<kml')!=-1:
            return KML
        if line.find('<gpx')!=-1:
            return GPX
        if line[:3]=='$GP':
            return NMEA
        if line[:2]=='PK':
            return KMZ
        if line[:3]=='RGP':
            return RGP
        if line[:2]=='{"' or line[3:5]=='[{':
            return JSON
        if len(line)>6 and line[6]=='\xFD':
            return SBP
    return UNKNOWN

def BuildMap(inputfile_single_or_list,mapid,trk_id,trk_seg_id,submitid,desc,user,options):
    if hasattr(inputfile_single_or_list,'__len__'):
        inputfile_list = inputfile_single_or_list
    else:
        inputfile_list = [inputfile_single_or_list]
    ptlist_all = []
    #print inputfile_list
    for inputfile in inputfile_list:
        if isinstance(inputfile,basestring):
            #http://www.kitetracker.com/gps/tracking?r=ksf15_17
            #http://www.kitetracker.com/data/loadtrack?riderId=ksf15&sessionId=17
            #http://connect.garmin.com/modern/activity/601780115
            #http://www.movescount.com/fr/moves/move41779004
            #https://www.strava.com/activities/505558211i
            #http://www.victorb.fr/visugps/visugps.html?track=http://www.logfly.org/Visu/20171113001853698.igc
            if inputfile.startswith('http://www.kitetracker.com/gps/tracking?r=') or inputfile.startswith('https://www.kitetracker.com/gps/tracking?r='):
                qry = dict(parse_qsl(urlparse(inputfile).query))
                (riderid,sessionid) = qry['r'].split('_')
                inputfile = 'http://www.kitetracker.com/data/loadtrack?riderId=%s&sessionId=%s'%(riderid,sessionid)
                inputfile = urlopen(inputfile)
                filetype = JSON
            elif inputfile.startswith('http://connect.garmin.com/modern/activity/') or inputfile.startswith('https://connect.garmin.com/modern/activity/'):
                if inputfile.strip().endswith('/'):
                    sessionid = inputfile[inputfile.rfind('/',0,-1)+1:-1]
                else:
                    sessionid = inputfile[inputfile.rfind('/')+1:]
                inputfile = urlopen('http://connect.garmin.com/proxy/activity-service-1.2/json/activityDetails/%s'%sessionid)
                filetype = JSON_GARMIN
            elif inputfile.startswith('https://connect.garmin.com/modern/course/'):
                if inputfile.strip().endswith('/'):
                    sessionid = inputfile[inputfile.rfind('/',0,-1)+1:-1]
                else:
                    sessionid = inputfile[inputfile.rfind('/')+1:]
                inputfile = urlopen('https://connect.garmin.com/modern/proxy/course-service/course/%s'%sessionid)
                filetype = JSON_GARMIN_COURSE
            elif inputfile.startswith('http://www.movescount.com/fr/moves/') or inputfile.startswith('http://www.movescount.com/fr/moves/') or inputfile.startswith('http://www.movescount.com/moves/'):
                if inputfile.strip().endswith('/'):
                    moveid = inputfile[inputfile.rfind('/',0,-1)+1:-1]
                else:
                    moveid = inputfile[inputfile.rfind('/')+1:]
                if not moveid.startswith('move'):
                    raise Exception(gettext('URL must follow pattern: "http[s]://www.movescount.com/[fr/]moves/move[XXXXX]"'))
                moveid = moveid[4:]
                inputfile = urlopen('http://www.movescount.com/Move/Track2/%s'%moveid)
                filetype = JSON_MOVESCOUNT
            elif inputfile.startswith('https://www.strava.com/activities/') or inputfile.startswith('http://www.strava.com/activities/'):
                if inputfile.strip().endswith('/'):
                    activityid = inputfile[inputfile.rfind('/',0,-1)+1:-1]
                else:
                    activityid = inputfile[inputfile.rfind('/')+1:]
                inputfile = urlopen('https://www.strava.com/stream/%s?streams[]=latlng&streams[]=distance&streams[]=altitude&streams[]=time'%activityid)
                stravahtmlfile = UrlOpenStrava(activityid)
                filetype = JSON_STRAVA
            elif inputfile.startswith('https://www.sportstracklive.com/track/map#') or inputfile.startswith('http://www.sportstracklive.com/track/map#'):
                foundfull = inputfile.rfind('/full')
                foundid = inputfile.rfind('/',0,foundfull)
                id = inputfile[foundid+1:foundfull]
                filetype = XML_SPORTSTRACKLIVE
                inputfile = urlopen('http://www.sportstracklive.com/live/xml/mapdata?g=_FIAE`FN??&z=10&what=t&op=track&id=%s'%id)
            elif inputfile.startswith('http://www.victorb.fr/visugps/visugps.html?track=') or inputfile.startswith('https://www.victorb.fr/visugps/visugps.html?track='):
                trackurl=inputfile[inputfile.find('track=')+len('track='):]
                url = 'http://www.victorb.fr/visugps/php/vg_proxy.php?track=%s'%trackurl
                print 'url=',url
                inputfile = urlopen(url)
                filetype = IGC
            else:
                raise Exception(gettext('URL must start with "http[s]://www.kitetracker.com/gps/tracking?r=", "http[s]://connect.garmin.com/modern/activity/", "http[s]://www.movescount.com/[fr/]moves/" or "http[s]://www.strava.com/activities/" or "http[s]://www.sportstracklive.com/track/map#" or "http[s]://www.victorb.fr/visugps/visugps.html?track="'))
        else:
            filetype = GetFileType(inputfile)
        Log('type is %s'%filetype)
        if (filetype==GPX):
            inputfile.seek(0,0)
            ptlist = ParseGpxFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==KML):
            inputfile.seek(0,0)
            ptlist = ParseKmlFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==NMEA):
            inputfile.seek(0,0)
            ptlist = ParseNmeaFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==KMZ):
            inputfile.seek(0,0)
            fname = 'tmp/%s.kmz'%str(uuid.uuid4())
            f = open(fname,'wb')
            kmzcontents = inputfile.read()
            f.write(kmzcontents)
            f.close()
            contents = unzipOne(fname)
            os.remove(fname)
            ptlist = ParseKmlFile(StringIO.StringIO(contents),trk_id,trk_seg_id)
        elif (filetype==RGP):
            # do not seek 0 for rgp
            ptlist = ParseRegepeFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==JSON):
            # do not seek 0 for url/json
            #inputfile.seek(0,0)
            ptlist = ParseJsonFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==JSON_GARMIN):
            # do not seek 0 for url/json
            #inputfile.seek(0,0)
            ptlist = ParseJsonGarminFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==JSON_GARMIN_COURSE):
            ptlist = ParseJsonGarmingFileCourse(inputfile,trk_id,trk_seg_id)
        elif (filetype==JSON_MOVESCOUNT):
            # do not seek 0 for url/json
            #inputfile.seek(0,0)
            ptlist = ParseJsonMoveCountFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==JSON_STRAVA):
            # do not seek 0 for url/json
            #inputfile.seek(0,0)
            ptlist = ParseJsonStravaFile(inputfile,stravahtmlfile,trk_id,trk_seg_id)
        elif (filetype==XML_SPORTSTRACKLIVE):
            # do not seek 0 for url/json
            #inputfile.seek(0,0)
            ptlist = ParseSportsTrackLiveFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==SBP):
            inputfile.seek(0,0)
            ptlist = ParseSbpFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==FIT):
            inputfile.seek(0,0)
            ptlist = ParseFitFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==IGC):
            # do not seek 0 for url
            ptlist = ParseIgcFile(inputfile,trk_id,trk_seg_id)
        elif (filetype==EMPTY):
            # ignore empty files
            continue
        else:
            raise Exception(gettext('Unknown file type'))
        ptlist_all.extend(ptlist)
    # count number of points without datetime
    nb_pt_wo_datetime = 0
    for pt in ptlist_all:
        if pt.datetime==None:
            nb_pt_wo_datetime += 1

    # if less than 10% of all points don't have datetime, remove them
    if nb_pt_wo_datetime<len(ptlist_all)*0.1:
        ptlist_all_new = []
        for pt in ptlist_all:
            if pt.datetime!=None:
                ptlist_all_new.append(pt)
        ptlist_all = ptlist_all_new
        nb_pt_wo_datetime = 0
    # add local time offset for GPX and NMEA (KML contains date offset or contains Z)
    if ((filetype==GPX)or(filetype==NMEA)):
        try:
            tz = GetTimeZone(ptlist[0].lat,ptlist[0].lon)
        except:
            tz=0
        if tz!=0:
            tzdelta = timedelta(hours=tz)
            for pt in ptlist_all:
                if pt.datetime!=None:
                    pt.datetime = pt.datetime + tzdelta
    # sort by datetime if applicable
    if nb_pt_wo_datetime==0:
        ptlist_all.sort(key=lambda pt:pt.datetime)

    # build track and map
    track = Track(ptlist_all)

    return BuildMapFromTrack(track,mapid,submitid,desc,user,options)

def BuildMapFromTrack(track,mapid,submitid,desc,user,options):
    #ProcessTrkSegWithProgress(track,mapid,submitid)
    SetProgress(submitid,gettext('Generating uuid'))
    pwd = str(uuid.uuid4())
    SetProgress(submitid,gettext('Writing to DB'))
    DbSetPassword(mapid,pwd)
    DbPut(mapid,pwd,'trackdesc',desc)
    DbPut(mapid,pwd,'trackuser',user)
    DbPut(mapid,pwd,'startpoint','%.4f,%.4f' % (track.ptlist[0].lat,track.ptlist[0].lon))
    if track.ptlist[0].datetime!=None:
        startdate = track.ptlist[0].datetime
    else:
        startdate = datetime.datetime.now()
    DbPut(mapid,pwd,'date',startdate.strftime('%Y-%m-%d'))
    ProcessTrkSegWithProgress(track,mapid,submitid,True,options)
    SetProgress(submitid,'Done')
    return pwd

## PROGRAM ENTRY POINT

def main():
    BuildMap(open('../../work/caramagne.gpx','r'),'caramagne',0,0,'caramagne','desc','user',options_default)

if __name__ == '__main__':
   main()

