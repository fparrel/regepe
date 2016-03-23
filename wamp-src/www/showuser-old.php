<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><title>Replay your GPS Tracks with REGEPE</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<link type="text/css" rel="StyleSheet" href="styles/inputform.css" />
</head>
<body>
<?php include('header.html'); ?>
<div id="body">
<h1>User <?php print $_GET['user']; ?></h1>
<div id="map_list">Loading...</div>
</div>
</body>
</html>
<script type="text/javascript" src="javascript/xmlhttprequest.js"></script>
<script type="text/javascript" src="javascript/header.js"></script>
<script type="text/javascript" src="javascript/db.js"></script>
<script type="text/javascript">
//<![CDATA[

/* sort Maps by decreasing date */
function sortMaps(map1,map2) {
    return ((map1.startdate < map2.startdate) ? 1 : ((map1.startdate > map2.startdate) ? -1 : 0));
}

/* Map object */
function Map(mapid,desc,startdate,lat,lon) {
    this.mapid = mapid;
    this.desc = desc;
    this.startdate = startdate;
    this.lat = lat;
    this.lon = lon;
}

function onReadystatechange() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            
            var maps = this.responseXML.getElementsByTagName("map");
            var map_list = new Array(maps.length);
            var i;
            for (i=0;i<maps.length;i++) {
                var mapid = maps[i].getAttribute('mapid');
                var desc = maps[i].childNodes[0].nodeValue;
                var startdate = maps[i].getAttribute('date');
                var lat = maps[i].getAttribute('lat');
                var lon = maps[i].getAttribute('lon');
                map_list[i] = new Map(mapid,desc,startdate,lat,lon);
                //map_list_contents = map_list_contents + '<li><a href="showmap.php?mapid='+mapid+'"/>'+desc+'</a> '+startdate+'</li>';
            }
            map_list.sort(sortMaps);
            var map_list_contents = '';
            for (i=0;i<map_list.length;i++) {
                map_list_contents = map_list_contents + '<li>'+map_list[i].startdate+' <a href="showmap.php?mapid='+map_list[i].mapid+'"/>'+map_list[i].desc+'</a></li>';
            }
            document.getElementById('map_list').innerHTML = '<ul>'+map_list_contents+'</ul>';
        }
    }
}

function fillPage() {
    var query_str = "/cgi-bin/showuser.py?user=<?php print $_GET['user']; ?>";
    var client = new XMLHttpRequest();
    client.open('GET',query_str);
    client.send();
    client.onreadystatechange = onReadystatechange;
}

fillPage();

//]]>
</script>
