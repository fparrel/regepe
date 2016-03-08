
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

/* Called when a map selection marker has been moved */
function onSelMarkerMove( ) {
    //TODO
}

/* Recompute selection infos and move markers */
function refreshSelection(pt1_id, pt2_id) {
    //TODO
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

/* Add buoy marker */
function addBuoyMarker() {
    //TODO
}

/* Remove buoy marker */
function removeBuoyMarker() {
    //TODO
}

snakelengthslider.onchange = function () {
	snakelength = snakelengthslider.getValue();
	refreshSnake(last_point_id);
	if (snakelength==0) {
		// remove track if no snake
        //TODO
	}
}

refreshCurrentPoint(0);
