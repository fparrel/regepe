<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><title>Replay your GPS Tracks with REGEPE</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<link type="text/css" rel="StyleSheet" href="styles/inputform.css" />
<style type="text/css">
table { border-collapse:collapse;}
</style>
</head>
<body>
    <div id="wrapper">
<?php include('header.html'); ?>
        <div id="body" style="position: static;">
            <h1>Replay your GPS Tracks with REGEPE</h1>
	    <h2>Last updates | <a href="indexall.php">All updates</a></h2>
        <div style="position: absolute;">
        <div style='width:500px; left:0; margin-left : 10px; '>
	    <table style="position: static;"><thead></thead><tbody>
<?php
$maps = new SimpleXMLElement(file_get_contents('http://localhost/cgi-bin/gethistory.py?limit=10'));
foreach($maps->map as $map) {
	$mapid = $map['mapid'];
	$desc = $map;
	$date = $map['date'];
	$user = $map['user'];
	$lat = $map['lat'];
	$lon = $map['lon'];
	//print $mapid.$desc.$date.$user.$lat.$lon;
	print '<tr class="maplistitm" id="row'.$mapid.'" style="cursor:pointer;" onclick="changePreview(\''.$mapid.'\','.$lat.','.$lon.',\''.str_replace("'","\\'",str_replace("\n","\\n",$desc)).'\')"><td>'.$date.'</td><td>'.$desc.'</td><td> by '.$user.'</td><td style="font-size:10px;"><a href="showmap-flot.php?mapid='.$mapid.'">View</a></tr>';
}
?>
	</tbody></table>
        </div>

    <div style="position: static;"><a href="tour.php?step=1"><img src="images/PlayStart64x64.png" width="64" height="64"/>Take tour</a></div>
    </div>
    <div id="previewout" style="margin-left: 510px; heigth:110px;width:130px; position:absolute; z-index:10;"><img style="visibility:hidden; border-style:solid;border-width:1px;" width="130" height="110" name="preview" id="preview"/></div>
    <div id="map_of_maps" style="height:300px;width:400px;right:0; position:absolute; margin-right: 10px; z-index:9;"></div>
        </div>
        <div id="footer_push"></div>
    </div>
<?php include('footer.html'); ?>
</body>
</html>
<script src="javascript/xmlhttprequest.js" type="text/javascript"></script>
<script src="javascript/header.js" type="text/javascript"></script>
<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=${GMapsApiKey2}" type="text/javascript"></script>
<script src="javascript/preview.js" type="text/javascript"></script>
