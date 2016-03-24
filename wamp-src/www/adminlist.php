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
        <div id="body" style="position: static;">
            <h1>List of maps</h1>
	    <table style="position: static;"><thead></thead><tbody>
<?php
$maps = new SimpleXMLElement(file_get_contents('http://localhost/cgi-bin/gethistory.py'));
foreach($maps->map as $map) {
	$mapid = $map['mapid'];
	$desc = $map;
	$date = $map['date'];
	$user = $map['user'];
	$lat = $map['lat'];
	$lon = $map['lon'];
	//print $mapid.$desc.$date.$user.$lat.$lon;
	$pwd = 'xxxx';
	$h=dba_open('../cgi-bin/maps/'.$mapid.'.db','rd','db4');
	if($h) {
		$pwd = dba_fetch('pwd',$h);
		dba_close($h);
	}else print_r(error_get_last());
	print '<tr id="row'.$mapid.'" style="cursor:pointer;" onclick="changePreview(\''.$mapid.'\','.$lat.','.$lon.',\''.str_replace("\n","\\n",$desc).'\')"><td>'.$date.'</td><td>'.$desc.'</td><td> by '.$user.'</td>';
	print '<td style="font-size:10px;"><a href="showmap-flot.php?mapid='.$mapid.'&maptype=GMaps" target="mapframe">View</a></td>';
	print '<td style="font-size:10px;">
<input type="button" value="Add map pwd cookie" onclick="AddMapPwdCookie(\''.$mapid.'\',\''.$pwd.'\');"/><a href="cgi-bin/rebuild.py?mapid='.$mapid.'" target="mapframe">Rebuild</a></td></tr>';
}
?>
	</tbody></table>
    <div id="previewout" style="margin-left: 510px; heigth:110px;width:130px; position:absolute; z-index:10;"><img style="visibility:hidden; border-style:solid;border-width:1px;" width="130" height="110" name="preview" id="preview"/></div>
    <!--<div id="map_of_maps" style="height:300px;width:400px;right:0; position:absolute; margin-right: 10px; z-index:9;"></div>-->
        </div>
        <div id="footer_push"></div>
    </div>
</body>
</html>
<script src="javascript/xmlhttprequest.js" type="text/javascript"></script>
<script src="javascript/header.js" type="text/javascript"></script>
<script src="javascript/preview.js" type="text/javascript"></script>
<script type="text/javascript">
    function AddMapPwdCookie(mapid,pwd) {
        var date = new Date();
        date.setTime(date.getTime()+(10*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = "pwd"+mapid+"="+pwd+expires+"; path=/";
    }
</script>
    