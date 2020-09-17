
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

/*
		// create line and markers styles
		start_icon = {externalGraphic:'/static/images/MarkerStart.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};
		end_icon = {externalGraphic:'/static/images/MarkerEnd.png',  graphicWidth:12, graphicHeight:20, graphicXOffset:-6, graphicYOffset:-20};
		
		trackseg_style = {
			strokeColor: "#aaaaaa",
			strokeWidth: 5,
			strokeOpacity: 0.5,
			strokeDashstyle: "solid"
		};
		
		drag = new OpenLayers.Control.DragFeature(selmarkers_layer, {onComplete: onMarkerDrag});
		VISU.getMap().addControl(drag);
		drag.activate();
*/

/* Recompute selection infos and move markers */
function refreshSelection(pt1_id, pt2_id) {
  console.log("refreshSelection %o %o",pt1_id,pt2_id);
  if(pt1_id >= 0 && pt1_id < nbpts && pt2_id >= 0 && pt2_id < nbpts) {
    sel_layer.setVisible(true);
    selbegin_feature.setGeometry(new ol.geom.Point(map_track_points[pt1_id]));
    selend_feature.setGeometry(new ol.geom.Point(map_track_points[pt2_id]));
  } else {
    sel_layer.setVisible(false);
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
                                  map.getView().setCenter(map_track_points[point_id]);
			}
			
                        //refreshSnake(point_id);
                        curpt_feature.setGeometry(new ol.geom.Point(map_track_points[point_id]));
                        curpt_feature.setStyle(arrow_icons[track_points[point_id].arrow_id]); 
			
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

console.log('geoportal ol');

var map_track_points = [];
var i;
for (i=0;i<track_points.length;i++) map_track_points[i]=ol.proj.fromLonLat([track_points[i].lon,track_points[i].lat]);

var bounds = new ol.extent.boundingExtent(map_track_points);

var track = new ol.geom.LineString(map_track_points);
var track_feature = new ol.Feature({
              geometry: track,
              name: 'Track'
          });


var arrow_icons = [];
for (var angle=0;angle<360;angle += 15) {
  arrow_icons.push(new ol.style.Style({image:new ol.style.Icon({src:'/static/images/Arrow' + angle + '.png'})}));
}

var curpt_feature = new ol.Feature({
        geometry: new ol.geom.Point(map_track_points[0]),
        name:'Current point'
      });

var curpt_layer = new ol.layer.Vector({
  source:new ol.source.Vector(
    {features:[
      curpt_feature
    ]}
  ),
  style:arrow_icons[track_points[0].arrow_id]
 });

var track_layer = new ol.layer.Vector({
    source:new ol.source.Vector({features:[track_feature]}),
    style:new ol.style.Style({stroke:new ol.style.Stroke({color: "#FFBB00",
                        width: 2
                        })}),
    opacity:0.7
  });

var selbegin_feature = new ol.Feature();
var selend_feature = new ol.Feature();
var sel_layer = new ol.layer.Vector({
  source:new ol.source.Vector({features:[selbegin_feature,selend_feature]}),
  style:new ol.style.Style({image:new ol.style.Icon({src:'/static/images/MarkerSelBegin.png'})})
});

var map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM()
      }),
      track_layer,
      sel_layer,
      curpt_layer
    ],
    view: new ol.View({
      center: map_track_points[0],
      zoom: 4
    })
  });

map.getView().fit(bounds);

map.addEventListener("click",function(e){
  var lonlat = ol.proj.toLonLat(e.coordinate);
  console.log(lonlat);
  refreshCurrentPoint(getCloserPointOfTrack(lonlat[1],lonlat[0]));
});

