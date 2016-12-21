
/* 
********************
* Global variables *
********************

--------------
GoogleMaps objects:
--------------
map
map_track_points
selbegin_marker
selend_marker
map_marker
curtrackseg
buoy_marker (only if wind is true)

startendiconsizes
icon_start
icon_end
selbegin_icon
selend_icon
arrowiconsizes
arrowIcon
bounds

*/

/* Called when a map selection marker has been moved */
function onSelMarkerMove(evt) {
	// Get selection point ids
	var latlng = selbegin_marker.getPosition();
	var newpt1id = getCloserPointOfTrack(latlng.lat(),latlng.lng());
	latlng = selend_marker.getPosition();
	var newpt2id = getCloserPointOfTrack(latlng.lat(),latlng.lng());
	// Refresh selection info box
	refreshSelection(newpt1id,newpt2id);
	// Move markers on chart
	moveChartMarkerLeft(newpt1id,selchartid);
	moveChartMarkerRight(newpt2id,selchartid);
}

/* Recompute selection infos and move markers */
function refreshSelection(pt1_id, pt2_id) {
	if (typeof(selbegin_marker)!="undefined") {
        selbegin_marker.setMap(null);
	}
	if (typeof(selend_marker)!="undefined") {
        selend_marker.setMap(null);
	}
    refreshSelectionInfos(pt1_id,last_point_id,pt2_id);
	if ((pt1_id >= 0 && pt1_id < nbpts)&&(pt2_id >= 0 && pt2_id < nbpts)) {		
		// Move markers
        selbegin_marker = new google.maps.Marker({position: new google.maps.LatLng(track_points[pt1_id].lat, track_points[pt1_id].lon),map:map,icon:selbegin_icon,draggable:true});
        google.maps.event.addListener(selbegin_marker, "dragend", onSelMarkerMove);
        selend_marker = new google.maps.Marker({position: new google.maps.LatLng(track_points[pt2_id].lat, track_points[pt2_id].lon),map:map,icon:selend_icon,draggable:true});
        google.maps.event.addListener(selend_marker, "dragend", onSelMarkerMove);
		return true;
	}
	return false;
}

/* Recompute current point infos and move marker */
function refreshCurrentPoint(point_id) {
    
	var hasmoved = 0;
	
	if (typeof last_point_id == "undefined") {
		last_point_id = -1;
	}
	
	if (point_id != last_point_id) { 
		if (typeof center_map == "undefined") center_map=1;
		
		if (point_id >= 0 && point_id < nbpts) {
			last_point_id = point_id;
			hasmoved = 1;
			if (center_map) map.panTo(new google.maps.LatLng(track_points[point_id].lat, track_points[point_id].lon));
			if (typeof map_marker == "undefined") {
                map_marker = new google.maps.Marker({position: new google.maps.LatLng(track_points[point_id].lat, track_points[point_id].lon), map: map, icon: arrowIcon[track_points[point_id].arrow_id], draggable: false});
			}
			else {
                map_marker.setPosition(new google.maps.LatLng(track_points[point_id].lat, track_points[point_id].lon));
                map_marker.setIcon(arrowIcon[track_points[point_id].arrow_id]);
			}
            refreshCurrentPointInfos(point_id);
			moveChartMarkerCurrentPoint(point_id);
			refreshSnake(point_id);
			
			currentpointslider.setValue(point_id);
            
            refreshSelectionInfos(selfirstptid,point_id,sellastptid);
		}
		
		
	}
	return hasmoved;
}

/* Refresh snake on map givent the current point id */
function refreshSnake(cur_pt) {
	if (snakelength>0) {
		if (typeof curtrackseg != "undefined") {
            curtrackseg.setMap(null);
		}
		var minid = cur_pt-snakelength;
		if (minid<0) { minid = 0; }
		var maxid = parseInt(cur_pt)+parseInt(snakelength)*2;
		if (maxid>map_track_points.length-1) { maxid = map_track_points.length-1; }
		curtrackseg = new google.maps.Polyline(
            {
                path: map_track_points.slice(minid,maxid),
                geodesic: true,
                strokeColor: "#ff8000",
                strokeOpacity: 0.5,
                strokeWeight: 4
            });
        curtrackseg.setMap(map);
	}
}

/* If possible change the map type to get one with a max zoom higer than needed_zoom */
function switchToMapTypeWithHigherResolution(needed_zoom) {
    var map_types = map.mapTypes;
    for(i in map_types) {
        if (map_types[i].maxZoom>needed_zoom) {
            map.setMapTypeId(i);
            return;
        }
    }
}

/* Add buoy marker */
function addBuoyMarker() {
    if (typeof buoy_marker=='undefined') {
        var buoy_icon = "/static/images/MarkerBuoy.png";
        buoy_marker = new google.maps.Marker({position:map.getCenter(),icon: buoy_icon, draggable: true, map:map});
        google.maps.event.addListener(buoy_marker, "dragend", onBuoyMarkerMove);
    }
}

/* buoy marker move event */
function onBuoyMarkerMove() {
    var latlng = buoy_marker.getPosition();
    refreshBuoyMarker(latlng.lat(),latlng.lng());
}

/* Remove buoy marker */
function removeBuoyMarker() {
    buoy_marker.setMap(null);
}

/* Event called when user scroll on map with the mouse */
function onMapMouseWheel(e) {
    var evt=window.event || e;
    var delta=evt.detail? evt.detail*(-120) : evt.wheelDelta;
    var current_zoom = map.getZoom();
    var max_zoom = map.mapTypes.get(map.getMapTypeId()).maxZoom;
    if ((delta>0) && (current_zoom==max_zoom)) {
        switchToMapTypeWithHigherResolution(current_zoom);
    }
    return true;
}

function redrawTrack() {
	map_track_points = [];
	var i;
	for(i=0;i<track_points.length;i++) {
		map_track_points[i] = new google.maps.LatLng(track_points[i].lat,track_points[i].lon);
	}
    track_overlay.setMap(null);
    track_overlay = new google.maps.Polyline(
        {
            path: map_track_points,
            geodesic: true,
            strokeColor: "#bb8000",
            strokeOpacity: 0.5,
            strokeWeight: 4
        });
    track_overlay.setMap(map);
}

/* Attach the event onMapMouseWheel() to 'map' */
if (document.getElementById("map").attachEvent) //if IE (and Opera depending on user setting)
    document.getElementById("map").attachEvent("on"+MOUSEWHEEL_EVT, onMapMouseWheel)
else if (document.addEventListener) //WC3 browsers
    document.addEventListener(MOUSEWHEEL_EVT, onMapMouseWheel, false)

// Create start/current/end icons
var icon_start = {url: "/static/images/MarkerStart.png", size: {width: 12, height: 20}, anchor: {x: 6, y: 20}};
var icon_end = {url: "/static/images/MarkerEnd.png", size: {width: 12, height: 20}, anchor: {x: 6, y: 20}};
var selbegin_icon = "/static/images/MarkerSelBegin.png";
var selend_icon = "/static/images/MarkerSelEnd.png";

// Create arrow icons
var arrowIcon = [];
for (var angle=0;angle<360;angle += 15) {
	arrowIcon.push(
        {
            url:"/static/images/Arrow" + angle + ".png",
            anchor: {x: 8, y: 8 },
            size: {width: 15, height: 15}
        });
}

// Track points
var map_track_points = [];
var i;
for(i=0;i<track_points.length;i++) {
	map_track_points[i] = new google.maps.LatLng(track_points[i].lat,track_points[i].lon);
}

// bounds
var bounds = new google.maps.LatLngBounds(map_track_points[0],map_track_points[0]);
for(i=0;i<map_track_points.length;i++) {
    bounds.extend(map_track_points[i]);
}


// Create map
// Center map
// Set map parameters
var mapOptions = {
  zoom: 12,
  center: bounds.getCenter(),
  mapTypeId: google.maps.MapTypeId.TERRAIN
};

var map = new google.maps.Map(document.getElementById("map"),mapOptions);


// Draw track
// Start point
var start_point_marker = new google.maps.Marker({position: new google.maps.LatLng(track_points[0].lat,track_points[0].lon), map: map, icon: icon_start, draggable: false});

// End point
var end_point_marker = new google.maps.Marker({position: new google.maps.LatLng(track_points[track_points.length-1].lat,track_points[track_points.length-1].lon), map: map, icon: icon_end, draggable: false});
var track_overlay = new google.maps.Polyline(
        {
            path: map_track_points,
            geodesic: true,
            strokeColor: "#bb8000",
            strokeOpacity: 0.5,
            strokeWeight: 4
        });
track_overlay.setMap(map);

// bounds
map.fitBounds(bounds);

// Click on map handling
google.maps.event.addListener(map,"click",function(evt) {
    refreshCurrentPoint(getCloserPointOfTrack(evt.latLng.lat(),evt.latLng.lng()));
	focusToMap();    
});


snakelengthslider.onchange = function () {
	snakelength = snakelengthslider.getValue();
	refreshSnake(last_point_id);
	if (snakelength==0) {
		// remove track if no snake
		if (typeof curtrackseg != "undefined") {
            curtrackseg.setMap(null);
		}
	}
}

refreshCurrentPoint(0);
