
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

var markers = new Array();

var marker_icon = {url: "/static/images/MarkerSelEnd.png", size: {width: 12, height: 20}, anchor: {x: 6, y: 20}};

// Create map
var mapOptions = {
  zoom: 5,
  center: new google.maps.LatLng(45.0,0.0),
  mapTypeId: google.maps.MapTypeId.TERRAIN
};
var map = new google.maps.Map(document.getElementById("map_of_maps"),mapOptions);


// create a clickable marker
function createMarker(mapid,latlon,text) {
  var marker = new google.maps.Marker({position:latlon, icon: marker_icon, draggable: false, map:map});
  google.maps.event.addListener(marker, "click", function(){
      showPreview(mapid);
      map.setCenter(latlon);
    });
  return marker;
}

function showOnMap(mapid,lat,lon,desc) {
  var latlon = new google.maps.LatLng(lat,lon);
  if(typeof markers[mapid]=='undefined') {
    markers[mapid] = createMarker(mapid,latlon,desc);
  }
  map.setCenter(latlon);
}

