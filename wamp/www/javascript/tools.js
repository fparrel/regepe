
function onSelClearClick() {
    if (confirm("Remove selected part from the track?")) { 
        cutMap('clear');
    }
}

function onSelCropClick() {
    if (confirm("Keep only the selected part of track?")) { 
        cutMap('crop');
    }
}

function onDelCurPtClick() {
    var ptid = last_point_id;
    if(ptid!=-1) {
        var pwd = getPwdFromCookie(mapid);
        var url = '/cgi-bin/cutmap.py?mapid='+mapid+'&fisrtptid='+ptid+'&lastptid='+(ptid+1)+'&action=clear&pwd='+pwd;
        var user_sess = getSessionFromCookie();
        if (user_sess.length>0) {
            url = url + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
        }
        //window.location.replace("http://www.un-site.com/une-page.htm");
        document.location.href = url;        
    }
}

function onDelPtListClick() {
    var ptid = last_point_id;
    if(ptid!=-1) {
        var pwd = getPwdFromCookie(mapid);
        var url = '/cgi-bin/cutmap.py?mapid='+mapid+'&pwd='+pwd+'&action=delptlist&ptlist='+todelete;
        var user_sess = getSessionFromCookie();
        if (user_sess.length>0) {
            url = url + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
        }
        //window.location.replace("http://www.un-site.com/une-page.htm");
        document.location.href = url;        
    }
}


function cutMap(action) {
    var firstptid = getSelFirstPtId();
    var lastptid = getSelLastPtId();
    //alert(firstptid+' '+lastptid);
    if ((firstptid!=-1)&&(lastptid!=-1)) {
        var pwd = getPwdFromCookie(mapid);
        var url = '/cgi-bin/cutmap.py?mapid='+mapid+'&fisrtptid='+firstptid+'&lastptid='+lastptid+'&action='+action+'&pwd='+pwd;
        var user_sess = getSessionFromCookie();
        if (user_sess.length>0) {
            url = url + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
        }
        //window.location.replace("http://www.un-site.com/une-page.htm");
        document.location.href = url;
    }
}

function onMapDeleteClick() {
    if (confirm("Confirm deletion of this map?")) { 
        var pwd = getPwdFromCookie(mapid);
        var url = '/cgi-bin/delmap.py?mapid='+mapid+'&pwd='+pwd;
        var user_sess = getSessionFromCookie();
        if (user_sess.length>0) {
            url = url + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
        }
        document.location.href = url;
    }
}
 
function onMapExportClick() {
    var url = '/cgi-bin/togpx.py?mapid='+mapid;
    document.location.href = url;
/*
    var gpxfile = '<?xml version="1.0" encoding="UTF-8"?>\n'+
'<gpx version="1.0" creator="regepe - http://www.regepe.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n'+
'<trk><trkseg>\n';
    for (i in track_points) {
        gpxfile += '<trkpt lat="'+track_points[i].lat+
            '" lon="'+track_points[i].lon+
            '">\n<ele>'+track_points[i].ele+
            '</ele>\n<course>'+track_points[i].course+
            '</course><speed>'+track_points[i].spd+
            '</speed>\n</trkpt>\n';
    }
    gpxfile += '</trkseg></trk></gpx>\n';
    */
}

function onDemizeAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            var result = this.responseXML.getElementsByTagName("result")[0].childNodes[0].nodeValue;
            if (result=='OK') {
                var nextindex = this.responseXML.getElementsByTagName("nextindex")[0].childNodes[0].nodeValue;
                var percent = this.responseXML.getElementsByTagName("percent")[0].childNodes[0].nodeValue;
                document.getElementById('demizeresults').innerHTML = ' '+percent+'% <img src="/images/loading.svg" width="16" height="16"/>';
                var url = this.url + '&index=' + nextindex;
                var req = new XMLHttpRequest();
                req.url = this.url;
                req.open("GET", url, true);
                req.onreadystatechange = onDemizeAnswer;
                req.send(null);
            }
            else if (result=='Done') {
                document.getElementById('demizeresults').innerHTML = 'Done';
                window.location.reload();
            }
            else {
                document.getElementById('demizeresults').innerHTML = '<b>Error:</b> '+result;
            }
        }
        else if (this.status == 500) {
            document.getElementById('demizeresults').innerHTML = 'Internal Error, please retry';
        }
    }
}

function onDemizeClick() {
    var pwd = getPwdFromCookie(mapid);
    var url = '/cgi-bin/demize.py?mapid='+mapid+'&pwd='+pwd;
    var user_sess = getSessionFromCookie();
    if (user_sess.length>0) {
        url = url + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
    }
    var req = new XMLHttpRequest();
    req.url = url;
    req.open("GET", url, true);
    req.onreadystatechange = onDemizeAnswer;
    req.send(null);
    document.getElementById('demizeresults').innerHTML = ' 0 % <img src="/images/loading.svg" width="16" height="16"/>';
    /*document.location.href = url;*/
}
