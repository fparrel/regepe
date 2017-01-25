
/* remove all markers */
function removeMarkers() {
    markers_layer.removeFeatures(markers);
    markers = [];
}

function removeMarker(index) {
    markers_layer.removeFeatures(markers[index]);
}

/* redraw track polyline from contents of points */
function redrawLine() {
    if (typeof line != "undefined") {
        track_layer.removeFeatures(line);
    }
    if(noline)return;
    line = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(points),null,track_style);
    track_layer.addFeatures([line]);
}

/* Add a given point object to the map */
function addPoint(newpt,index) {
    var pt = new OpenLayers.Geometry.Point(newpt.lon,newpt.lat);
    // WGS84 -> GeoPortal projection conversion
    pt = pt.transform(OpenLayers.Projection.CRS84, VISU.getMap().getProjection());
    points[index] = pt;
    points[index].pt = newpt;
    var pt_marker;
    pt_marker = new OpenLayers.Feature.Vector(pt,null,pt_icon);
    markers_layer.addFeatures([pt_marker]);
    markers.push(pt_marker);
    pt_marker.pt_index = index;
    addWpt(points[index].pt,index);
}

/* Click on map event */
function onMapClick(lat,lon) {
    if(points.length>0) {
        addPoint(new Point(lat,lon,points[points.length-1].pt),points.length);
    }
    else {
        addPoint(new Point(lat,lon),points.length);
    }
    if (points.length>0) {
        redrawLine();
        refreshLength();
        refreshUrls();
    }
}

/* When marker is dragged */
function onMarkerDrag(e) {
    if (e.geometry) {
        var pos = e.geometry.clone();
        pos.transform(VISU.getMap().getProjection(), OpenLayers.Projection.CRS84); // GeoPortail -> WGS84
        var pt = points[e.pt_index].pt;
        points[e.pt_index] = e.geometry;
        points[e.pt_index].pt = pt;
        points[e.pt_index].pt.lat = pos.y;
        points[e.pt_index].pt.lon = pos.x;
        askElevation(points[e.pt_index].pt);
        redrawLine();
        refreshLength();
        refreshUrls();
        refreshGraph();
    }
}

function selectWptOnMap(index) {
    if(sel_index!=-1) {
        markers[sel_index].style = pt_icon;
    }
    markers[index].style = sel_icon;
    sel_index = index;
    markers_layer.redraw();
}

function onMarkerSelect(pt_marker) {
    if(sel_index!=-1) {
        markers[sel_index].style = pt_icon;
    }
    pt_marker.style = sel_icon;
    markers_layer.redraw();
    sel_index = pt_marker.pt_index;
    selectWpt(sel_index);
}

function addPointsFromUrl() {
    if (pts_from_url.length>0) {
        var rect = new OpenLayers.Bounds();
        var i;
        for(i=0;i<pts_from_url.length;i++) {
            addPoint(pts_from_url[i],i);
            rect.extend(new OpenLayers.LonLat(pts_from_url[i].lon,pts_from_url[i].lat));
        }
        VISU.getMap().zoomToExtent(rect.transform(OpenLayers.Projection.CRS84, VISU.getMap().getProjection()), false);
        redrawLine();
        refreshLength();
        refreshUrls();
        refreshGraph();
    }
}

/* Called by geoportal api to init the map */
function initGeoportalMap() {
    
    // Load gp visualisation box for france
    VISU = iv.getViewer();
	//geoportalLoadVISU("GeoportalVisuDiv", "normal", "FXX");
	if (VISU.getMap().allowedGeoportalLayers) {
		
		// Add bg layer: IGN MAP
		VISU.addGeoportalLayer('GEOGRAPHICALGRIDSYSTEMS.MAPS:WMSC',{visibility: true,opacity: 0.8});
		
		
		// create line and markers styles
		sel_icon = {externalGraphic:'/static/images/MarkerStart.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};
		pt_icon = {externalGraphic:'/static/images/MarkerSelBegin.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};
		
		track_style = {
			strokeColor: "#ff0000",
			strokeWidth: 3,
			strokeOpacity: 0.5,
			strokeDashstyle: "solid"
		};
		
		track_layer = new OpenLayers.Layer.Vector(TRACK);
		
		VISU.getMap().addLayer(track_layer);
        
		markers_layer = new OpenLayers.Layer.Vector(MARKS);
		VISU.getMap().addLayer(markers_layer);
		drag = new OpenLayers.Control.DragFeature(markers_layer, {onComplete: onMarkerDrag, onStart: onMarkerSelect});
		VISU.getMap().addControl(drag);
		drag.activate();
		
		// add listener on click on Map event
		VISU.getMap().events.register("click",
			VISU.getMap(), function(e) {
				var pos = VISU.getMap().getLonLatFromViewPortPx(e.xy);
				if (pos) {
					pos.transform(VISU.projection, OpenLayers.Projection.CRS84); // GeoPortail -> WGS84
					onMapClick(pos.lat,pos.lon);
				}
				//focusToMap();
			}
		);
            
        addPointsFromUrl();
        
		//force redraw
		iv.zoomIn();
		iv.zoomOut();
	}
}

var iv = Geoportal.load('map',
                [GeoPortalApiKey],
                {// map's center :
                // longitude:
                lon:0.0,
                // latitude:
                lat:45.0
                },
                null,
                {
                   //OPTIONS
                   onView : initGeoportalMap,
                    language:LANG,
                    viewerClass:'Geoportal.Viewer.Default',
                    overlays:{} //remove blue pin
                }
    );

/* Manage map resize */
var oldmapw = document.getElementById('mapresizer').clientWidth;
var oldmaph = document.getElementById('mapresizer').clientHeight;

function onWindowMouseUp() {
    var w = document.getElementById('mapresizer').clientWidth;
    var h = document.getElementById('mapresizer').clientHeight;
    if((w!=oldmapw)||(h!=oldmaph)) {
        oldmapw = w;
        oldmaph = h;
        onResizeMap();
    }
    return true;
}

window.onmouseup= onWindowMouseUp;

function onResizeMap() {
    document.getElementById('map').style.width=(document.getElementById('mapresizer').clientWidth-20)+'px';
    document.getElementById('map').style.height=(document.getElementById('mapresizer').clientHeight-20)+'px';
    var w = document.getElementById('map').clientWidth;
    var h = document.getElementById('map').clientHeight;
    VISU.setSize(w,h);
    VISU.getMap().render(document.getElementById('map'));
}
