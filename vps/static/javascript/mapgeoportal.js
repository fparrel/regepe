
/*
********************
* Global variables *
********************
------------------
GeoPortal objects:
------------------
VISU
selbegin_icon
selend_icon
arrow_icons
trackseg_style
curpt_layer
curpt_vector
hasmoved
curtrackseg

*/

function onMarkerDrag(e) {
   var pos = e.geometry;
    if (pos) {
        pos.transform(VISU.getMap().getProjection(), OpenLayers.Projection.CRS84); // GeoPortail -> WGS84
        var ptid = getCloserPointOfTrack(pos.y,pos.x);
        pos.transform(OpenLayers.Projection.CRS84,VISU.getMap().getProjection());
        if(e==selbegin_vector) {
        	// Refresh selection info box
            refreshSelection(ptid,sellastptid);
            // Move markers on chart
            moveChartMarkerLeft(ptid,selchartid);
        }
        else {
        	// Refresh selection info box
            refreshSelection(selfirstptid,ptid);
            // Move markers on chart
            moveChartMarkerRight(ptid,selchartid);
        }
    }
}

var map_track_points;
var track_layer;
var start_feature;
var end_feature;
var track_feature;

function redrawTrack() {
	map_track_points = [];
	var bounds = new OpenLayers.Bounds();
        var i;
	for(i=0;i<track_points.length;i++) {
		var pt = new OpenLayers.Geometry.Point(track_points[i].lon,track_points[i].lat);
		pt = pt.transform(OpenLayers.Projection.CRS84, VISU.getMap().getProjection());
		map_track_points[i] = pt;
		bounds.extend(pt);
	}
	if(typeof(start_feature)!='undefined')
		track_layer.removeFeatures([start_feature,end_feature,track_feature]);
	start_feature = new OpenLayers.Feature.Vector(map_track_points[0],null,start_icon);
	end_feature = new OpenLayers.Feature.Vector(map_track_points[map_track_points.length-1],null,end_icon);
	track_feature = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(map_track_points),null,track_style);
	track_layer.addFeatures([track_feature]);
	return bounds;
}

/* Called by geoportal api to init the map */
function initGeoportalMap() {
    
    // Load gp visualisation box for france
    VISU = iv.getViewer();
	//geoportalLoadVISU("GeoportalVisuDiv", "normal", "FXX");
	if (VISU.getMap().allowedGeoportalLayers) {

		// Add bg layer: IGN MAP
		//VISU.addGeoportalLayer('GEOGRAPHICALGRIDSYSTEMS.MAPS:WMSC',{visibility: true,opacity: 0.8});
        // now added by loader at init time

		// Set controls
        /*
		VISU.openLayersPanel(false);
		VISU.setLayersPanelVisibility(true);
		VISU.openToolsPanel(false);
        VISU.setInformationPanelVisibility(false);
        */
        //needed for good computation of bounds
        //VISU.getMap().setCenterAtLonLat(track_points[0].lon,track_points[0].lat, 5);


		// create line and markers styles
		start_icon = {externalGraphic:'/static/images/MarkerStart.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};
		end_icon = {externalGraphic:'/static/images/MarkerEnd.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};
		selbegin_icon = {externalGraphic:'/static/images/MarkerSelBegin.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};
		selend_icon = {externalGraphic:'/static/images/MarkerSelEnd.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};		
		arrow_icons = [];
		for (var angle=0;angle<360;angle += 15) {
			arrow_icons.push({externalGraphic:'/static/images/Arrow' + angle + '.png',  graphicWidth:15, graphicHeight:15, graphicXOffset:-8, graphicYOffset:-8});
		}
		
		track_style = {
			strokeColor: "#FFBB00",
			strokeWidth: 5,
			strokeOpacity: 1.0,
			strokeDashstyle: "solid"
		};
		
		trackseg_style = {
			strokeColor: "#aaaaaa",
			strokeWidth: 5,
			strokeOpacity: 0.5,
			strokeDashstyle: "solid"
		};
		
		track_layer = new OpenLayers.Layer.Vector(TRACK);
		var bounds = redrawTrack();
		
		VISU.getMap().addLayer(track_layer);
		
		
		// current point layer
		curpt_layer = new OpenLayers.Layer.Vector(CURRENT);
		curpt_vector = new OpenLayers.Feature.Vector(map_track_points[0].clone(),null,
		arrow_icons[track_points[0].arrow_id]);
		curpt_layer.addFeatures([curpt_vector]);
		VISU.getMap().addLayer(curpt_layer);
		
		// selection markers layer
		selmarkers_layer = new OpenLayers.Layer.Vector(SELECTION);
		VISU.getMap().addLayer(selmarkers_layer);
		drag = new OpenLayers.Control.DragFeature(selmarkers_layer, {onComplete: onMarkerDrag});
		VISU.getMap().addControl(drag);
		drag.activate();
		
		// add listener on click on Map event
		VISU.getMap().events.register("click",
			VISU.getMap(), function(e) {
				var pos = VISU.getMap().getLonLatFromViewPortPx(e.xy);
				if (pos) {
					pos.transform(VISU.projection, OpenLayers.Projection.CRS84); // GeoPortail -> WGS84
					refreshCurrentPoint(getCloserPointOfTrack(pos.lat,pos.lon));
				}
				focusToMap();
			}
		);
        
		// set center and zoom
		VISU.getMap().setCenter(bounds.getCenterLonLat(),VISU.getMap().getZoomForExtent(bounds),true,true);
        
		//force redraw
		iv.zoomIn();
		iv.zoomOut();
	}
}

/* Recompute selection infos and move markers */
function refreshSelection(pt1_id, pt2_id) {
	if ((typeof(selbegin_vector)!="undefined")&&(typeof(selend_vector)!="undefined")) {
		selmarkers_layer.removeAllFeatures();
		//selmarkers_layer.removeFeatures([selbegin_vector,selend_vector]);
	}
    if(pt1_id >= 0 && pt1_id < nbpts && pt2_id >= 0 && pt2_id < nbpts) {
        selbegin_vector = new OpenLayers.Feature.Vector(map_track_points[pt1_id].clone(),null,
            selbegin_icon);
        selend_vector = new OpenLayers.Feature.Vector(map_track_points[pt2_id].clone(),null,
            selend_icon);
        selmarkers_layer.addFeatures([selbegin_vector,selend_vector]);
    }
    refreshSelectionInfos(pt1_id, last_point_id, pt2_id);
	return false;
}

/* Recompute current point infos and move marker */
function refreshCurrentPoint(point_id) {
	
	hasmoved = 0;
	
	if (typeof last_point_id == "undefined") {
		last_point_id = -1;
	}
	
	if (point_id != last_point_id) { 
		if (typeof center_map == "undefined") center_map=1;
		
		if (point_id >= 0 && point_id < nbpts && typeof map_track_points!='undefined') {
			last_point_id = point_id;
			hasmoved = 1;
			if (center_map) {
				var lonlat = new OpenLayers.LonLat(map_track_points[point_id].x,map_track_points[point_id].y);
				VISU.getMap().updateSize();
				VISU.getMap().setCenter(lonlat);
			}
			
            refreshSnake(point_id);
            
			curpt_layer.removeFeatures([curpt_vector]);
			curpt_vector = new OpenLayers.Feature.Vector(map_track_points[point_id].clone(),null,
				arrow_icons[track_points[point_id].arrow_id]);
			curpt_layer.addFeatures([curpt_vector]);
			
            refreshCurrentPointInfos(point_id);
			moveChartMarkerCurrentPoint(point_id);
			
			currentpointslider.setValue(point_id);
		}
		
		
	}
	return hasmoved;
}

/* Refresh snake on map givent the current point id */
function refreshSnake(cur_pt) {
	if (snakelength>0) {
		if (typeof curtrackseg != "undefined") {
			curpt_layer.removeFeatures([curtrackseg]);
		}
		var minid = cur_pt-snakelength;
		if (minid<0) { minid = 0; }
		var maxid = parseInt(cur_pt)+parseInt(snakelength)*2;
		if (maxid>map_track_points.length-1) { maxid = map_track_points.length-1; }
		curtrackseg = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(map_track_points.slice(minid,maxid)), null, trackseg_style);
		curpt_layer.addFeatures([curtrackseg]);
	}
}

function onMoveSelBeginMarker() {
	var ptid = getCloserPointOfTrack(selbegin_marker.getLatLng().lat(),selbegin_marker.getLatLng().lng());
	/* ... */
}

function onMoveSelEndMarker() {
	var ptid = getCloserPointOfTrack(selend_marker.getLatLng().lat(),selend_marker.getLatLng().lng());	
	/* ... */
}

snakelengthslider.onchange = function () {
	snakelength = snakelengthslider.getValue();
	refreshSnake(last_point_id);
	if (snakelength==0) {
		// remove track if no snake
		if (typeof curtrackseg != "undefined") {
			curpt_layer.removeFeatures([curtrackseg]);
		}
	}
}

refreshCurrentPoint(0);

var VISU=null;

console.log("GeoPortalApiKey="+GeoPortalApiKey);

var iv = Geoportal.load('map',
                [GeoPortalApiKey],
                {// map's center :
                // longitude:
                lon:track_points[0].lon,
                // latitude:
                lat:track_points[0].lat
                },
                null,
                {
                   //OPTIONS
                   onView : initGeoportalMap,
                    language:LANG,
                    viewerClass:'Geoportal.Viewer.Default',
                    overlays:{}, //remove blue pin
                    layers:['ORTHOIMAGERY.ORTHOPHOTOS','GEOGRAPHICALGRIDSYSTEMS.MAPS'],
                    layersOptions:{
                        'ORTHOIMAGERY.ORTHOPHOTOS':{ visibility:false, opacity:1.0 }, //aerial photo: hidden by default
                        'GEOGRAPHICALGRIDSYSTEMS.MAPS':{ visibility:true, opacity:0.85 } //IGN map: visible with high opacity
                    }
                }
    );
