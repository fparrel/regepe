
/* Recompute selection infos and move markers */
function refreshSelection(pt1_id, pt2_id) {
  //console.log("refreshSelection %o %o",pt1_id,pt2_id);
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
    if (typeof center_map == "undefined") center_map = 1;

    if (point_id >= 0 && point_id < nbpts && typeof map_track_points!='undefined') {
      last_point_id = point_id;
      hasmoved = 1;
      if (center_map) {
        map.getView().setCenter(map_track_points[point_id]);
      }

      refreshSnake(point_id);
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
  if (snakelength > 0) {
    snake_layer.setVisible(true);
    let minid = cur_pt-snakelength;
    if (minid<0) { minid = 0; }
    let maxid = parseInt(cur_pt)+parseInt(snakelength)*2;
    if (maxid>map_track_points.length-1) { maxid = map_track_points.length-1; }
    snake_feature.setGeometry(new ol.geom.LineString(map_track_points.slice(minid,maxid)));
  } else {
    snake_layer.setVisible(false);
  }
}

snakelengthslider.onchange = function () {
  snakelength = snakelengthslider.getValue();
  refreshSnake(last_point_id);
}

refreshCurrentPoint(0);

// Build track points
var map_track_points = track_points.map(function(tp){return ol.proj.fromLonLat([tp.lon, tp.lat]);}); //tp => ol.proj.fromLonLat([tp.lon, tp.lat]));


// Track layer
var track_layer = new ol.layer.Vector(
  {
    source: new ol.source.Vector(
              { features:[new ol.Feature({
                            geometry: new ol.geom.LineString(map_track_points),
                            name: 'Track'})
                         ]
              }),
    style:new ol.style.Style({stroke:new ol.style.Stroke({color: "#FFBB00",
                                                          width: 2
                                                          })}),
    opacity:0.7
  });


// Snake layer
var snake_feature = new ol.Feature({name:'Snake'});
var snake_layer = new ol.layer.Vector({
  source:new ol.source.Vector({features:[snake_feature]}),
  style:new ol.style.Style({stroke:new ol.style.Stroke({color: "#aaaaaa",
                                                        width: 3
                                                       })}),
  opacity:0.7
});


// Current point layer
var arrow_icons = [];
for (let angle=0;angle<360;angle += 15) {
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


// Selection layer
var selbegin_feature = new ol.Feature();
var selend_feature = new ol.Feature();
var sel_layer = new ol.layer.Vector({
  source:new ol.source.Vector({features:[selbegin_feature,selend_feature]}),
  style:new ol.style.Style({image:new ol.style.Icon({src:'/static/images/MarkerSelBegin.png',anchor:[0.5,1.0]})})
});


// Begin/end points layer
var markerbegin = new ol.style.Style({image:new ol.style.Icon({src:'/static/images/MarkerStart.png',anchor:[0.5,1.0]})});
var markerend = new ol.style.Style({image:new ol.style.Icon({src:'/static/images/MarkerEnd.png',anchor:[0.5,1.0]})});
var feature_begin = new ol.Feature(
        {geometry:new ol.geom.Point(map_track_points[0])});
var feature_end = new ol.Feature(
        {geometry:new ol.geom.Point(map_track_points[map_track_points.length-1])});

var beginend_layer = new ol.layer.Vector(
  {source:new ol.source.Vector(
    {features:[feature_begin,feature_end]
    }),
    style:function(feature) { return (feature==feature_begin)?markerbegin:markerend;}
  });


// IGN Source
function newIGNSource() {
  let resolutions = [];
  let matrixIds = [];
  let maxResolution = ol.extent.getWidth(ol.proj.get('EPSG:3857').getExtent()) / 256;
  for (let i = 0; i < 18; i++) {
    matrixIds[i] = i.toString();
    resolutions[i] = maxResolution / Math.pow(2, i);
  }
  return new ol.source.WMTS({
    url: 'https://wxs.ign.fr/choisirgeoportail/geoportail/wmts',
    //layer: 'GEOGRAPHICALGRIDSYSTEMS.MAPS',
    layer: 'GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2',
    matrixSet: 'PM',
    //format: 'image/jpeg',
    format: 'image/png',
    projection: 'EPSG:3857',
    tileGrid: new ol.tilegrid.WMTS({
      origin: [-20037508, 20037508],
      resolutions: resolutions,
      matrixIds: matrixIds,
    }),
    style: 'normal'
  });
}

function newIGNESSource() {
  let resolutions = [];
  let matrixIds = [];
  let projectionExtent = ol.proj.get('EPSG:4326').getExtent();
  let maxResolution = ol.extent.getWidth(projectionExtent) / 512;
  for (let i = 0; i < 18; i++) {
    matrixIds[i] = "EPSG:4326:" + i;
    resolutions[i] = maxResolution / Math.pow(2, i);
  }
  return new ol.source.WMTS({
    url: 'https://www.ign.es/wmts/mapa-raster',
    layer: 'MTN',
    matrixSet: 'EPSG:4326',
    format: 'image/jpeg',
    projection: 'EPSG:4326',
    tileGrid: new ol.tilegrid.WMTS({
      origin: ol.extent.getTopLeft(projectionExtent),
      resolutions: resolutions,
      matrixIds: matrixIds,
    }),
    style: 'normal',
    attributions: '<a href="http://www.ign.es" target="_blank">IGN.es</a>'
  });
}


// Open topo map source
function newOpenTopoSource() {
  return new ol.source.OSM({
              url: 'https://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png'
            });
}


function newSource(maptype) {
  if (maptype=='OpenTopo') {
    return newOpenTopoSource();
  } else if (maptype=='OSM') {
    return new ol.source.OSM();
  } else if (maptype==='GeoPortal') {
    return newIGNSource();
  } else if (maptype==='IGNES') {
    return newIGNESSource();
  }
}


// Map creation
var map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: newSource(map_type)
      }),
      track_layer,
      snake_layer,
      beginend_layer,
      sel_layer,
      curpt_layer
    ],
    view: new ol.View({
      center: map_track_points[0],
      zoom: 4
    })
  });

map.getView().fit(new ol.extent.boundingExtent(map_track_points));

map.addEventListener("click",function(e){
  var lonlat = ol.proj.toLonLat(e.coordinate);
  refreshCurrentPoint(getCloserPointOfTrack(lonlat[1],lonlat[0]));
});

var modify = new ol.interaction.Modify({features:new ol.Collection([selbegin_feature,selend_feature])})
map.addInteraction(modify);
function onSelMarkerMove(e) {
  let lonlat1 = ol.proj.toLonLat(selbegin_feature.getGeometry().getCoordinates());
  let ptid1 = getCloserPointOfTrack(lonlat1[1],lonlat1[0]);
  let lonlat2 = ol.proj.toLonLat(selend_feature.getGeometry().getCoordinates());
  let ptid2 = getCloserPointOfTrack(lonlat2[1],lonlat2[0]);
  refreshSelection(ptid1,ptid2);
  moveChartMarkerLeft(ptid1,selchartid);
  moveChartMarkerRight(ptid2,selchartid);
}
modify.on('modifyend',onSelMarkerMove);

