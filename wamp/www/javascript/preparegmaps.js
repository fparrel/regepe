
/* redraw track polyline from contents of points */
function redrawLine() {
    if (typeof line != "undefined") {
        line.setMap(null);
    }
    if(noline)return;
    line = new google.maps.Polyline(
        {
            path: points,
            geodesic: true,
            strokeColor: "#bb8000",
            strokeOpacity: 1.0,
            strokeWeight: 4
        });
    line.setMap(map);
}

/* remove all markers */
function removeMarkers() {
    var i;
    for(i=0;i<markers.length;i++) {
        markers[i].setMap(null);
    }
    markers = [];
}

function removeMarker(index) {
    markers[index].setMap(null);
}

function selectWptOnMap(index) {
    if(sel_index!=-1) {
        markers[sel_index].setIcon(pt_icon);
    }
    markers[index].setIcon(sel_icon);
    sel_index = index;
}

/* Add a given point object to the map */
function addPoint(newpt,index) {
    points[index] = new google.maps.LatLng(newpt.lat,newpt.lon);
    points[index].pt = newpt;
    var pt_marker;
    pt_marker = new google.maps.Marker({position: new google.maps.LatLng(newpt.lat, newpt.lon), map: map, icon: pt_icon, draggable: true});
    markers.push(pt_marker);
    pt_marker.pt_index = index;
    google.maps.event.addListener(pt_marker, "dragend", function(evt) {
        var pt = points[pt_marker.pt_index].pt;
        points[pt_marker.pt_index] = evt.latLng;
        points[pt_marker.pt_index].pt = pt;
        points[pt_marker.pt_index].pt.lat = evt.latLng.lat();
        points[pt_marker.pt_index].pt.lon = evt.latLng.lng();
        redrawLine();
        refreshLength();
        refreshUrls();
        askElevation(points[pt_marker.pt_index].pt);
    });
    google.maps.event.addListener(pt_marker, "click", function(evt) {
        if(sel_index!=-1) {
            markers[sel_index].setIcon(pt_icon);
        }
        pt_marker.setIcon(sel_icon);
        sel_index = pt_marker.pt_index;
        selectWpt(sel_index);
    });
    addWpt(points[index].pt,index);
}

/* Click on map event */
function onMapClick(lat,lon) {
    addPoint(new Point(lat,lon),points.length);
    if (points.length>0) {
        redrawLine();
        refreshLength();
        refreshUrls();
    }
}

// Create icons
var sel_icon = "../images/MarkerStart.png";//new GIcon(iconsizes, "../images/MarkerStart.png", null, "../images/MarkerShade.png");
var pt_icon = "../images/MarkerSelBegin.png";//new GIcon(iconsizes, "../images/MarkerSelBegin.png", null, "../images/MarkerShade.png");

// Create map
var mapOptions = {
  zoom: 5,
  center: new google.maps.LatLng(45.0,0.0),
  mapTypeId: google.maps.MapTypeId.TERRAIN
};

var map = new google.maps.Map(document.getElementById("map"),mapOptions);

// Click on map handling
google.maps.event.addListener(map,"click",function(evt) {
    onMapClick(evt.latLng.lat(),evt.latLng.lng());
});

// add points from URL
if (pts_from_url.length>0) {
    var i;
    var bounds = new google.maps.LatLngBounds(new google.maps.LatLng(pts_from_url[0].lat,pts_from_url[0].lon),new google.maps.LatLng(pts_from_url[0].lat,pts_from_url[0].lon));
    for(i=0;i<pts_from_url.length;i++) {
        addPoint(pts_from_url[i],i);
        bounds.extend(new google.maps.LatLng(pts_from_url[i].lat,pts_from_url[i].lon));
    }
    map.fitBounds(bounds);
    redrawLine();
    refreshLength();
    refreshUrls();
}
