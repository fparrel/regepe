from flask import Flask,render_template,send_file,Response,flash,request,redirect
from werkzeug.utils import secure_filename
import json
import os.path
import os
import gzip
import urllib
from db import DbGetListOfDates,DbGet,DbGetComments,DbGetMulitple,DbGetNearbyPoints,DbPut,DbPutWithoutPassword,DbSearchWord,DbGetMapsOfUser,DbGetAllMaps,DbAddComment,CheckValidMapId,CheckValidFreetext,DbDelMap,DbChkPwd
import anydbm
import traceback
from progress import GetProgress
from users import CheckSession,Login,ActivateUser,SendActivationMail,ReserveUser,GetUserFromUserOrEmail,SendForgotPasswordMail
import sys
from orchestrator import BuildMap,ProcessTrkSegWithProgress,BuildMapFromTrack
from searchparser import SearchQueryParser
from sets import Set
from textutils import remove_accents
from log import Log
from mapparser import ParseMap
from model import Track
from options import options_default
from dem import GetEleFromLatLon
from computeprofile import ComputeProfile
from demize import Demize
from generate_id import uniqid
from config import keysnpwds


# Create flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


## Index page

@app.route('/',defaults={'limit':10})
@app.route('/indexall',defaults={'limit':-1})
def index(limit):
    maplist = DbGetListOfDates()
    cptr = 0
    mapsout = []
    for date in sorted(maplist.iterkeys(),reverse=True):
        maps = maplist[date]
        for mapid in maps:
            (lat,lon) = DbGet(mapid,'startpoint').split(',')
            trackdesc = DbGet(mapid,'trackdesc')
            trackuser = DbGet(mapid,'trackuser')
            desc=trackdesc.decode('utf8')
            mapsout.append({'mapid':mapid,'lat':lat,'lon':lon,'user':trackuser,'desc':desc,'date':date})
            cptr += 1
            if(limit>-1) and (cptr>limit):
                break
        if(limit>-1) and (cptr>limit):
            break
    return render_template('index.html',limit=limit,maps=mapsout,GMapsApiKey=keysnpwds['GMapsApiKey'])


## Thumbnails

if not os.path.isdir('data'):
	os.mkdir('data')
if not os.path.isdir('data/thumbnail_cache'):
	os.mkdir('data/thumbnail_cache')

@app.route('/thumbnail/<mapid>')
def thumbnail(mapid):
    filename='data/thumbnail_cache/%s.png'%mapid
    if os.path.isfile(filename):
        # Return image in cache
        return send_file(filename, mimetype='image/png')
    else:
        # Read map data
        f=gzip.open('data/mapdata/%s.json.gz'%mapid,'rb')
        mapdata=json.load(f)
        f.close()
        # Find most interesting points + sampling
        i=0
        step = round((mapdata['nbpts']-1)/20)
        if step<1:
            step = 1
        pt_selected=[]
        for pt in mapdata['points']:
            if i==0 or pt[0]==mapdata['minlat'] or pt[0]==mapdata['maxlat'] or pt[1]==mapdata['minlon'] or pt[1]==mapdata['maxlon'] or i%step==0:
                pt_selected.append((pt[0],pt[1]))
            i+=1
        pt_selected.append((pt[0],pt[1]))
        # Build gmaps url
        url = 'http://maps.googleapis.com/maps/api/staticmap?size=130x110&maptype=terrain&markers=size:tiny|%s,%s|%s,%s&path=weight:3|%s'%(pt_selected[0][0],pt_selected[0][1],pt_selected[-1][0],pt_selected[-1][1],'|'.join(map(lambda ll:'%s,%s'%ll,pt_selected)))
        # Download png, put it in cache and send it
        f = urllib.urlopen(url)
        fcache = open(filename,'wb')
        contents = f.read()
        fcache.write(contents)
        fcache.close()
        f.close()
        return contents


## Show map

@app.route('/showmap/<mapid>', defaults={'map_type': None})
@app.route('/showmap/<mapid>/<map_type>')
def showmap(mapid,map_type):
    # Read map data
    f=gzip.open('data/mapdata/%s.json.gz'%mapid,'rb')
    mapdata=json.load(f)
    f.close()
    # Read map db
    mapdb = anydbm.open('data/maps/%s.db'%mapid, 'r')
    if map_type==None:
        map_type = mapdata['type']
    # Render
    _mapdb={}
    for key in mapdb:
        _mapdb[key] = mapdb[key].decode('utf-8') # We must convert each utf8 string into unicode for jinja2
    out = render_template('showmap.html',mapid=mapid,type=map_type,mapdb=_mapdb,mapdata=mapdata,GMapsApiKey=keysnpwds['GMapsApiKey'],GeoPortalApiKey=keysnpwds['GeoPortalApiKey'])
    mapdb.close()
    return out

@app.route('/mapdata/<mapid>')
def mapdata(mapid):
    # Read map data
    f=gzip.open('data/mapdata/%s.json.gz'%mapid,'rb')
    mapfromfile=json.load(f)
    f.close()
    return Response(render_template('mapdata.js',mapdata=mapfromfile,chartdata=json.dumps(mapfromfile['chartdata'])), mimetype='text/javascript')

@app.route('/comments/<mapid>')
def comments(mapid):
    comments = DbGetComments(mapid)
    return Response('<?xml version="1.0" encoding="UTF-8"?><result>%s</result>' % ''.join(map(lambda comment: '<comment user="%s" date="%s">%s</comment>' % (comment[1],comment[0],comment[2]),comments)), mimetype='text/xml')

@app.route('/sendcomment/<mapid>/<comment>')
def sendcomment(mapid,comment):
    try:
        user = 'unknown'
        if request.form.has_key('user'):
            user = request.form.getvalue('user')
            if not CheckValidUserName(user):
                raise Exception('Invalid user name')
            sess = request.form.getvalue('sess')
            if CheckSession(user,sess):
                pass
            else:
                raise Exception('Invalid session, please re-login')
        else:
            user = request.remote_addr
        if not CheckValidMapId(mapid):
            raise Exception('Invalid map id')
        if not CheckValidFreetext(comment):
            raise Exception('Invalid map id')
        DbAddComment(mapid,user,comment)
        result = 'OK'
    except Exception, e:
        result = str(e)
    out = '<?xml version="1.0" encoding="UTF-8"?>\n<result>%s</result>'%result
    return Response(out, mimetype='text/xml')

@app.route('/nearmaps/<mapid>')
def nearmaps(mapid):
    lat,lon = map(float,DbGet(mapid,'startpoint').split(','))
    return '{'+','.join(['"%s":%s' % (_mapid,json.dumps(DbGetMulitple(_mapid,('startpoint','trackdesc','trackuser','date')))) for _mapid in filter(lambda mid: mid!=mapid,DbGetNearbyPoints(lat,lon))])+'}'

@app.route('/dbget/<mapid>/<element>')
def dbget(mapid,element):
    try:
        val = DbGet(mapid,element.encode('ascii'))
        message = 'OK'
    except Exception, e:
        message = 'Error: ' + str(e)+'\n'+traceback.format_exc()
        val = 'Error'
    out = '<?xml version="1.0" encoding="UTF-8"?>\n<answer><message>%s</message><pageelementid>%s</pageelementid><value>%s</value></answer>' % (message,element,val)
    return Response(out, mimetype='text/xml')

@app.route('/dbput/<mapid>/<pwd>/<ele>/<val>',defaults={'user':None,'sess':-1})
@app.route('/dbput/<mapid>/<pwd>/<ele>/<val>/<user>/<sess>')
def dbput(mapid,pwd,ele,val,user,sess,defaults={'user': None,'sess': -1}):
    try:
        if user!=None and sess!=-1:
            if CheckSession(user,sess):
                map_user = DbGet(mapid,'trackuser')
                if len(map_user)>0 and map_user==user:
                    DbPutWithoutPassword(mapid,ele,val)
                    message = 'OK'
                else:
                    raise Exception('Map %s does not belong to user %s, but to user %s' % (mapid,user,map_user))
            else:
                raise Exception('Invalid session, please re-login')
        else:
            DbPut(mapid,pwd,ele.encode('ascii'),val.encode('utf8'))
            message = 'OK'
    except Exception, e:
        message = 'Error: ' + str(e)
        val = 'Error'
    out = '<?xml version="1.0" encoding="UTF-8"?>\n<answer><message>%s</message><pageelementid>%s</pageelementid><value>%s</value></answer>' % (message,ele,val)
    return Response(out, mimetype='text/xml')


## Send map

@app.route('/submitform')
def submitform():
    return render_template('submitform.html',GMapsApiKey=keysnpwds['GMapsApiKey'])

@app.route('/upload', methods=['POST'])
def upload():
    # Get submit_id
    submit_id = request.form['submit_id'].encode('ascii')
    if not submit_id.isalnum():
        return 'Bad submitid'
    # Build inputfile array
    inputfile = []
    i=0
    for file in request.files.getlist("file[]"):
        # Save each uploaded file
        if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        Log('Saving file',submit_id)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename('%s_%s.gpx'%(submit_id,i))))
        i+=1
        inputfile.append(file)
    # In case of import from URL
    if request.form.has_key('fromurl') and len(request.form['fromurl'])>0:
        inputfile.append(request.form('fromurl').encode('ascii'))
    if len(inputfile)<1:
        return 'Error while uploading file'
    # Track selection in case file contains several tracks
    if request.form.has_key('trk_select'):
        trk_id = int(request.form['trk_select'])
    else:
        trk_id = 0
    trk_seg_id = 0
    # Get track description
    desc = request.form['desc'].encode('utf8')
    # Check session
    user = request.form['user']
    sys.stderr.write('%s\n'%(request.form))
    if user=='NoUser' or user=='':
        user = 'unknown'
    else:
        sess = request.form['sess']
        if not CheckSession(user,sess):
            user = 'unknown'
    # Parse options (flat,wind,maptype,...)
    options = options_default
    for key in options:
        if request.form.has_key(key):
            if type(options[key])==bool:
                options[key]=request.form[key]=='yes'
            elif type(options[key])==int:
                options[key]=int(request.form[key])
            elif type(options[key])==str:
                options[key]=request.form[key]
            else:
                raise Exception('type %s not handled',type(options[key]))
    Log('start BuildMap',submit_id)
    pwd = BuildMap(inputfile,submit_id,trk_id,trk_seg_id,submit_id,desc,user,options)
    Log('end BuildMap',submit_id)
    return '''<script type="text/javascript">
    var date = new Date();
    date.setTime(date.getTime()+(10*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
    document.cookie = "pwd%(mapid)s=%(pwd)s"+expires+"; path=/";
    location.href=\'/showmap/%(mapid)s\';
    </script>'''% {'mapid':submit_id,'pwd':pwd}

@app.route('/getprogress/<submitid>')
def getprogress(submitid):
    return GetProgress(submitid.encode('ascii')).encode('ascii')


## Search

class MapSeach(SearchQueryParser):
    def GetWord(self, word):
        return Set(DbSearchWord('trackdesc',word))
    def GetWordWildcard(self, word):
        return Set()
    def GetQuotes(self, search_string, tmp_result):
        return Set()

def map_search_result(mapid):
    (lat,lon) = DbGet(mapid,'startpoint').split(',')
    trackdesc = DbGet(mapid,'trackdesc')
    startdate = DbGet(mapid,'date')
    trackuser = DbGet(mapid,'trackuser')
    try:
        desc = trackdesc.encode('ascii', 'xmlcharrefreplace')
    except:
        desc = trackdesc
    return('<map mapid="%s" lat="%s" lon="%s" date="%s" user="%s">%s</map>' % (mapid,lat,lon,startdate,trackuser,desc))

@app.route('/search/<search_req>')
def search(search_req):
    try:
        req = remove_accents(search_req.encode('utf8').lower(),'utf-8')
        mapids = MapSeach().Parse(req)
        out='<result><maps>%s</maps></result>'%''.join(map(map_search_result,mapids))
    except Exception, e:
        out='<error>Error: %s</error>'%e
    return Response(out, mimetype='text/xml')


## Show user

@app.route('/showuser/<user>')
def showuser(user):
    return render_template('showuser.html',user=user)

@app.route('/userinfo/<user>')
def userinfo(user):
    mapids = DbGetMapsOfUser(user.encode('ascii'))
    out = '<maps>%s</maps>'%''.join(map(map_search_result,mapids))
    return Response(out, mimetype='text/xml')


## Browse maps

@app.route('/mapofmaps')
def mapofmaps():
    return render_template('mapofmaps.html',GMapsApiKey=keysnpwds['GMapsApiKey'])

def map_search_result2(lat,lon,mapid):
    trackdesc = DbGet(mapid,'trackdesc')
    startdate = DbGet(mapid,'date')
    trackuser = DbGet(mapid,'trackuser')
    try:
        desc = trackdesc.encode('ascii', 'xmlcharrefreplace')
    except:
        desc = trackdesc
    return('<map mapid="%s" lat="%s" lon="%s" date="%s" user="%s">%s</map>' % (mapid,lat,lon,startdate,trackuser,desc))

def latlonmapids2xml(latlonmapids):
    lat,lon,mapids = latlonmapids
    return '<maps lat="%.4f" lon="%.4f">%s</maps>' % (lat,lon,''.join(map(lambda mapid:map_search_result2(lat,lon,mapid),mapids)))

@app.route('/getmaplist')
def getmaplist():
    latlonmapidss = DbGetAllMaps()
    out = '<results>%s</results>' % ''.join(map(latlonmapids2xml,latlonmapidss))
    return Response(out, mimetype='text/xml')


## Map Tools

def auth(mapid,pwd,user,sess):
    # Check rights
    if user!=None and sess!=None:
        if CheckSession(user,sess):
            map_user = DbGet(mapid,'trackuser')
            if len(map_user)>0 and map_user==user:
                pass
            else:
                raise Exception('Map %s does not belong to user %s, but to user %s' % (mapid,user,map_user))
        else:
            raise Exception('Invalid session, please re-login')
    else:
        if not DbChkPwd(mapid,pwd):
            raise Exception('You do not have the map\'s password in your browser\'s cookies')

@app.route('/delmap/<mapid>/<pwd>',defaults={'user':None,'sess':None})
@app.route('/delmap/<mapid>/<pwd>/<user>/<sess>')
def delmap(mapid,pwd,user,sess):
    try:
        auth(mapid,pwd,user,sess)
        # Delete map
        DbDelMap(mapid)
        mapfile = 'data/mapdata/%s.json.gz' % mapid
        os.remove(mapfile)
        message = 'Map deleted'
    except Exception, e:
        message = str(e)
    return render_template('map_deleted.html',message=message)


def modifymap(mapid,pwd,user,sess,modifyfunction):
    try:
        # Authentificate
        auth(mapid,pwd,user,sess)
        # Parse map
        options, ptlist = ParseMap(mapid)
        # Apply modifications
        ptlist,startpointchanged = modifyfunction(ptlist)
        # Rebuild map
        track = Track(ptlist)
        ProcessTrkSegWithProgress(track,mapid,mapid,True,options)
        # If start point has changed, then update the database
        if startpointchanged:
            DbPutWithoutPassword(mapid,'startpoint','%.4f,%.4f' % (track.ptlist[0].lat,track.ptlist[0].lon))
        # Recompute thumbnail
        previewfile = 'data/thumbnail_cache/%s.png' % mapid
        if os.access(previewfile,os.F_OK):
            os.remove(previewfile)
        message = None
    except Exception, e:
        message = str(e)
    if message==None:
        return redirect('/showmap/%s'%mapid)
    else:
        return render_template('map_action_error.html',message=message,mapid=mapid)

@app.route('/map/crop/<mapid>/<pwd>/<int:pt1>/<int:pt2>',defaults={'user':None,'sess':None})
@app.route('/map/crop/<mapid>/<pwd>/<int:pt1>/<int:pt2>/<user>/<sess>')
def cropmap(mapid,pwd,pt1,pt2,user,sess):
    return modifymap(mapid,pwd,user,sess,lambda ptlist: (ptlist[pt1:pt2],pt1!=0))

@app.route('/map/clear/<mapid>/<pwd>/<int:pt1>/<int:pt2>',defaults={'user':None,'sess':None})
@app.route('/map/clear/<mapid>/<pwd>/<int:pt1>/<int:pt2>/<user>/<sess>')
def clearmap(mapid,pwd,pt1,pt2,user,sess):
    return modifymap(mapid,pwd,user,sess,lambda ptlist: (ptlist[:pt1]+ptlist[pt2:],pt1==0))

def removepoints(ptlist,ptidxtodel):
    l=range(0,len(ptlist))
    for i in ptidxtodel:
        l.remove(i)
    return ([ptlist[i] for i in l],0 in ptidxtodel)

@app.route('/map/clearlist/<mapid>/<pwd>/<ptliststr>',defaults={'user':None,'sess':None})
@app.route('/map/clearlist/<mapid>/<pwd>/<ptliststr>/<user>/<sess>')
def clearmaplist(mapid,pwd,ptliststr,user,sess):
    ptidxtodel = map(int,ptliststr.split(','))
    return modifymap(mapid,pwd,user,sess,lambda ptlist: removepoints(ptlist,ptidxtodel))

@app.route('/map/export/<mapid>')
def exportmap(mapid):
    # TODO: build it from client side
    pass

@app.route('/map/demize/<int:index>/<mapid>/<pwd>',defaults={'user':None,'sess':None})
@app.route('/map/demize/<int:index>/<mapid>/<pwd>/<user>/<sess>')
def demize(index,mapid,pwd,user,sess):
    try:
        # Authentificate
        auth(mapid,pwd,user,sess)
        # Start/continue/finish DEMization. index is current point index, l is total number of points in map
        index,l = Demize(index,mapid)
        # Format answer
        if index==0:
            answer = '<answer><result>Done</result></answer>'
        else:
            percent = index * 100 / l
            answer = '<answer><result>OK</result><nextindex>%s</nextindex><percent>%s</percent></answer>' % (index,percent)
    except Exception, e:
        answer = '<answer><result>%s</result></answer>' % e
    return Response('<?xml version="1.0" encoding="UTF-8"?>\n%s'%answer,mimetype='text/xml')


## User services

def CheckHumain(humaincheck):
    return ((humaincheck.strip().lower()=='earth')or(humaincheck.strip().lower()=='the earth'))

@app.route('/registerform')
def registerform():
    """ Display register form """
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    mail = request.form['mail'].lower()
    user = request.form['user'].lower()
    pwd1 = request.form['pwd1']
    pwd2 = request.form['pwd2']
    humaincheck = request.form['humaincheck']
    if not CheckHumain(humaincheck):
        return render_template('register.html',error_message='Humain check error')
    if pwd1!=pwd2:
        return render_template('register.html',error_message='Password check error')
    activation_id = ReserveUser(user.encode('ascii'),mail.encode('ascii'),pwd1.encode('utf8'))
    SendActivationMail(mail,user,activation_id)
    return render_template('user_registered.html',user=user)

@app.route('/activate/<user>/<activationid>')
def activate(user,activationid):
    """ Activate user given it's activation_id """
    try:
        ActivateUser(user,activationid)
    except Exception, e:
        return render_template('user_activate_error.html',message=str(e))
    return render_template('user_activated.html',user=user)

@app.route('/login/<user>/<pwd>')
def login(user,pwd):
    """ Check login/password return sesssion_id """
    try:
        (user,sessid) = Login(user,pwd)
    except Exception, e:
        return Response('<result><user>NoUser</user><sess>-1</sess><error>%s</error></result>'%e, mimetype='text/xml')
    out = '<result>'
    if user==None:
        user = 'NoUser'
        sess = -1
    out = '<result><user>%s</user><sess>%s</sess></result>' % (user,sessid)
    return Response(out, mimetype='text/xml')

@app.route('/chksess/<user>/<sess>')
def chksess(user,sess):
    """ Check session_id for a given user """
    try:
        ret = CheckSession(user,sess)
    except Exception, e:
        out = '<answer><result>Error: %s</result><user>NoUser</user><sess>-1</sess></answer>' % str(e)
        return Response(out, mimetype='text/xml')
    if ret:
        result = 'OK'
    else:
        result = 'Expired'
    out = '<answer><result>%s</result><user>%s</user><sess>%s</sess></answer>' % (result,user,sess)
    return Response(out, mimetype='text/xml')

@app.route('/resendpwd', methods=['POST'])
def resendpwd():
    user_mail = request.form['user_mail'].encode('ascii').lower()
    humaincheck = request.form['humaincheck']
    if not CheckHumain(humaincheck):
        return render_template('resendpwd_error.html',error_message='Humain check error')
    try:
        user = GetUserFromUserOrEmail(user_mail)
        mail = SendForgotPasswordMail(user)
    except Exception, e:
        return render_template('resendpwd_error.html',error_message=str(e))
    return render_template('resendpwd_ok.html',mail=mail)


def retrievemap(mapid):
    (lat,lon) = DbGet(mapid,'startpoint').split(',')
    desc = DbGet(mapid,'trackdesc').decode('utf8')
    startdate = DbGet(mapid,'date')
    user = DbGet(mapid,'trackuser')
    return {'mapid':mapid,'lat':lat,'lon':lon,'desc':desc,'date':startdate,'user':user}

@app.route('/userhome/<user>')
def userhome(user):
    mapids = DbGetMapsOfUser(user.encode('ascii'))
    return render_template('userhome.html',user=user,maps=map(retrievemap,mapids),GMapsApiKey=keysnpwds['GMapsApiKey'])

@app.route('/mergemaps/<mapidsliststr>/<user>/<sess>')
def mergemaps(mapidsliststr,user,sess):
    if not CheckSession(user,sess):
        message = 'Cannot identify user %s %s'%(user,sess)
    else:
        mapids = mapidsliststr.split(',')
        ptlistmerged = {}
        for mapid in mapids:
            newmapid = uniqid()
            Log("MergeCgi: parse map %s" % mapid,newmapid)

            # Parse map
            options,ptlist = ParseMap(mapid)
            #TODO: merge options

            # set right day if needed
            if ptlist[0].datetime.year<=1980:
                dfromdb = DbGet(mapid,'date')
                if dfromdb:
                    d = datetime.datetime.strptime(dfromdb,'%Y-%m-%d')
                    for pt in ptlist:
                        pt.datetime = pt.datetime.replace(year=d.year,month=d.month,day=d.day)

            # append to dict
            for pt in ptlist:
                ptlistmerged[pt.datetime] = pt

        ptlistmerged = ptlistmerged.values()
        ptlistmerged.sort(key=lambda pt:pt.datetime)

        Log("MergeCgi: rebuild: Track len=%d" % len(ptlistmerged),newmapid)

        # Rebuild map
        track = Track(ptlistmerged)
        pwd = BuildMapFromTrack(track,newmapid,newmapid,'Result of merge',user,options)

        Log("MergeCgi: finished",newmapid)

        # Redirect to map
        return redirect('/showmap/%s'%newmapid)

@app.route('/delmaps/<mapidsliststr>/<user>/<sess>')
def delmaps(mapidsliststr,user,sess):
    if not CheckSession(user,sess):
        message = 'Cannot identify user %s %s'%(user,sess)
    else:
        try:
            mapids = mapidsliststr.split(',')
            message = ''
            for mapid in mapids:
                map_user = DbGet(mapid,'trackuser')
                if len(map_user)>0 and map_user==user:
                    DbDelMap(mapid)
                    os.remove('data/mapdata/%s.json.gz'%mapid)
                    message += 'Map %s deleted. '%mapid
                else:
                    message += 'Map %s do not belong to you'%mapid
                    break
        except Exception, e:
            message += 'Error: %s'%e
    return render_template('map_deleted.html',message=message)


## Prepare

@app.route('/prepare',defaults={'map_type':'GeoPortal','pts':[],'names':[]})
@app.route('/prepare/<map_type>',defaults={'pts':[],'names':[]})
@app.route('/prepare/<map_type>/<pts>',defaults={'names':None})
@app.route('/prepare/<map_type>/<pts>/<names>')
def prepare(map_type,pts,names):
    return render_template('prepare.html',map_type=map_type,GMapsApiKey=keysnpwds['GMapsApiKey'],GeoPortalApiKey=keysnpwds['GeoPortalApiKey'])

@app.route('/ele/<float:lat>/<float:lon>')
def getele(lat,lon):
    return Response('%d'%GetEleFromLatLon(lat,lon), mimetype='text/plain')

def PtStr2FloatArray(ptstr):
    out = ptstr.split(',')
    return (float(out[0]),float(out[1]))

@app.route('/profile/<ptliststr>/<width>/<height>')
def profile(ptliststr,width,height):
    ptlist = map(PtStr2FloatArray,ptliststr.split('~'))
    if(len(ptlist)<2):
        return Response('Error: Cannot compute profile for only one point', mimetype='text/plain')
    nbpts = 400
    return Response('\n'.join(map(str,ComputeProfile(ptlist,nbpts,width,height))), mimetype='text/plain')

@app.route('/prepare/export/<format>/<ptlist>/<names>')
def prepare_export(format,ptlist,names):
    # TODO: build it from client side
    pass

## Program entry point

if __name__ == '__main__':
    # Start web server
    app.run(port=8080,debug=True)
