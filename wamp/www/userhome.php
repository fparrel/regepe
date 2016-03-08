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
<?php include('header.html'); ?>
<div id="body">
    <h1>User <?php print $_GET['user']; ?></h1>
    <h2>My tracks</h2>
    <!--<div style='height:320px;'/>-->
    Selection: <input type="button" value="Delete" onclick="onDeleteClick();"/> <input type="button" value="Merge" onclick="onMergeClick();"/><br/>
    <div style="width:50%; overflow:auto; position: absolute; height: 100%;">
        <table><thead></thead><tbody>
<?php
$maps = new SimpleXMLElement(file_get_contents('http://localhost/cgi-bin/showuser.py?user='.$_GET['user']));
foreach($maps->map as $map) {
	$mapid = $map['mapid'];
	$desc = $map;
	$date = $map['date'];
	$lat = $map['lat'];
	$lon = $map['lon'];
	//print $mapid.$desc.$date.$user.$lat.$lon;
	print '<tr id="row'.$mapid.'" style="cursor:pointer;" onclick="changePreview(\''.$mapid.'\','.$lat.','.$lon.',\''.str_replace("\n","\\n",$desc).'\')"><td><input class="chkbx" type="checkbox" name="chkbx'.$mapid.'"/></td><td>'.$date.'</td><td>'.$desc.'</td><td style="font-size:10px;"><a href="showmap-flot.php?mapid='.$mapid.'">View</a></tr>';
}
?>
        </tbody></table>
    </div>
    <div id="previewout" style="position: absolute; margin-left: 50%; heigth:110px;width:130px;"><img style="visibility:hidden;" width="130" height="110" name="preview" id="preview"></div>
    <div id="map_of_maps" style="height:300px;width:400px;right:0; position: absolute; margin-right: 10px;"></div>
    <div id="footer_push"></div>
</div>
</body>
</html>
<script type="text/javascript" src="javascript/xmlhttprequest.js"></script>
<script type="text/javascript" src="javascript/header.js"></script>
<script type="text/javascript" src="javascript/db.js"></script>
<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=${GMapsApiKey}" type="text/javascript"></script>
<script src="javascript/preview.js" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[

function getMapList() {
    var eles = document.getElementsByClassName("chkbx");
    var mapidlist = "";
    for(var i=0;i<eles.length;i++) {
        if(eles[i].checked) {
            if(mapidlist.length>0)
                mapidlist += "," + eles[i].name.substring(5);
            else
                mapidlist += eles[i].name.substring(5);
        }
    }
    return mapidlist;
}

function onMergeClick() {
    var mapidlist = getMapList();
    var user_sess = getSessionFromCookie();
    var url = '/cgi-bin/merge.py?mapids='+ mapidlist + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
    document.location.href = url;
}

function onDeleteClick() {
    var mapidlist = getMapList();
    var user_sess = getSessionFromCookie();
    var url = '/cgi-bin/delmaps.py?mapids='+ mapidlist + '&user=' + user_sess[0] + '&sess=' + user_sess[1];
    if (confirm("Confirm deletion of "+(mapidlist.split(",").length)+" map(s)?")) { 
        document.location.href = url;
    }
}

//]]>
</script>
