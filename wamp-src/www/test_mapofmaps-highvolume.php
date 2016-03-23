<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><title>Map of maps</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<link type="text/css" rel="StyleSheet" href="styles/inputform.css" />
</head>
<body>
<?php include('header.html'); ?>
<div id="body">
<h1>Map of maps</h1>
<div id="map_of_maps" style="height:500px;width:500px;"></div>
</div>
</body>
</html>
<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAA-SFgG1PQ0XMpzJtYw64TYBSxKPePYn95QAlgX1lqeZIVHDkIpRSbAUoIeWaVER-Ii5aXAs-5dM_1fw" type="text/javascript"></script>
<script src="javascript/xmlhttprequest.js" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[

// create a clickable marker
function createMarker(pt, text) {
	var marker = new GMarker(pt, {icon: marker_icon});
	GEvent.addListener(marker, "click", function(){
		marker.openInfoWindowHtml(text);
	});
	return marker;
}

function onReadystatechange() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            var maps = this.responseXML.getElementsByTagName("maps");
            for (i=0;i<maps.length;i++) {
                var lat = maps[i].getAttribute('lat');
                var lon = maps[i].getAttribute('lon');
                if ((typeof(markers[lat+','+lon])=="undefined")||(markers[lat+','+lon]=="undefined")) {
                    var mapslist = maps[i].getElementsByTagName("map");
                    var mytext = '';
                    for (j=0;j<mapslist.length;j++) {
                        var mapid = mapslist[j].getAttribute('mapid');
                        var mapdesc = mapslist[j].childNodes[0].nodeValue;
                        mytext = mytext + mapdesc + '<A HREF="/showmap.php?mapid=' + mapid + '">Go</A><BR/>';
                    }
                    var marker = createMarker(new GLatLng(lat,lon),mytext);
                    markers[lat+','+lon] = marker;
                    map.addOverlay(marker);
                }
            }
        }
    }
}

function onMapMove() {
    var bounds = map.getBounds();
    var minlat = Number(bounds.getSouthWest().lat()).toFixed(4);
    var maxlat = Number(bounds.getNorthEast().lat()).toFixed(4);
    var maxlon = Number(bounds.getNorthEast().lng()).toFixed(4);
    var minlon = Number(bounds.getSouthWest().lng()).toFixed(4);
    var query_str = "/cgi-bin/getmaplist.py?minlat="+minlat+"&maxlat="+maxlat+"&minlon="+minlon+"&maxlon="+maxlon;
    var client = new XMLHttpRequest();
    client.open('GET',query_str);
    client.send();
    client.onreadystatechange = onReadystatechange;
    for (key in markers) {
        var latlon = key.split(',');
        if (!(bounds.containsLatLng(new GLatLng(latlon[0],latlon[1])))) {
            map.removeOverlay(markers[key]);
            markers[key] = "undefined";
        }
    }    
}

// Create map
var map = new GMap2(document.getElementById("map_of_maps"));
map.addMapType(G_PHYSICAL_MAP);
map.setMapType(G_PHYSICAL_MAP);
map.enableScrollWheelZoom();

map.setCenter(new GLatLng(45.0,0.0));
map.setZoom(5);

var marker_icon_size = new GIcon();
marker_icon_size.iconSize = new GSize(12, 20);
marker_icon_size.shadowSize = new GSize(22, 20);
marker_icon_size.iconAnchor = new GPoint(6, 20);
marker_icon_size.infoWindowAnchor = new GPoint(5, 1);
var marker_icon = new GIcon(marker_icon_size, "/images/MarkerSelEnd.png", null, "/images/MarkerShade.png");

var markers = new Array();

GEvent.addListener(map, "moveend", onMapMove);

onMapMove();

//]]>
</script>
