<?php
$map_type='GeoPortal'; 

if (array_key_exists('ptlist',$_GET)) {
    foreach(explode('~',$_GET['ptlist']) as $ptstr) {
        $ptarray = explode(',',$ptstr);
        $pt = array('lat'=>floatval($ptarray[0]),'lon'=>floatval($ptarray[1]));
        if (count($ptarray)>=3) {
            $pt['ele'] = intval($ptarray[2]);
        }
        $ptlist[] = $pt;
    }
}
if (array_key_exists('names',$_GET)) {
    $i = 0;
    foreach(explode('~',$_GET['names']) as $name) {
        $ptlist[$i]['name'] = $name;
        $i++;
    }
}
if (array_key_exists('maptype',$_GET)) {
    $map_type=$_GET['maptype'];
}
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html xmlns:og="http://opengraphprotocol.org/schema/" xmlns:fb="http://ogp.me/ns/fb#">
<head>
<title>Replay your GPS tracks with ReGePe</title>
<meta http-equiv="X-UA-Compatible" content="IE=7"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script type="text/javascript" src='javascript/raphael-min.js'></script>
<script type="text/javascript" src='javascript/g.raphael-min.js'></script>
<script type="text/javascript" src='javascript/g.line-min.js'></script>
<script type="text/javascript" src="javascript/jquery.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.selection.js"></script>
<script type="text/javascript" src="javascript/jquery.flot.time.js"></script>
<link type="text/css" rel="StyleSheet" href="styles/mapstyle.css" />
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<meta name="robots" content="noindex">
</head>
<body>
    <div id="wrapper">
<?php include('header.html'); ?>
        <div id="body">
            <div id="mapnwpts" style="float:left; margin:10px 0px;">
                <div id="maptotal" style="float: left;">
                    <div id="mapresizer" style="height:500px;width:500px;resize:both; border:2px solid;overflow:auto;padding:8px;">
<?php if ($map_type=='GMaps') { ?>
                        <div id="map" style="height:100%;width:100%;" class="map" title="Click on map to add a point" onmousewheel="onMapMouseWheel(event);" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } else if ($map_type=='GeoPortal') { ?>
                        <div id="map" style="height:500px;width:500px;" title="Click on map to add a point" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } else if ($map_type=='MapQuest') { ?>
                        <div id="map" style="height:100%;width:100%;" title="Click on map to add a point" tabindex="0" onkeydown="onMapKeyDown(event);"></div>
<?php } ?>
                    </div>
                    <div>Switch to: <?php
$maptypes=array("GeoPortal"=>"Geo Portail","GMaps"=>"Google Maps","MapQuest"=>"Open Street Map");
foreach($maptypes as $maptype=>$maptypedesc) {
	if($map_type!=$maptype) {
		print '<a id="switch2'.$maptype.'" href="/prepare.php?maptype='.$maptype.'"/>'.$maptypedesc.'</a> ';
	}
}
?>
                    </div>
                </div>
                <div id="wpts" style="float: left; margin:10px;overflow:auto; height: 500px; width:170px;"><b>Waypoints</b></div>
            </div>
            <div style="clear:both;"></div>
            <div id="wpttools">
                <input id="clearbtn" type="button" value="Clear" onclick="onClearClick();"/>
                <input id="deletebtn" type="button" value="Delete selected point" onclick="onDeleteClick();"/>
            </div>
            <div id="itiinfos" style="margin-top:10px;"><b>Length:</b> <span id="length"></span> <b>D+:</b> <span id="dplus"></span> <b>D-:</b> <span id="dminus"></span></div>
            <div id="profile" style="margin-top:10px;">
                <input id="compprofilebtn" type="button" value="Compute Profile" onclick="onComputeProfileClick();"/><img id="compprofileloading" />
                <div style="clear:both;"></div>
                <div id="profile_infos" style="float: left; line-height:1.5em; height:6em; border: 1px solid; display: none;">&nbsp;</div>
                <div id="curpt_infos" style="float: left; line-height:1.5em; height:6em; border: 1px solid; display: none;">&nbsp;</div>
                <div style="clear:both;"></div>
                <div id="profilechartntitlenctrl" style="display:inline-block;">
                    <div id="profile_img" style="width:800px;height:200px;border-style:solid;border-width:1px;">
                        <div class="chart" id="profilechart" style="padding:0; border: 0px;width:800px;height:200px">
                        </div>
                    </div>
                    <div id="profile_title" style="font-style:italic;text-align:center;">&nbsp;</div>
                </div>
            </div>
            <div id="export" style="margin-top:10px;">
                <!--<input id="exportbtn" type="button" value="Export" onclick="onExportClick();" />-->
                <b>Export to file:</b> 
                <select id="exportformat" name="exportformat" onchange="onExportFmtChange();">
                    <option value="wpt">.wpt (OziExplorer)</option>
                    <option value="gpx">GPX</option>
                </select>
                <select id="exportallnamed" name="exportallnamed" onchange="onExportAllOrNamedChange();">
                    <option value="all">All points</option>
                    <option value="named">Only labeled points</option>
                </select>
                <a id="exporthref" href="">Export</a>        <!--
                <a id="exporthref" href="javascript:doExport();">Export</a>
                -->
            </div>
            <div id="geturl" style="margin-top:10px;">
                <b>Share:</b> <input id="geturlbtn" type="button" value="Send as URL" onclick="onGetUrlClick();" />
                <input id="urllnk" type="text" value="" size="30" style="visibility:hidden;"/>
            </div>
            <div id="printmap" style="margin-top:10px;">
                <input type="button" value="Print Map" onclick="onBuildMapClick();"/>
            </div>
        </div>
        <div id="footer_push"></div>
    </div>
</div>
<?php include('footer.html'); ?>
</body>
</html>
<?php if ($map_type=='GMaps') { ?>
<!--<script type="text/javascript" src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=${GMapsApiKey}"></script>-->
<script type="text/javascript" src="//maps.googleapis.com/maps/api/js?key=${GMapsApiKey2}&sensor=false"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" charset="utf-8" src='http://api.ign.fr/geoportail/api/js/2.0.0/Geoportal.js'><!-- --></script>
<style type="text/css" media="print">
body{display:inline;}
</style>
<?php } else if ($map_type=='MapQuest') { ?>
<script src='http://open.mapquestapi.com/sdk/js/v7.0.s/mqa.toolkit.js'></script> 
<?php } ?>
<script type="application/javascript" src="javascript/utils.js"></script>
<script type="application/javascript" src="javascript/xmlhttprequest.js"></script>
<script type="application/javascript" src="javascript/header.js"></script>
<script type="application/javascript" src="javascript/db.js"></script>
<script type="application/javascript">
//<![CDATA[

var pts_from_url=[];
<?php
if (isset($ptlist)) {
    $i = 0;
    foreach($ptlist as $pt) {
?>
pts_from_url[<?php echo $i; ?>] = new Point(<?php echo $pt['lat']; ?>,<?php echo $pt['lon']; ?>);
<?php
        if(array_key_exists('ele',$pt)) {
?>
pts_from_url[<?php echo $i; ?>].ele = <?php echo $pt['ele']; ?>;
<?php
        }
        if(array_key_exists('name',$pt)) {
?>
pts_from_url[<?php echo $i; ?>].name = "<?php echo $pt['name']; ?>";
<?php
        }
        $i++;
    }
}
?>

// list of points object, map_type dependant
// fields:
//  .pt_index
//  .pt
var points = [];

// list of markers for easy remove
var markers = [];

// list of waypoints on the right
// fields:
//.wptname
var wptlbl = [];

// current selection index
var sel_index = -1;

/* Creates a point object */
function Point(lat,lon,previous_pt) {
    this.lat = lat; // latitude  in decimal degrees
    this.lon = lon; // longitude in decimal degrees
    //[optional] ele : elevation in m
    //[optional] elelbl : elevation label
    if(typeof(previous_pt)=='undefined') {
        this.dist = 0.0;
    }
    else {
        console.log('plat='+previous_pt.lat); 
        this.dist = previous_pt.dist + geodeticDist(previous_pt.lat,previous_pt.lon,lat,lon);
    }
    console.log('thisdist='+this.dist);
}

/* Build a points list for passing through a GET url */
function buildPtlistUrl(pointslist) {
    var out = '';    
    var i;
    for(i=0;i<pointslist.length;i++) {
        if(i>0) {
            out += '~';
        }
        out += pointslist[i].lat.toFixed(6)+','+pointslist[i].lon.toFixed(6);
        if (typeof pointslist[i].ele != "undefined") {
            out += ','+pointslist[i].ele;
        }
    }
    return out;
}

/* Build a names list for passing through a GET url */
function buildNamesListUrl() {
    var i;
    var namesurl = '';
    for(i=0;i<points.length;i++) {
        if(i>0) { namesurl +='~'; }
        namesurl += wptlbl[i].wptname.value.replace('~',' ');
    }
    return namesurl;
}

/* When user clicks on GetUrl button */
function onGetUrlClick() {
    var ptlisturl = buildPtlistUrl(getLatLonList());
    var namesurl = buildNamesListUrl();
    document.getElementById('urllnk').value = 'http://localhost/prepare.php?ptlist='+ptlisturl+'&names='+namesurl+'&maptype=<?php echo $map_type; ?>';
    document.getElementById('urllnk').style.visibility = 'visible';
}

/* When user clicks on Export button */
function onExportClick() {
    var namesurl = buildNamesListUrl();
    var ptliststr = buildPtlistUrl(getLatLonList());
    var exportformat = document.getElementById('exportformat').value;
    var exporthref = document.createElement('a');
    exporthref.setAttribute('href','/cgi-bin/export.py?fmt='+exportformat+'&ptlist='+ptliststr+'&names='+namesurl);
    exporthref.innerHTML = 'Export';
    exporthref.setAttribute('onclick','this.innerHTML="";');
    document.getElementById('export').appendChild(exporthref);
}

function onExportFmtChange() {
    refreshUrls();
}

function onExportAllOrNamedChange() {
    refreshUrls();
}

/* ask elevation to the server for a given point */
function askElevation(pt) {
    var client = new XMLHttpRequest();
    client.pt = pt;
    client.open('GET','/cgi-bin/getele.py?lat='+pt.lat+'&lon='+pt.lon);
    client.send();
    client.onreadystatechange = onGetEleAnswer;
}

/* When server answer to a get elevation request */
function onGetEleAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            this.pt.elelbl.innerHTML = this.responseText+'m';
            this.pt.ele = parseInt(this.responseText);
            refreshLength();
            refreshGraph();
        }
    }
}

function computePathLengthAndEleDiff() {
    var i;
    var d;
    var l = 0;
    var dminus = 0;
    var dplus = 0;
    for(i=1;i<points.length;i++) {
        l += geodeticDist(points[i-1].pt.lat,points[i-1].pt.lon,points[i].pt.lat,points[i].pt.lon);
        points[i].pt.dist = l;
        if ((typeof points[i].pt.ele != "undefined")&&(typeof points[i-1].pt.ele != "undefined")) {
            d = points[i].pt.ele-points[i-1].pt.ele;
            if(d>0) dplus += d;
            else dminus += -d;
        }
    }
    return [l,dplus,dminus];
}

function refreshLength() {
    var res = computePathLengthAndEleDiff();
    document.getElementById('length').innerHTML = res[0].toFixed(0)+" m";
    document.getElementById('dplus').innerHTML = res[1].toFixed(0)+" m";
    document.getElementById('dminus').innerHTML = res[2].toFixed(0)+" m";
}

var maptypes=[<?php
$maptypes=array("GeoPortal"=>"Geo Portail","GMaps"=>"Google Maps","MapQuest"=>"Open Street Map");
foreach($maptypes as $maptype=>$maptypedesc) {
	if($map_type!=$maptype) {
		print '"'.$maptype.'",';
	}
}
?>];

function refreshUrls() {
    var ptlisturl = buildPtlistUrl(getLatLonList());
    var namesurl = buildNamesListUrl();
    var i;
    for(i=0;i<maptypes.length;i++) {
        document.getElementById('switch2'+maptypes[i]).href = 'http://localhost/prepare.php?ptlist='+ptlisturl+'&names='+namesurl+'&maptype='+maptypes[i];
    }
    document.getElementById('urllnk').value = 'http://localhost/prepare.php?ptlist='+ptlisturl+'&names='+namesurl+'&maptype=<?php echo $map_type; ?>';
    if(document.getElementById('exportallnamed').value=='named') {
        ptlisturl = "";
        namesurl = "";
        for(i=0;i<points.length;i++) {
            if (wptlbl[i].wptname.value) {
                if(i>0) {
                    ptlisturl += '|';
                    namesurl += '|';
                }
                ptlisturl += points[i].pt.lat+','+points[i].pt.lon;
                if (typeof points[i].pt.ele != "undefined") {
                    ptlisturl += ','+points[i].pt.ele;
                }
                namesurl += wptlbl[i].wptname.value;
            }
        }
    }
    document.getElementById('exporthref').setAttribute('href','/cgi-bin/export.py?fmt='+document.getElementById('exportformat').value+'&ptlist='+ptlisturl+'&names='+namesurl);
}

function onWptChange() {
    refreshUrls();
}

function onWptClick(index) {
    selectWpt(index);
    selectWptOnMap(index);
}

/* Add a waypoint to the list that is on the right of map */
function addWpt(pt,index) {
    var wpt = document.createElement('input');
    wpt.setAttribute('type','text');
    wpt.setAttribute('id','wptname'+(index+1));
    wpt.style.width='100%';
    wpt.onchange = onWptChange;
    
    if(typeof pt.name!='undefined') {
        wpt.setAttribute('value',pt.name);
    }
    
    var lbl = document.createElement('p');
    //lbl.innerHTML = index+': ';
    lbl.appendChild(wpt);
    var elelbl = document.createElement('div');
    elelbl.setAttribute('id','wptlbl'+(index+1));
    lbl.appendChild(elelbl);
    document.getElementById('wpts').appendChild(lbl);
    lbl.wptname=wpt;
    wptlbl[index] = lbl;
    pt.elelbl = elelbl;
    
    lbl.onclick = function() { onWptClick(index); }
    
    // for getting elevation
    if(typeof pt.ele!='undefined') {
        elelbl.innerHTML = pt.ele + ' m';
    }
    else {
        askElevation(pt);
    }
    
    //alert(latlon2tilerowcol(pt.lat,pt.lon,16));
}

/* Clear the waypoint list that is on the right of map */
function clearWpts() {
    document.getElementById('wpts').innerHTML = '<b>Waypoints</b>';
}

/* Clear the waypoint list that is on the right of map */
function removeWpt(index) {
    document.getElementById('wpts').removeChild(wptlbl[index]);
}

function selectWpt(index) {
    var i;
    for(i=0;i<points.length;i++) {
        wptlbl[i].style.background = (i==index)?'pink':'white';
        wptlbl[i].wptname.style.background = (i==index)?'pink':'white';
    }
    if(ptinput2px!=null) {
        selxPt = ptinput2px[index]+marginsize;
        refreshSelInfos();
    }
}

/* When user wants to clear map */
function onClearClick() {
    if (confirm("Clear track?")) {
        points = [];
        wptlbl = [];
        redrawLine();
        removeMarkers();
        clearWpts();
        refreshLength();
        refreshUrls();
        refreshGraph();
    }
}

/* When user wants to delete selected point */
function onDeleteClick() {
    if(sel_index!=-1) {
        removeMarker(sel_index);
        removeWpt(sel_index);
        points.splice(sel_index,1);
        wptlbl.splice(sel_index,1);
        markers.splice(sel_index,1);
        var i;
        for(i=sel_index;i<points.length;i++) {
            points[i].pt_index--;
            markers[i].pt_index--;
        }
        redrawLine();
        refreshLength();
        refreshUrls();
        refreshGraph();
        sel_index = -1;
    }
}

var eles;
var dists;
var marginsize;
var pt2px;
var ptinput2px=null;

var selxPt=-1;
var selxLeft=-1;
var selxRight=-1;
var noline=0;

function ptIndexFromPosx(posx) {
    if(posx<marginsize)
        return -1;
    var i;
    for(i=0;i<pt2px.length;i++) {
        if(posx<=pt2px[i]+marginsize)
            return i;
    }
    return -1;
    /*
    posx = posx - marginsize + 1;
    var r = Math.round(posx * eles.length / (800-marginsize-30));
    if(r<0) return -1;
    if(r>399) return -1;
    return r;*/
}
function posxFromPtIndex(i) {
    //return marginsize + Math.round(i * (800-marginsize-30) / eles.length) + 11;
    return pt2px[i]+marginsize+9;
}

function refreshSelInfos(up) {
    var i1 = ptIndexFromPosx(selxLeft);
    var i2 = ptIndexFromPosx(selxRight);
    var i0 = ptIndexFromPosx(selxPt);
    var profile_infos = "";
    var curpt_infos = "";
    //alert(i0+" "+i1+" "+i2);
    if((i1!=-1)&&((i2!=-1)||(!up))) {
        document.getElementById("markerleft").style.left = posxFromPtIndex(i1) + "px";
        document.getElementById("markerleft").style.display = "inline";
    }
    else {
        document.getElementById("markerleft").style.display = "none";
    }
    if((i1!=-1)&&(i2!=-1)) {
        document.getElementById("markerright").style.left = (posxFromPtIndex(i2) - 10)+ "px";
        document.getElementById("markerright").style.display = "inline";
        var hdist = (dists[i2]-dists[i1]);
        var vdist = (eles[i2]-eles[i1]);
        profile_infos += "<b>Selection</b><br/>Dist: "+Math.round(hdist)+"m<br/>Vert dst:"+Math.round(vdist)+"m";
        if(hdist>0) {
            var slope = vdist * 100.0 / hdist;
            profile_infos += "<br/>Slope:"+Math.round(slope)+"% "+Math.round(Math.atan(vdist/hdist)*180/Math.PI)+"&deg;";
        }
    }
    else {
        document.getElementById("markerright").style.display = "none";
    }
    if(i0!=-1) {
        document.getElementById("markerpt").style.left = posxFromPtIndex(i0) + "px";
        //document.getElementById("markerpt").style.left = "100px";
        document.getElementById("markerpt").style.display = "inline";
        curpt_infos += "<b>Current point</b><br/>Ele:"+eles[i0]+"m";
        if(i0<eles.length-1) {
            var hdist = (dists[i0+1]-dists[i0]);
            var vdist = (eles[i0+1]-eles[i0]);
            if(hdist>0) {
                var slope = vdist * 100.0 / hdist;
                curpt_infos += "<br/>Slope:"+Math.round(slope)+"% "+Math.round(Math.atan(vdist/hdist)*180/Math.PI)+"&deg;";
            }
        }
        //curpt_infos += i0;
    }
    else {
        document.getElementById("markerpt").style.display = "none";
    }
    document.getElementById("profile_infos").innerHTML = profile_infos;
    document.getElementById("profile_infos").style.display='inline';
    document.getElementById("curpt_infos").innerHTML = curpt_infos;
    document.getElementById("curpt_infos").style.display='inline';
}

function returnInt(element) {
  return parseInt(element,10);
}

function onChartMouseDown(e,o) {
	var ev = e || window.event;
    var posx = ev.clientX - findPosX(document.getElementById("chartimg"));
	if (ev.button==LEFT_BUTTON) {
        selxLeft = posx;
        refreshSelInfos();
    }
	else if (ev.button==RIGHT_BUTTON) {
        selxPt = posx;
        refreshSelInfos();
    }
}

function onChartMouseUp(e,o) {
	var ev = e || window.event;
	if (ev.button==LEFT_BUTTON) {
		var posx = ev.clientX - findPosX(document.getElementById("chartimg"));
        selxRight = posx;
        refreshSelInfos(1);
    }
}

/* Answer from profile computation */
function onComputeProfileAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            document.getElementById('compprofileloading').style.display='none';
            //document.getElementById('profile_title').innerHTML = '<b>Elevation in meters against distance in meters</b>';
            var res = this.responseText.split("\n");
            //document.getElementById('chartimg').src = res[0];
            //document.getElementById('chartimg').style.width="800px";
            //document.getElementById('chartimg').style.height="200px";
            eles = res[1].split(',');
            eles = eles.map(returnInt);
            dists = res[2].split(',');
            dists = dists.map(parseFloat);
            //marginsize = parseInt(res[3]);
            pt2px = res[4].split(',');
            pt2px = pt2px.map(returnInt);
            ptinput2px = res[5].split(',');
            ptinput2px = ptinput2px.map(returnInt);
            refreshGraphDetail();
        }
    }
}

/* Send points for profile computation */
function computeProfile(ptlisturl) {
    var client = new XMLHttpRequest();
    client.open('GET','/cgi-bin/computeprofile.py?ptlist='+ptlisturl+'&width=800&height=200');
    client.send();
    client.onreadystatechange = onComputeProfileAnswer;
    
    document.getElementById('compprofileloading').style.width="32px";
    document.getElementById('compprofileloading').style.height="32px";
    document.getElementById('compprofileloading').src = '/images/loading.svg'; 
    document.getElementById('compprofileloading').style.display="inline";
    //.innerHTML = '<img src="/images/loading.svg" width="32" height="32"/>';
}

/* When user wants to compute profile */
function onComputeProfileClick() {
    computeProfile(buildPtlistUrl(getLatLonList()));
}

/* Recompute point list string */
function getLatLonList() {
    var out = [];
    var i;
    for(i=0;i<points.length;i++) {
        out[i] = points[i].pt;
    }
    return out;
}


var zooms = {15: 4.777302*256, 16: 2.388657*256};
var x0s = {15: -20037508, 16: -20037508};
var y0s = {15: 20037508, 16: 20037508};

function wmstGetCaps() {
    
}

function latlon2tilerowcol(lat,lon,matrix) {
    //lat,lon -> Mercator
    var x = 111319.49079327357 * lon; // a*2*pi/360
    var y = 6378137.0 * Math.log(Math.tan((lat*0.0087266462599716) + Math.PI/4));
    return [(x-x0s[matrix]) / zooms[matrix] | 0, (y0s[matrix]-y) / zooms[matrix] | 0];
}

function getTilesBounds(matrix) {
    var i;
    var lat;var lon;
    var minlat,minlon,maxlat,maxlon;
    if(points.length<1) return null;
    minlat = points[0].pt.lat;
    maxlat = points[0].pt.lat;
    minlon = points[0].pt.lon;
    maxlon = points[0].pt.lon;
    for (i=1;i<points.length;i++) {
        lat = points[i].pt.lat;
        lon = points[i].pt.lon;
        if(lat<minlat)minlat = lat;
        if(lat>maxlat)maxlat = lat;
        if(lon<minlon)minlon = lon;
        if(lon>maxlon)maxlon = lon;
    }
    var t1 = latlon2tilerowcol(minlat,minlon,matrix);
    var t2 = latlon2tilerowcol(maxlat,maxlon,matrix);
    return [t1[0],t2[0],t2[1],t1[1]];
}

function getTiles(key,matrix,element) {
    var bounds = getTilesBounds(15);
    var row,col;
    var out=[];
    var img;
    element.style.height = ((bounds[3]-bounds[2]+1)*256)+"px";
    element.style.width = ((bounds[1]-bounds[0]+1)*256)+"px";
    for(row=bounds[2];row<=bounds[3];row++) {
        for(col=bounds[0];col<=bounds[1];col++) {
            var img = document.createElement("img");
            img.src = "http://wxs.ign.fr/"+key+"/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX="+matrix+"&TILEROW="+row+"&TILECOL="+col+"&FORMAT=image%2Fjpeg";
            img.style.left = ((col-bounds[0])*256)+"px";
            img.style.top = ((row-bounds[2])*256)+"px";
            img.style.width='256px';
            img.style.height='256px';
            img.setAttribute("alt",row+","+col);
            element.appendChild(img);
            out.push(img.style.left+"."+img.style.top+","+row+","+col+"\n");
            out.push("http://wxs.ign.fr/"+key+"/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX="+matrix+"&TILEROW="+row+"&TILECOL="+col+"&FORMAT=image%2Fjpeg");
        }
    }
    return out;
}

function onBuildMapClick() {
    var myWindow = window.open("","Printable map","width=200,height=100,menubar=yes");
    var e = myWindow.document.createElement("div");
    myWindow.document.body.appendChild(e);
    //document.getElementById('printmap').innerHTML='';
    tiles = getTiles("${GeoPortalApiKey}",15,e);
}

/*function addWptToGraph(pt) {
    console.log("addWptToGraph");
    profiledata.push([pt.dist,pt.ele]);
    $.plot($("#profilechart"), [profiledata], options);
}*/

function refreshGraph() {
    console.log("refreshGraph");
    profiledata = [];
    var i;
    for(i=0;i<points.length;i++) {
        profiledata.push([points[i].pt.dist,points[i].pt.ele]);
    }
    $.plot($("#profilechart"), [profiledata], options);
}

function refreshGraphDetail() {
    console.log("refreshGraphDetail");
    profiledata = [];
    var i;
    for(i=0;i<points.length;i++) {
        profiledata.push([points[i].pt.dist,points[i].pt.ele]);
    }
    profiledatadetail = [];
    var i;
    for(i=0;i<eles.length;i++) {
        profiledatadetail.push([dists[i],eles[i]]);
    }
    $.plot($("#profilechart"), [profiledata,profiledatadetail], options);
}

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
var profiledata=[];
$(function() {
    $.plot($("#profilechart"), [profiledata], options);
});

//]]>
</script>
<?php if ($map_type=='GMaps') { ?>
<script type="text/javascript" src="javascript/preparegmaps.js"></script>
<?php } else if ($map_type=='GeoPortal') { ?>
<script type="text/javascript" src="javascript/preparegeoportal2.js"></script>  
<?php } else if ($map_type=='MapQuest') { ?>
<script type="text/javascript" src="javascript/preparemapquest.js"></script>
<?php } ?>
