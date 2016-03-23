
/* Chart object constructor */
function Chart(name,marginsize,pt2px) {
	this.name = name;
	this.marginsize = marginsize + 9;
	this.pt2px = pt2px;
}

/* Point object constructors */
function Point(lat,lon,time,ele,spd,arrow_id,course) {
	this.lat = lat;
	this.lon = lon;
	this.time = time;
	this.ele = ele;
	this.spd = spd;
	this.arrow_id = arrow_id;
	this.course = course;
}
function Point(lat,lon,time,ele,spd,arrow_id,course,hr) {
	this.lat = lat;
	this.lon = lon;
	this.time = time;
	this.ele = ele;
	this.spd = spd;
	this.arrow_id = arrow_id;
	this.course = course;
    this.hr=hr;
}

/* Returns the point id on map given a X position on the chart (this function takes into account the chart margin) 
   Returns -1 if posx is out of bounds */
function getPointIdFromChartPosX(posx,chartid) {
	posx -= chart[chartid].marginsize - 9;
	for (pointid=0;pointid<chart[chartid].pt2px.length-1;pointid++) {
		if ((chart[chartid].pt2px[pointid]<=posx)&&
		    (chart[chartid].pt2px[pointid+1]>=posx)) {
			return (pointid);
		}
	}
	return (-1);
}

/* Returns the point id of the closer track's point to (lat,lng) */
function getCloserPointOfTrack(lat,lng) {
	var dmin = 10000000;
	var imin = -1;
	var d = 0;
	var i = 0;
	for (i=0;i<track_points.length;i++) {
		d = geodeticDist(track_points[i].lat,track_points[i].lon,lat,lng);
		if (d<dmin) {
			dmin = d;
			imin = i;
		}
	}
	return imin;
}
