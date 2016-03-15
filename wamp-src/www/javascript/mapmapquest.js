
/* 
********************
* Global variables *
********************

--------------
GMaps objects:
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

var markericonoffset = {x:-6,y:-20};

/* Called when a map selection marker has been moved */
function onSelMarkerMove( ) {
    //TODO
}

function onDragSelPoi() {
	//stick point to track
	var ptid = getCloserPointOfTrack(this.getLatLng().lat,this.getLatLng().lng);
	this.ptid = ptid;
	this.setLatLng({lat:track_points[ptid].lat,lng:track_points[ptid].lon});
	//refresh infos
	refreshSelectionInfos(firstpt.ptid,last_point_id,secondpt.ptid);
	// Move markers on chart
	if(this==firstpt)
		moveChartMarkerLeft(ptid,selchartid);
	else if(this==secondpt)
		moveChartMarkerRight(ptid,selchartid);		
}

/* Recompute selection infos and move markers */
function refreshSelection(pt1_id, pt2_id) {
    if (typeof firstpt != "undefined") {
        map.removeShape(firstpt);
    }
    if (typeof secondpt != "undefined") {
        map.removeShape(secondpt);
    }
    refreshSelectionInfos(pt1_id,last_point_id,pt2_id);
    if((pt1_id>-1)&&(pt2_id>-1)) {
        firstpt=new MQA.Poi( {lat:track_points[pt1_id].lat, lng:track_points[pt1_id].lon} );
	firstpt.ptid = pt1_id;
	firstpt.draggable = 1;
	MQA.EventManager.addListener(firstpt,"dragend",onDragSelPoi);
        firstpt.setIcon(icon_pt1);
	firstpt.setIconOffset(markericonoffset);
        map.addShape(firstpt);
        secondpt=new MQA.Poi( {lat:track_points[pt2_id].lat, lng:track_points[pt2_id].lon} );
	secondpt.ptid = pt2_id;
	secondpt.draggable = 1;
	MQA.EventManager.addListener(secondpt,"dragend",onDragSelPoi);
        secondpt.setIcon(icon_pt2);
	secondpt.setIconOffset(markericonoffset);
        map.addShape(secondpt);
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
            
			//TODO
			//curpt.remove();
			map.removeShape(curpt);
			curpt = new MQA.Poi( {lat:track_points[point_id].lat, lng:track_points[point_id].lon} );
			curpt.setIcon(arrowIcon[track_points[point_id].arrow_id]);
			map.addShape(curpt);
			
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
		//TODO
	}
}

function onMoveSelBeginMarker() {
    //TODO
}

function onMoveSelEndMarker() {
    //TODO
}


/* Add buoy marker */
function addBuoyMarker() {
    //TODO
}

/* Remove buoy marker */
function removeBuoyMarker() {
    //TODO
}

function onMapClick(a) {
    refreshCurrentPoint(getCloserPointOfTrack(a.ll.lat,a.ll.lng));
    focusToMap();
}

function redrawTrack() {
	if(typeof(track)!='undefined')
		map.removeShape(track);
	var rect = new MQA.RectLL();
        rect.lr=new MQA.LatLng(track_points[0].lat,track_points[0].lon);
        rect.ul=new MQA.LatLng(track_points[0].lat,track_points[0].lon);
	track = new MQA.LineOverlay();
	track.color = '#FF0000';
	track.colorAlpha = 0.5;
	var pts = new Array(track_points.length*2);
	for(i=0;i<track_points.length;i++) {
		pts[i*2] = track_points[i].lat;
		pts[i*2+1] = track_points[i].lon;
		rect.extend({lat:track_points[i].lat,lng:track_points[i].lon});
	}
	track.setShapePoints(pts);
	map.addShape(track);
	return rect;
}

var track;

MQA.EventUtil.observe(window, 'load', function() {
	
    /*Create an object for options*/ 
    var options={
        elt:document.getElementById('map'),       /*ID of element on the page where you want the map added*/ 
        zoom:13,                                  /*initial zoom level of the map*/ 
        latLng:{lat:track_points[0].lat, lng:track_points[0].lon},   /*center of map in latitude/longitude */ 
        mtype:'osm',                              /*map type (osm)*/ 
        bestFitMargin:0,                          /*margin offset from the map viewport when applying a bestfit on shapes*/ 
        zoomOnDoubleClick:true                    /*zoom in when double-clicking on map*/ 
    };

    /*Construct an instance of MQA.TileMap with the options object*/ 
    window.map = new MQA.TileMap(options);

    MQA.withModule('shapes', 'mousewheel', function() {
        map.enableMouseWheelZoom();
        var rect = redrawTrack();
        
        map.zoomToRect(rect,false);
        
        arrowIcon = [];
        for (var angle=0;angle<360;angle += 15) {
            arrowIcon.push(new MQA.Icon("../images/Arrow" + angle + ".png", 15, 15));
        }
        icon_pt1 = new MQA.Icon("/images/MarkerSelBegin.png",12,20);
        icon_pt2 = new MQA.Icon("/images/MarkerSelEnd.png",12,20);
        
        //var start=new MQA.Poi( {lat:track_points[0].lat, lng:track_points[0].lon} );
        //map.addShape(start);
        curpt=new MQA.Poi( {lat:track_points[0].lat, lng:track_points[0].lon} );
        curpt.setIcon(arrowIcon[track_points[0].arrow_id]);
        map.addShape(curpt);
	
	var startpt = new MQA.Poi( {lat:track_points[0].lat, lng:track_points[0].lon} );
	startpt.setIcon(new MQA.Icon("/images/MarkerStart.png",12,20));
	startpt.setIconOffset(markericonoffset);
	var endpt = new MQA.Poi( {lat:track_points[track_points.length-1].lat, lng:track_points[track_points.length-1].lon} );
	endpt.setIcon(new MQA.Icon("/images/MarkerEnd.png",12,20));
	endpt.setIconOffset(markericonoffset);
	map.addShape(startpt);
	map.addShape(endpt);
	
        
        refreshCurrentPoint(0);

    });
    
     MQA.EventManager.addListener(map,'click',onMapClick);
    
});


snakelengthslider.onchange = function () {
	snakelength = snakelengthslider.getValue();
	refreshSnake(last_point_id);
	if (snakelength==0) {
		// remove track if no snake
		//TODO
	}
}

