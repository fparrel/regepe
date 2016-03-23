
/* remove all markers */
function removeMarkers() {
    var i;
    for(i=0;i<markers.length;i++) {
        map.removeShape(markers[i]);
    }
    markers = [];
}

/* redraw track polyline from contents of points */
function redrawLine() {
    if (typeof line != "undefined") {
        map.removeShape(line);
    }
    if(noline)return;
    line = new MQA.LineOverlay();
    line.color = '#FF0000';
    line.colorAlpha = 0.5;
    var pts = new Array((points.length)*2);
    var i;
    for(i=0;i<points.length;i++) {
    	pts[i*2] = points[i].pt.lat;
		pts[i*2+1] = points[i].pt.lon;
    }
    line.setShapePoints(pts);
    map.addShape(line);
}

function onDragPtMarker() {
    var pt_marker = this;
    points[pt_marker.pt_index].pt.lat = this.getLatLng().lat;
    points[pt_marker.pt_index].pt.lon = this.getLatLng().lng;
    redrawLine();
    askElevation(points[pt_marker.pt_index].pt);
    refreshLength();
    refreshUrls();
}

function selectWptOnMap(index) {
    if(sel_index!=-1) {
        markers[sel_index].setIcon(icon_pt);
    }
    markers[index].setIcon(icon_sel);
    sel_index = index;
}

function onClickPtMarker() {
    var pt_marker = this;
    var i;
    if(sel_index!=-1) {
        markers[sel_index].setIcon(icon_pt);
    }
    /*for(i=0;i<points.length;i++) {
        points[i].setIcon(icon_pt);
    }*/
    pt_marker.setIcon(icon_sel);
    sel_index = this.pt_index;
    selectWpt(sel_index);
}

/* Add a given point object to the map */
function addPoint(newpt,index) {
    var pt_marker;
    if (index==0) {
        pt_marker = new MQA.Poi( {lat:newpt.lat, lng:newpt.lon} );
        pt_marker.setIcon(icon_pt);
    }
    else {
        pt_marker = new MQA.Poi( {lat:newpt.lat, lng:newpt.lon} );
        pt_marker.setIcon(icon_pt);
    }
    points[index] = pt_marker;
    points[index].pt = newpt;
    pt_marker.draggable = 1;
    map.addShape(pt_marker);
    markers.push(pt_marker);
    pt_marker.pt_index = index;
    MQA.EventManager.addListener(pt_marker,"dragend",onDragPtMarker);
    MQA.EventManager.addListener(pt_marker,"click",onClickPtMarker);
    addWpt(points[index].pt,index);
}

function removeMarker(index) {
    map.removeShape(points[index]);
}

function onMapClick(a) {
    addPoint(new Point(a.ll.lat,a.ll.lng),points.length);
    if (points.length>0) {
        redrawLine();
        refreshLength();
        refreshUrls();
    }
}

MQA.EventUtil.observe(window, 'load', function() {
	
    /*Create an object for options*/ 
    var options={
        elt:document.getElementById('map'),       /*ID of element on the page where you want the map added*/ 
        zoom:5,                                  /*initial zoom level of the map*/ 
        latLng:{lat:45.0, lng:0.0},   /*center of map in latitude/longitude */ 
        mtype:'osm',                              /*map type (osm)*/ 
        bestFitMargin:0,                          /*margin offset from the map viewport when applying a bestfit on shapes*/ 
        zoomOnDoubleClick:true                    /*zoom in when double-clicking on map*/ 
    };

    /*Construct an instance of MQA.TileMap with the options object*/ 
    window.map = new MQA.TileMap(options);

    MQA.withModule('mousewheel', function() {
        map.enableMouseWheelZoom();
    });
    icon_pt = new MQA.Icon("/images/MarkerSelBegin.png",12,20);
    icon_sel = new MQA.Icon("/images/MarkerStart.png",12,20);
    
    MQA.EventManager.addListener(map,'click',onMapClick);
    
    MQA.withModule('shapes', function() {
        // add points from URL
        addPointsFromUrl();
    });
    
});

function addPointsFromUrl() {
    if (pts_from_url.length>0) {
        var rect = new MQA.RectLL();
        rect.lr=new MQA.LatLng(pts_from_url[0].lat,pts_from_url[0].lon);
        rect.ul=new MQA.LatLng(pts_from_url[0].lat,pts_from_url[0].lon);
        var i;
        for(i=0;i<pts_from_url.length;i++) {
            addPoint(pts_from_url[i],i);
            rect.extend({lat:pts_from_url[i].lat,lng:pts_from_url[i].lon});
        }
        map.zoomToRect(rect,false);
        redrawLine();
        refreshLength();
        refreshUrls();
    }
}
