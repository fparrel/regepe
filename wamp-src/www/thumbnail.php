<?php

function handleErrorVoid($errno, $errstr, $errfile, $errline, array $errcontext) {   return true;}
function handleErrorThrow($errno, $errstr, $errfile, $errline, array $errcontext)
{
    // error was suppressed with the @-operator
    if (0 === error_reporting()) {
        return false;
    }

    throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
}
//set_error_handler('handleErrorVoid');

$pngfname = 'previews/'.$_GET['mapid'].'.png';
$phpfname = './maps/'.$_GET['mapid'].'-json.php.gz';
if(!file_exists($phpfname)) {
	$phpfname = './maps/'.$_GET['mapid'].'-json.php';
}

if((!file_exists($pngfname))||(filemtime($pngfname)<filemtime($phpfname))||(filesize($pngfname)==0)) {

/* Get Map data */
$filename = './maps/'.$_GET['mapid'].'-json.php.gz';
if (file_exists($filename)) {
    /* compressed */
    $handle = fopen($filename, 'rb');
    //$contents = gzuncompress(fread($handle, filesize($filename)));
    //set_error_handler('handleErrorThrow');
    try {
        $contents = gzdecode(fread($handle, filesize($filename)));
    } catch(ErrorException $e) {
        try {
            fseek($handle,0);
            $contents = gzuncompress(fread($handle, filesize($filename)));
        } catch(ErrorException $e) {
            print $e;
        }
    }
    fclose($handle);
    //print ($contents);
    eval($contents);
}
else {
    /* not compressed */
    include('./maps/'.$_GET['mapid'].'.php');
}

$windindex = strpos($map_data,'wind = ');
if ($windindex!=false) {
    $wind = substr($map_data,$windindex+strlen('wind = '),1);
}

/* parse map data */
$i = strpos($map_data,'track_points');
if(!$i) {
	die('Parse error');
}
$i = strpos($map_data,'[',$i);
if(!$i) {
	die('Parse error');
}
$j = strpos($map_data,'];',$i);
if(!$j) {
	die('Parse error');
}
$pts_str = explode('new Point(',substr($map_data,$i+1,$j-$i-1));
$idx = 0;
$minlat = 90.0;
$maxlat = -90.0;
$minlon = 180.0;
$maxlon = -180.0;
$step = round((sizeof($pts_str)-1)/20);
if($step<1) $step = 1;
$i_markers = 4;
foreach($pts_str as $pt_str) {
	if($idx>0) {
		$pt = explode(',',$pt_str);
		$lat = $pt[0];
		$lon = $pt[1];
		if($idx==1) {
			$start = "$lat,$lon";
		}
		if($lat<$minlat) {
			$minlat = $lat;
			$markers[0] = "$lat,$lon";
			$markers_idx[0] = $idx;
		}
		if($lat>$maxlat) {
			$maxlat = $lat;
			$markers[1] = "$lat,$lon";
			$markers_idx[1] = $idx;
		}
		if($lon<$minlon) {
			$minlon = $lon;
			$markers[2] = "$lat,$lon";
			$markers_idx[2] = $idx;
		}
		if($lon>$maxlon) {
			$maxlon = $lon;
			$markers[3] = "$lat,$lon";
			$markers_idx[3] = $idx;
		}
		if($idx % $step == 0) {
			$markers[$i_markers] = "$lat,$lon";
			$markers_idx[$i_markers] =  $idx;
			$i_markers++;
		}
	}
	$idx++;
}
$end = "$lat,$lon";

/* build url */
$centerlat = ($maxlat+$minlat)/2;
$centerlon = ($maxlon+$minlon)/2;
$center_url = "center=$centerlat,$centerlon";
foreach($markers as $mid=>$marker) {
	$markers_ordered[$markers_idx[$mid]] = $marker;
}
ksort($markers_ordered);
$markers_url = 'markers=size:tiny|'.$start.'|'.$end;
$path_url = "path=weight:3|$start|".implode('|',$markers_ordered)."|$end";
$url = "http://maps.googleapis.com/maps/api/staticmap?size=130x110&maptype=terrain&${markers_url}&${path_url}&sensor=false";

/* download */
$f = fopen($url,'r');
$fout = fopen($pngfname,'wb');
while (!feof($f)) {
	fwrite($fout,fread($f, 8192));
}
fclose($fout);
fclose($f);

}

/* output file */
header('Content-Type: image/png');
readfile($pngfname);
exit;

?>
