
function changePreview(mapid,lat,lon,desc) {
	showOnMap(mapid,lat,lon,desc);
	showPreview(mapid);
}	

var prevrow = null;
var prevcolor = null;
var prevborder = null;

function showPreview(mapid) {
	document.images['preview'].src = '/thumbnail/'+mapid;
	document.getElementById("preview").style.visibility = 'visible';
	if(prevrow!=null) {
		prevrow.style.backgroundColor = prevcolor;
		prevrow.style.border = prevborder;
	}
	prevcolor = document.getElementById("row"+mapid).style.backgroundColor;
	prevborder = document.getElementById("row"+mapid).style.border;
	prevrow = document.getElementById("row"+mapid);
	document.getElementById("row"+mapid).style.backgroundColor = "#A7C942";
	document.getElementById("row"+mapid).style.border ='1px solid ';
}

var markers=new Array();

var marker_icon_size = new GIcon();
marker_icon_size.iconSize = new GSize(12, 20);
marker_icon_size.shadowSize = new GSize(22, 20);
marker_icon_size.iconAnchor = new GPoint(6, 20);
marker_icon_size.infoWindowAnchor = new GPoint(5, 1);
var marker_icon = new GIcon(marker_icon_size, "/static/images/MarkerSelEnd.png", null, "/static/images/MarkerShade.png");

// Create map
var map = new GMap2(document.getElementById("map_of_maps"));
map.addMapType(G_PHYSICAL_MAP);
map.setMapType(G_PHYSICAL_MAP);
map.enableScrollWheelZoom();

map.setCenter(new GLatLng(45.0,0.0));
map.setZoom(5);

// create a clickable marker
function createMarker(mapid,latlon,text) {
	var marker = new GMarker(latlon, {icon: marker_icon});
	//marker.openInfoWindowHtml(text);
	GEvent.addListener(marker, "click", function(){
		showPreview(mapid);
		map.setCenter(latlon);
	});
	return marker;
}

function showOnMap(mapid,lat,lon,desc) {
	var latlon = new GLatLng(lat,lon);
	if(typeof markers[mapid]=='undefined') {
		markers[mapid] = createMarker(mapid,latlon,desc);
		map.addOverlay(markers[mapid]);
	}
	map.setCenter(latlon);
}
