/* 
********************
* Global variables *
********************

---------
From map:
---------
nbpts
spdunit
flat
wind
mapid
track_points
linecharts

-------------------
Dynamic parameters:
-------------------
center_map
auto_play
snakelength
playingnbpts
winddir
buoy_lat
buoy_lon
winddirorbuoy

selchartid
selfirstptid
sellastptid
last_point_id

-----------
Autoplayer:
-----------
autoplaycptr
auto_play_interval_id

--------
Sliders:
--------
currentpointslider
playingspeedslider
snakelengthslider

----------
Constants:
----------
LEFT_BUTTON
RIGHT_BUTTON
MOUSEWHEEL_EVT

*/

/* Called when a selection has changed on a chart. 
   If -1 is passed as chartid, remove current selection. */
function chartSelChange(chartid) {
	if (chartid != -1) {
		selchartid = chartid;
		refreshSelection(linecharts[chartid].pt1_id,linecharts[chartid].pt2_id);
	}
	else {
		refreshSelection(-1,-1);
        var i;
        for (i=0;i<linecharts.length;i++) {
            moveChartSelection(i,-1,-1);
        }	
    }
}

/* Move the left marker of a selection on all chart. 
   DO NOT refresh map markers and infos */
function moveChartMarkerLeft(pt1_id,chartid) {
    var i;
    for (i=0;i<linecharts.length;i++) {
        moveChartMarkerLeftOne(pt1_id,i);
    }
}

/* Move the left marker of a selection on a chart. 
   DO NOT refresh map markers and infos */
function moveChartMarkerLeftOne(pt1_id,chartid) {
    var sel = plot[chartid].getSelection();
    if(sel!=null) {
        sel.xaxis.from = chartdata[chartid][0].data[pt1_id][0];
        plot[chartid].setSelection(sel);
    }
	linecharts[chartid].pt1_id = pt1_id;
}

/* Move the right marker of a selection on all chart. 
   DO NOT refresh map markers and infos */
function moveChartMarkerRight(pt2_id,chartid) {
    var i;
    for (i=0;i<linecharts.length;i++) {
        moveChartMarkerRightOne(pt2_id,i);
    }
}

/* Move the right marker of a selection on a chart. 
   DO NOT refresh map markers and infos */
function moveChartMarkerRightOne(pt2_id,chartid) {
    var sel = plot[chartid].getSelection();
    if(sel!=null){
        sel.xaxis.to = chartdata[chartid][0].data[pt2_id][0];
        plot[chartid].setSelection(sel);
    }
	linecharts[chartid].pt2_id = pt2_id;
}

/* Move the current point marker on all charts. 
   DO NOT refresh map marker and infos */
function moveChartMarkerCurrentPoint(ptid) {
    var i;
    for(i=0;i<linecharts.length;i++) {
        moveChartMarker(i,ptid);
    }
}

/* Toogle "Center Map" switch */
function toogleCenterMap() {
	if (typeof center_map == "undefined") center_map=1;
	if (center_map) {
		center_map=0;
		document.getElementById('center_map_toogle').innerHTML="No";
	}
	else {
		center_map=1;
		document.getElementById('center_map_toogle').innerHTML="Yes";
	}
}

function setAutoPlayToOff() {
	if (typeof auto_play == "undefined") auto_play=0;
    auto_play=0;
    document.getElementById('toogle_auto_play').innerHTML="Play";
    clearInterval(auto_play_interval_id);
}

/* Auto play callback function: move forward current point (according to speed) and refresh infos and marker */
function autoPlayCallback() {
    var endnotreached = true;
	if (playingnbpts<1) {
		// count before going to next point
		if (typeof autoplaycptr == "undefined") autoplaycptr = 2-playingnbpts;
		autoplaycptr--;
		if (autoplaycptr==0) {
			endnotreached = scrollOffset(1);
			autoplaycptr = 2-playingnbpts;
		}
	}
	else {
		// go by playingnbpts points
		endnotreached = scrollOffset(playingnbpts);
	}
    if (!endnotreached) {
        setAutoPlayToOff();
    }
}

/* Toogle "Auto play" switch */
function toogleAutoPlay() {
	if (typeof auto_play == "undefined") auto_play=0;
	if (auto_play) {
        setAutoPlayToOff();
		/*document.getElementById('toogle_auto_play').innerHTML="Play";
		clearInterval(auto_play_interval_id);*/
	}
	else {
        if (currentpointslider.getValue()==currentpointslider.getMaximum()) {
            currentpointslider.setValue(currentpointslider.getMinimum());
        }
		auto_play=1;
		document.getElementById('toogle_auto_play').innerHTML="Stop";
		auto_play_interval_id = setInterval("autoPlayCallback();",100);
	}
}

/* Change the current point id according to a given offset (scrolle slider that will trigger refresh of infos and marker) */
function scrollOffset(offset) {
    var newvalue = currentpointslider.getValue()+offset;
    if (newvalue>=currentpointslider.getMaximum()) {
        currentpointslider.setValue(currentpointslider.getMaximum());
        return false;
    }
    else if (newvalue<=currentpointslider.getMinimum()) {
        currentpointslider.setValue(currentpointslider.getMinimum());
        return false;
    }
    else {
        currentpointslider.setValue(newvalue);
    }
    return true;
}

/* Sum the lenght on path between two points */
function computeLengtOnPath(pt1_id, pt2_id) {
    var ptid;
    var l = 0.0;
    if (pt2_id<pt1_id) {
        var tmp = pt1_id;
        pt1_id = pt2_id;
        pt2_id = tmp;
    }
    if ((pt1_id<0)||(pt2_id+1>nbpts)) {
        return 0.0;
    }
    for(ptid=pt1_id;ptid<pt2_id;ptid++) {
        l += geodeticDist(track_points[ptid].lat,track_points[ptid].lon,
            track_points[ptid+1].lat,track_points[ptid+1].lon);
    }
    return l;
}

/* Used by updateChartMarkerValue and updateSelChartMarkerValue */
var charmarkervalues = new Array();
var charmarkerdiv = new Array();

/* Update value that is displayed next to single point chart marker */
function updateChartMarkerValue(name,value,title) {
/*    if(typeof charmarkervalues[name]!='undefined') {
        charmarkervalues[name].data = value;
    }
    else {
        var markervaluediv = document.createElement('div');
        markervaluediv.style.marginTop = "-200px";
        markervaluediv.style.marginLeft = "2px";
        markervaluediv.title = title;
        charmarkervalues[name] = document.createTextNode(value);
        markervaluediv.appendChild(charmarkervalues[name]);
        document.getElementById(name+"chartmarkercurrentpoint").appendChild(markervaluediv);
        document.getElementById(name+"chartmarkercurrentpoint").onmousedown = document.getElementById(name+"chartinput").onmousedown; //function(event) { onChartMouseDown(event,this,0); };
        document.getElementById(name+"chartmarkercurrentpoint").onmouseup = document.getElementById(name+"chartinput").onmouseup; //function(event) { onChartMouseUp(event,this,0); };
        document.getElementById(name+"chartmarkercurrentpoint").oncontextmenu = function(event) { return false; };
        
    }*/
}

/* Update value that is displayed above chart selection markers */
function updateSelChartMarkerValue(name,value,title) {
/*    if(typeof charmarkervalues[name+'sel'+0]!='undefined') {
        var i;
        for(i=0;i<value.length;i++) {
            charmarkervalues[name+'sel'+i].data = value[i];
        }
    }
    else {
        
        var markervaluediv = document.createElement('div');
        markervaluediv.style.marginTop = "-215px";
        var i;
        for(i=0;i<value.length;i++) {
            var markervalueinnerdiv = document.createElement('div');
            markervalueinnerdiv.title = title[i];
            markervalueinnerdiv.style.display = 'inline';
            markervalueinnerdiv.style.marginLeft = '5px';
            charmarkervalues[name+'sel'+i] = document.createTextNode(value[i]);
            markervalueinnerdiv.appendChild(charmarkervalues[name+'sel'+i]);
            markervaluediv.appendChild(markervalueinnerdiv);
        }
        document.getElementById(name+"chartchartmarkerleft").appendChild(markervaluediv);
        document.getElementById(name+"chartchartmarkerleft").onmousedown = function(event) { onChartMouseDown(event,this,0); };
        document.getElementById(name+"chartchartmarkerleft").onmouseup = function(event) { onChartMouseUp(event,this,0); };
        document.getElementById(name+"chartchartmarkerleft").oncontextmenu = function(event) { return false; };
        
        charmarkerdiv[name+'sel'] = markervaluediv;
        
    }
    
    var w = (parseInt(document.getElementById(name+"chartchartmarkerright").style.left)+10 - parseInt(document.getElementById(name+"chartchartmarkerleft").style.left) - parseInt(charmarkerdiv[name+'sel'].offsetWidth))/2;
    charmarkerdiv[name+'sel'].style.marginLeft = w + "px";*/
}

/* Recompute and refresh current point infos */
function refreshCurrentPointInfos(point_id) {
    var infos = '';
    if(track_points[point_id].time!='None') {
        infos = infos + '<b>Time:</b> '+track_points[point_id].time;
    }
    if(track_points[point_id].spd>=0.0) {
		infos = infos + '<br/><b>Speed:</b> '+track_points[point_id].spd.toFixed(2)+' '+spdunit;
        updateChartMarkerValue("spdtime",track_points[point_id].spd.toFixed(2)+' '+spdunit,'Instant speed');
    }
    if (!flat) {
        infos = infos + '<br/><b>Elevation:</b> '+track_points[point_id].ele+' m';
        updateChartMarkerValue("eledist",track_points[point_id].ele+' m','Elevation');
    }
    if (wind) {
        infos = infos + '<br/><b>Course:</b> '+track_points[point_id].course+'&deg;';
        if(track_points[point_id].spd>=0.0) {
            if(winddirorbuoy) {
                infos = infos + '<br/><b>VMG:</b> '+(track_points[point_id].spd*Math.cos((track_points[point_id].course - winddir)*Math.PI/180)).toFixed(2)+' '+spdunit;
            }
            else {
                infos = infos + '<br/><b>VMG:</b> '+(track_points[point_id].spd*computeVmgCosForBuoy(track_points[point_id].lat,track_points[point_id].lon,track_points[point_id].course)).toFixed(2)+' '+spdunit;
            }
        }
    }
    if(typeof track_points[point_id].hr!='undefined') {
        infos = infos + '<br/><b>Heart rate:</b> '+track_points[point_id].hr;
    }
    if(typeof track_points[point_id].cumul_dplus!='undefined') {
        infos += '<br/><b>D+:</b> '+track_points[point_id].cumul_dplus;
    }
    if(typeof track_points[point_id].cumul_dminus!='undefined') {
        infos += '<br/><b>D-:</b> '+track_points[point_id].cumul_dminus;
    }
    document.getElementById("current_point_infos").innerHTML = infos;    
}

/* return a string that represents a time delta */
function secondsToTimeString(seconds) {
    if (seconds>=60) {
        var minutes = Math.floor(seconds / 60);
        seconds -= minutes*60;
        if (seconds<10) { seconds = '0'+seconds; }
        if (minutes>=60) {
            var hours = Math.floor(minutes / 60);
            minutes -= hours*60;
            if (minutes<10) { minutes = '0'+minutes; }
            return hours+':'+minutes+':'+seconds;
        }
        return minutes+':'+seconds;
    }
    return seconds+' s';
}

function tom180p180(deg) {
    deg=deg%360;
    if((deg>-180)&&(deg<=180)) {
        return(deg);
    }
    else if(deg>180) {
        return (deg-360);
    }
    else if(deg<=-180) {
        return (deg+360);
    }
    else {
        return (deg);
    }
}

/* Recompute and refresh selection infos */
function refreshSelectionInfos(pt1_id, pt_cur, pt2_id) {
	if ((pt1_id >= 0 && pt1_id < nbpts)&&(pt2_id >= 0 && pt2_id < nbpts)) {
        
        selfirstptid = pt1_id;
        sellastptid = pt2_id;
        
		// Compute infos
		var hdist = geodeticDist(track_points[pt2_id].lat,track_points[pt2_id].lon,
			track_points[pt1_id].lat,track_points[pt1_id].lon);
		var vdist = track_points[pt2_id].ele-track_points[pt1_id].ele;
        var slope = 0.0;
		if (hdist>0) {
			slope = vdist * 100.0 / hdist;
		}
		
		// Display infos
        var timediff = -1;
        if ((track_points[pt2_id].time!='None')&&(track_points[pt1_id].time!='None')) {
            timediff = (parseTimeString(track_points[pt2_id].time)-parseTimeString(track_points[pt1_id].time));
        }
		var infos = '';
        //infos = infos + pt1_id+','+pt2_id+'<br/>';
        var lenpath=computeLengtOnPath(parseInt(pt1_id), parseInt(pt2_id));
        infos = infos +
		'<b>Direct distance:</b> '+Math.round(hdist)+' m<br/>' +
        '<b>Distance on path:</b> '+Math.round(lenpath)+' m';
        if (timediff>=0) {
            infos = infos + '<br/><b>Speed:</b> '+convertSpeed(hdist/timediff,spdunit).toFixed(2)+ ' '+spdunit;
            updateSelChartMarkerValue('spdtime',[convertSpeed(lenpath/timediff,spdunit).toFixed(2)+ ' '+spdunit,convertSpeed(hdist/timediff,spdunit).toFixed(2)+ ' '+spdunit],['Speed on path','Direct speed']);
        }
		if (!flat) {
            var infoselechart = [Math.round(vdist)+' m',Math.round(slope)+'%'];
            var infoseletitle = ['Height gain/loss','Slope'];
			infos = infos +
			'<br/><b>D:</b> '+Math.round(vdist)+' m<br/>' +
			'<b>Slope:</b> '+Math.round(slope)+' %';
            if (timediff>=0) {
                infos = infos + '<br/><b>Vert. spd:</b> '+Math.round(vdist*3600/timediff)+' m/h';
                infoselechart.push(Math.round(vdist*3600/timediff)+' m/h');
                infoseletitle[infoseletitle.length] = 'Vert. speed';
            }
            updateSelChartMarkerValue('eledist',infoselechart,infoseletitle);
		}
		if (wind) {
            var course = computeCourse(
				track_points[pt1_id].lat,track_points[pt1_id].lon,
				track_points[pt2_id].lat,track_points[pt2_id].lon);
			infos = infos +
			'<br/><b>Course abs.:</b> ' + Math.round(course)+'&deg;'+
            '<br/><b>Course rel.:</b> ' + tom180p180(Math.round(course - winddir))+'&deg;';
            if (timediff>=0) {
                if(winddirorbuoy) {
                    infos = infos +
                        '<br/><b>VMG:</b> ' + convertSpeed(hdist * Math.cos((course - winddir)*Math.PI/180) / timediff,spdunit).toFixed(2)+' '+spdunit;
                }
                else {
                    infos = infos +
                        '<br/><b>VMG:</b> ' + convertSpeed(hdist * computeVmgCosForBuoy(track_points[pt1_id].lat,track_points[pt1_id].lon,course) / timediff,spdunit).toFixed(2)+' '+spdunit;
                }
            }
            if(pt_cur!=-1) {
                infos = infos +
                '<br/><b>Angle:</b> ' + Math.round(computeAngle(
                    track_points[pt1_id].lat,track_points[pt1_id].lon,
                    track_points[pt_cur].lat,track_points[pt_cur].lon,
                    track_points[pt2_id].lat,track_points[pt2_id].lon))+'&deg;';            
            }
            
		}
        if (timediff>=0) {
            infos = infos + '<br/><b>Time delta:</b> '+secondsToTimeString(timediff);
        }
		document.getElementById('selection_infos').innerHTML=infos;
	}
	else {
		document.getElementById('selection_infos').innerHTML = 'No selection';
	}
}

function getSelFirstPtId() {
    return (selfirstptid);
}

function getSelLastPtId() {
    return (sellastptid);
}

function guessWindDir() {
    var cptr,min_cptr=nbpts,min_angle=-1,angle;
    var polar = new Array();
    i = 0;
    for(angle=0;angle<360;angle+=10) {
        cptr = 0;
        for(ptid in track_points) {
            if ((track_points[ptid].course>=angle)&&(track_points[ptid].course<(parseInt(angle)+15))) {
                cptr++;
            }
        }
        if (cptr<min_cptr) {
            min_cptr = cptr;
            min_angle = angle+5;
        }
        polar[i] = cptr;
        i++;
    }
    return min_angle;
}

COMMENT_ADD = '<a href="javascript:void(0);return false;" onclick="toogleAddComment();">Add</a>';

function toogleAddComment() {
    document.getElementById('comments').innerHTML = '<table><tbody><tr><td>'+
        '<textarea rows="5" cols="20" id="comment_inputtxtbox"></textarea>'+
        '</td><td style="vertical-align:bottom;">'+
        '<input id="comment_cancelbtn" type="button" value="Cancel" onclick="onCommentCancelClick();"/><br/>'+
        '<input id="comment_okbtn" type="button" value="OK" onclick="onCommentOkClick();"/>'+
        '</td></tr></tbody></table>';
}

function onCommentCancelClick() {
    fillComments();
}

function onCommentOkClick() {
    var comment = document.getElementById('comment_inputtxtbox').value;
    if (comment.length>0) {
        sendComment(comment);
        document.getElementById('comments').innerHTML = 'Sending...';
    }
}

function sendComment(comment) {
    var req = new XMLHttpRequest();
    var url = '/sendcomment/'+mapid+'/'+encodeURIComponent(htmlentities(comment));
    var user_sess = getSessionFromCookie();
    if (user_sess.length>0) {
        url = url + '&user='+user_sess[0] + '&sess=' + user_sess[1];
    }
    req.open("GET", url, true);
    req.onreadystatechange = onSendCommentAnswer;
    req.send(null);
}

function onSendCommentAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            var result;
            result = this.responseXML.getElementsByTagName("result")[0].childNodes[0].nodeValue;
            if (result=='OK') {
                fillComments();
            }
            else {
                document.getElementById('comments').innerHTML = '<b>Error:</b> '+result;
            }
        }
    }
}

function fillComments() {
    var req = new XMLHttpRequest();
    var url = '/comments/'+mapid;
    var req = new XMLHttpRequest();
    req.open("GET", url, true);
    req.onreadystatechange = onGetCommentsAnswer;
    req.send(null);
}

function onGetCommentsAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            var comments = this.responseXML.getElementsByTagName("comment");
            var out = '';
            for (var i=0;i<comments.length;i++) {
                var d = comments[i].getAttribute("date");
                var user = comments[i].getAttribute("user");
                var comment = '';
                if (comments[i].childNodes[0]) {
                    comment = comments[i].childNodes[0].nodeValue;
                }
                out = out + '<i>'+d+'</i> by <b>' + user + ':</b> ' + comment + '<br/>';
            }
            document.getElementById('comments').innerHTML = out + COMMENT_ADD;
        }
    }
}

/* When user choose to use buoy instead of winddir slider */
function useBuoy() {
    var windirbox_height = getComputedHeight('windirbox');
    document.getElementById('windirbox').style.display = 'none';
    document.getElementById('use_buoy').style.display = 'none';
    document.getElementById('use_windir').style.display = 'block';
    document.getElementById('use_windir').style.height = windirbox_height;
    addBuoyMarker();
    winddirorbuoy = 0;
}

/* When user choose to use winddir slider instead of buoy */
function useWinddir() {
    document.getElementById('use_windir').style.display = 'none';
    document.getElementById('windirbox').style.display = 'block';
    document.getElementById('use_buoy').style.display = 'block';
    removeBuoyMarker();
    winddirorbuoy = 1;
    winddirslider.onchange();
}

/* Called by the map when buoy marker has been moved */
function refreshBuoyMarker(lat,lon) {
    buoy_lat = lat;
    buoy_lon = lon;
    refreshSelectionInfos(getSelFirstPtId(),last_point_id,getSelLastPtId());
    refreshCurrentPointInfos(last_point_id);
}

/* Computes the VMG cosinus using buoy */
function computeVmgCosForBuoy(boat_lat,boat_lon,course) {
    var w = computeCourse(boat_lat,boat_lon,buoy_lat,buoy_lon);
    /*var course = computeCourse(boat_lat,boat_lon,boatdir_lat,boatdir_lon);*/
    return Math.cos((course-w)*Math.PI/180);
}

/* save wind direction to database */
function saveWindDir() {
    putToDbNoAck(mapid,getPwdFromCookie(mapid),'winddir',winddir);
}

/* called when winddir is got from db */
function onGetWindDir(gotvalue) {
    dontsavewind = 1;
    winddirslider.setValue(gotvalue);
}

/* trigger load of winddir */
function loadWindDir() {
    getFromDbWithCallback(mapid,'winddir',onGetWindDir);
}

/* Draw winddir on Polar */
/*function refreshWinddirPolar() {
    polarcanva.clear();
    polarcanva.image(polarimgsrc,0,0,400,300);
    polarcanva.path("M150 150L"+(150+120*Math.cos((winddir-90)*Math.PI/180))+" "+(150+120*Math.sin((winddir-90)*Math.PI/180)));
}*/

/* Add DEMize button on elevation chart */
function addDemizeButton() {
    var demizebtndiv = document.createElement('div');
    demizebtndiv.style.marginTop = '15px';
    demizebtndiv.innerHTML = 'Bad/noisy elevations? Get clean elevation from Digital Elevation Model --&gt; <input id="demizebtn" type="button" value="DEMize" onclick="onDemizeClick();"/><div id="demizeresults" style="display: inline; marginLeft: 5px;"></div>';
    document.getElementById('eledistchart').appendChild(demizebtndiv);
}

/* Callback called when isdemized result got */
function onIsDemizedAnswer(value) {
    if (value!='Y') {
        addDemizeButton();
    }
}

/* Callback called when isdemized resulted an error */
function onIsDemizedError(errstring) {
    //in case of doubt, add the button
    addDemizeButton();
}

/* Add DEMize button on elevation chart if chart not already demized */
function addDemizeButtonIfNeeded() {
    getFromDbWithCallbackError(mapid,'demized',onIsDemizedAnswer,onIsDemizedError);
}

function computeSpeedIfNeeded() {
    var i;
    for(i=0;i<nbpts-1;i++) {
        if(track_points[i].spd==-1.0) {
            if((track_points[i].time!='None')&&(track_points[i+1].time!='None')) {
                var timediff = (parseTimeString(track_points[i+1].time)-parseTimeString(track_points[i].time));
                var hdist = geodeticDist(track_points[i+1].lat,track_points[i+1].lon,
                        track_points[i].lat,track_points[i].lon);
                track_points[i].spd = convertSpeed(hdist/timediff,spdunit);
            }
        }
    }
}

var todelete = [];

function onMapKeyDown(e) {
	var ev = e || window.event;
	var char_code = (ev.which) ? ev.which : ev.keyCode;
	if(char_code==46) {
		//alert("del "+last_point_id);
		var todel_id = last_point_id;
		todelete.push(todel_id);
		track_points.splice(todel_id,1);
		nbpts--;
		onTrackPointsChanged();
	}
}

function focusToMap() {
	document.getElementById("map").focus();
}

function onTrackPointsChanged() {
	currentpointslider.setMaximum(nbpts);
	currentpointslider.setBlockIncrement(parseInt(nbpts/20) + 1);
	redrawTrack();
}

function onSubmitDeleteClick() {
	//alert(todelete);
	onDelPtListClick();
}

function toogleTab(e) {
  var eid=e.id.substr(3);
  document.getElementById(eid).style.display='block';
  var charts = document.getElementsByClassName("chart");
  var i;
  for(i=0;i<charts.length;i++) {
    if(charts[i].id!=eid) {
      charts[i].style.display='none';
    }
  }
  var labels = document.getElementById("chartlabels");
  for(i=0;i<labels.children.length;i++) {
    if(labels.children[i]!=e) {
      labels.children[i].className='chartlabel';
    }
  }
  e.className='chartlabelselected';
}

function onChartSelected(chartid,minx,maxx) {
    var i,mini = -1,maxi=-1;
    for(i=0;i<chartdata[chartid][0].data.length;i++) {
        if ((mini==-1)&&(chartdata[chartid][0].data[i][0]>=minx)) {
            mini = i;
        }
        if ((maxi==-1)&&(chartdata[chartid][0].data[i][0]>=maxx)) {
            maxi = i;
            break;
        }
    }
    refreshSelection(mini,maxi);
    selchartid = chartid;
    chartzoombtn[chartid].minx = minx;
    chartzoombtn[chartid].maxx = maxx;
    chartzoombtn[chartid].style.display="inline";
}

function onChartUnselected(chartid) {
    //console.log("onChartUnselected %s",chartid);
    chartzoombtn[chartid].style.display="none";
}

function doChartZoom(chartid,minx,maxx) {
    plot[chartid] = $.plot(placeholder[chartid], chartdata[chartid], $.extend(true, {}, chartoptions[chartid], 
        {xaxis: {min: minx,max: maxx}}));
}

function onChartZoom(btn,chartid) {
    doChartZoom(chartid,btn.minx,btn.maxx);
    chartzoomresetbtn[chartid].minx=btn.minx;
    chartzoomresetbtn[chartid].maxx=btn.maxx;
    chartzoombtn[chartid].style.display="none";
    chartzoomresetbtn[chartid].style.display="inline";
}

function onChartZoomReset(btn,chartid) {
    doChartZoom(chartid,chartdata[chartid][0].data[0][0],chartdata[chartid][0].data[chartdata[chartid][0].data.length-1][0]);
    plot[chartid].setSelection({xaxis: {from: btn.minx,to: btn.maxx}});
    chartzoomresetbtn[chartid].style.display="none";
}

function onChartCurrentPointChange(chartid,idx) {
    refreshCurrentPoint(idx);
}

function moveChartSelection(chartid,ptidfrom,ptidto) {
    if(ptidfrom==-1)
        plot[chartid].clearSelection();
    else
        plot[chartid].setSelection({
            xaxis: {
                from: chartdata[chartid][0].data[ptidfrom][0],
                to: chartdata[chartid][0].data[ptidto][0]
            }
        });
}

function moveChartMarker(chartid,ptid) {
    if(typeof plot[chartid]=="undefined") return; //not ready
    var o = plot[chartid].pointOffset({x:chartdata[chartid][0].data[ptid][0],y:chartdata[chartid][0].data[ptid][1]});
    var chartmarker = $("#chartmaker"+chartid);
    if(chartmarker.length == 0) {
        placeholder[chartid].append("<div id=\'chartmaker"+chartid+"\' style=\'position:absolute;left:"+(o.left)+"px;top:"+plot[chartid].getPlotOffset().top+"px;height:"+plot[chartid].height()+"px;width:1px;background-color:black;\'></div>");
    }
    else {
        chartmarker[0].style.left = o.left+"px";
    }
}

function pauseAreas(chartlineid) {
    var markings = [];
    var i;
    for(i=0;i<pauses.length;i++) {
        markings.push({xaxis: { from: chartdata[chartlineid][0]["data"][pauses[i][0]][0], to: chartdata[chartlineid][0]["data"][pauses[i][1]][0] }});
    }
    //console.log("pauseAreas(%d) markings=%o",chartlineid,markings);
    return markings;
}

function refreshPauseAreas() {
    var i;
    for(i=0;i<chartdata.length;i++) {
        chartoptions[i]["grid"]["markings"] = pauseAreas(i);
        //plot[i]["options"]["grid"]["markings"] = pauseAreas(i);
        //plot[i] = $.plot(placeholder[i], chartdata[i], $.extend(true, {}, chartoptions[i], {grid:{markings:pauseAreas(i)}}));
        plot[i] = $.plot(placeholder[i], chartdata[i], chartoptions[i]);
    }
}


var selfirstptid = -1;
var sellastptid = -1;
var last_point_id = -1;

// Sliders
var currentpointslider;
var playingspeedslider;
var snakelengthslider;

if(wind) {
    var winddirslider;
    var winddir = 180;
    var winddirorbuoy = 1;
    var dontsavewind = 1;
    var polar;
    var polarimgsrc;
    var polarcanva;
}

// For flot charts 
var chartdata = [];
var plot = [];
var placeholder = [];
var chartzoombtn = [];
var chartzoomresetbtn = [];
var chartoptions = [];
var linecharts = [];
var options = {
    series: {
        lines: {
            show: true
        },
        points: {
            show: false
        }
    },
    legend: {
        noColumns: 2
    },
    xaxis: {
        tickDecimals: 0
    },
    yaxis: {
        //min: 0
    },
    selection: {
        mode: "x"
    },
    grid:{clickable: true}
};
var optionstime = {
    series: {
        lines: {
            show: true
        },
        points: {
            show: false
        }
    },
    legend: {
        noColumns: 2
    },
    xaxis: {
        //tickDecimals: 0
        mode: "time",
        timeformat: "%H:%M:%S"
    },
    yaxis: {
        //min: 0
    },
    selection: {
        mode: "x"
    },
    grid:{
        clickable: true
    }
};


//Get from DB
//getFromDb(mapid,'trackdesc');
//getFromDb(mapid,'trackuser');
//getFromDb(mapid,'date');

//Sliders creation
currentpointslider = new Slider(document.getElementById("currentpoint-slider"), document.getElementById("currentpoint-slider-input"));
currentpointslider.setMinimum(0);
currentpointslider.setMaximum(nbpts);
currentpointslider.setValue(0);
currentpointslider.setBlockIncrement(parseInt(nbpts/20) + 1);
currentpointslider.onchange = function () {
	refreshCurrentPoint(currentpointslider.getValue());
}
playingspeedslider = new Slider(document.getElementById("playingspeed-slider"), document.getElementById("playingspeed-slider-input"));
playingnbpts = 1;
playingspeedslider.setValue(11);
playingspeedslider.onchange = function () {
	playingnbpts = playingspeedslider.getValue()-10;
}

snakelengthslider = new Slider(document.getElementById("snakelength-slider"), document.getElementById("snakelength-slider-input"));
snakelength = 50;
snakelengthslider.setValue(50);

if (wind) {
    winddirslider = new Slider(document.getElementById("winddir-slider"), document.getElementById("winddir-slider-input"));

    /* add windir indicator in polar */
    // Get Polar
    /*
//    polar = document.getElementById("polarchart").getElementsByTagName("img")[0];
    polar = document.getElementById("polargraph");
    // Hide polar
    polar.style.display="none";
    //document.getElementById("polarchart").style.height=500;
    // Save image src
    polarimgsrc = polar.getAttribute("src");
    // Create canva
    polarcanva = Raphael("polarchart",400,300);
    // Redraw polar and add line
    refreshWinddirPolar();*/
    //refreshBestVMGs();
    
    winddirslider.setMinimum(0);
    winddirslider.setMaximum(359);
    winddirslider.onchange = function () {
        winddir = winddirslider.getValue();
        var lbl = degreesToCardinalDir(winddir);
        document.getElementById("winddir-value").innerHTML = winddir + " &deg; ("+lbl+")";
        refreshSelectionInfos(getSelFirstPtId(),last_point_id,getSelLastPtId());
        if (last_point_id!=-1) {
            refreshCurrentPointInfos(last_point_id);
        }
        /* dontsavewind: saveWindDir is not called on map loading */
        if(dontsavewind) {
            dontsavewind = 0;
        }
        else {
            if(typeof windsave_timeout!='undefined') {
                clearTimeout(windsave_timeout);
            }
            windsave_timeout = setTimeout("saveWindDir();",5000);
        }
        refreshWinddirPolar();
        refreshBestVMGs();
    }
    winddirslider.setValue(guessWindDir());
    /*winddirslider.onchange();*/
    loadWindDir();
   
}

if(!flat) {
    addDemizeButtonIfNeeded();
}

fillComments();

computeSpeedIfNeeded();


$(function() {
    var i,j;
    for(i=0,j=0;i<chart.length;i++) {
        if(chart[i]['type']=='line') {
            chartdata[j] = [chart[i]];
            placeholder[j] = $("#chart"+chart[i]['name']);
            placeholder[j][0].chartid=j;
            chartzoombtn[j] = $("#chartzoombtn"+chart[i]['name'])[0];
            chartzoomresetbtn[j] = $("#chartzoomresetbtn"+chart[i]['name'])[0];
            chartoptions[j] = ((chart[i]['timerange'])?optionstime:options);
            
            chartoptions[j]["grid"]["markings"] = pauseAreas(j);
            
            plot[j] = $.plot(placeholder[j], chartdata[j], chartoptions[j]);
            placeholder[j].bind("plotselected", function (event, ranges) {onChartSelected(event.target.chartid,ranges.xaxis.from,ranges.xaxis.to);});
            placeholder[j].bind("plotunselected", function (event) {onChartUnselected(event.target.chartid);});
            placeholder[j].bind("plotclick", function (event, pos, item) { if (item) onChartCurrentPointChange(event.target.chartid,item.dataIndex);});
            linecharts.push({pt1_id:-1,pt2_id:-1});
            j++;
        }
    }
    toogleTab(document.getElementsByClassName("chartlabel")[0]);
});
