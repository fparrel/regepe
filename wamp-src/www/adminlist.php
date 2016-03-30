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
<?php if ($_SERVER['REQUEST_METHOD'] === 'POST') { ?>
  <div style="position:fixed;left:0px;">
    <input type="button" value="Add pwd cookie" onclick="DoAddMapPwdCookie();"/>
    <input type="button" value="Rebuild" onclick="DoRebuild();"/>
    <input type="checkbox" value="forcerecompspd" id="forcerecompspd"><label for="forcerecompspd">recomp spd</label>
  </div>
  <h1>List of maps</h1>
  <table><thead></thead><tbody>
<?php
/*
print_r(dba_handlers(true));
$h=dba_open('../cgi-bin/test.dbm.db','rd','gdbm');
if($h) {
  $world = dba_fetch('hello',$h);
  print ' gdbm="'.$world.'"';
  dba_close($h);
}else print_r(error_get_last());
$h=dba_open('../cgi-bin/test.dbhash','rd','gdbm');
if($h) {
  $world = dba_fetch('hello',$h);
  print ' dbhash="'.$world.'"';
  dba_close($h);
}else print_r(error_get_last());
print 'out="'.exec("whoami").'"<br/>';
print 'out="'.exec("ls ../cgi-bin/test.dbhash").'"<br/>';
print 'out="'.exec("file ../cgi-bin/test.dbhash").'"<br/>';
print 'out="'.exec("env").'"<br/>';
print 'out="'.exec('db_dump ../cgi-bin/test.dbhash').'"';
*/
$maps = new SimpleXMLElement(file_get_contents('http://localhost/cgi-bin/admingetmaps.py?pwd='.$_POST['pwd']));
$i=1;
foreach($maps->map as $map) {
	$mapid = $map['mapid'];
	$desc = $map;
	$date = $map['date'];
	$user = $map['user'];
	$lat = $map['lat'];
	$lon = $map['lon'];
	//print $mapid.$desc.$date.$user.$lat.$lon;
	$pwd = $map['pwd'];
	/*$h=dba_open('../cgi-bin/maps/'.$mapid.'.db','rd','cdb');
	if($h) {
		$pwd = dba_fetch('pwd',$h);
		dba_close($h);
	}else print_r(error_get_last());*/
	print '<tr id="row'.$mapid.'" style="cursor:pointer;" onclick="changePreview(\''.$mapid.'\','.$lat.','.$lon.',\''.str_replace("\n","\\n",$desc).'\')"><td style="font-size:10px;"><a href="showmap-flot.php?mapid='.$mapid.'" target="mapframe">'.$i.'</a><input type="hidden" value="'.$pwd.'" id="pwdof_'.$mapid.'"/></td><td>'.$date.'</td><td>'.$desc.'</td><td>'.$user.'</td></tr>';
	//print '<td style="font-size:10px;"><a href="cgi-bin/rebuild.py?mapid='.$mapid.'" target="mapframe">Rebuild</a><br/><a href="cgi-bin/rebuild.py?mapid='.$mapid.'&forcerecompspd=yes" target="mapframe">Rebuild+spd</a></td></tr>';
  $i++;
}
?>
	</tbody></table>
  <div id="previewout" style="position:absolute;top:0px;right:0px;heigth:110px;width:130px;z-index:10;"><img style="visibility:hidden;border-style:solid;border-width:1px;" width="130" height="110" name="preview" id="preview"/></div>
<?php } else { ?>
  <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST"><input type="password" name="pwd"/><input type="submit"/></form>
<?php } ?>
</body>
</html>
<script type="text/javascript">
var curmapid;
function DoRebuild() {
  var recomp=(document.getElementById("forcerecompspd").checked)?"yes":"no";
  parent.document.getElementById("mapframe").src="/cgi-bin/rebuild.py?mapid="+curmapid+"&forcerecompspd="+recomp;
}
function DoAddMapPwdCookie() {
  AddMapPwdCookie(curmapid,document.getElementById("pwdof_"+curmapid).value);
}
function AddMapPwdCookie(mapid,pwd) {
	var date = new Date();
	date.setTime(date.getTime()+(10*24*60*60*1000));
	var expires = "; expires="+date.toGMTString();
	document.cookie = "pwd"+mapid+"="+pwd+expires+"; path=/";
}

function changePreview(mapid,lat,lon,desc) {
	showPreview(mapid);
}	

var prevrow = null;
var prevcolor = null;
var prevborder = null;

function showPreview(mapid) {
	curmapid=mapid;
	document.images['preview'].src = '/thumbnail.php?mapid='+mapid;
	document.getElementById("preview").style.visibility = 'visible';
	if(prevrow!=null) {
		prevrow.style.backgroundColor = prevcolor;
		prevrow.style.border = prevborder;
	}
	prevcolor = document.getElementById("row"+mapid).style.backgroundColor;
	prevborder = document.getElementById("row"+mapid).style.border;
	prevrow = document.getElementById("row"+mapid);
	document.getElementById("row"+mapid).style.backgroundColor = "#A7C942";
	document.getElementById("row"+mapid).style.border ='1px solid ';
}
</script>
