<?php

/*function handleErrorVoid($errno, $errstr, $errfile, $errline, array $errcontext) {   return true;}
function handleErrorThrow($errno, $errstr, $errfile, $errline, array $errcontext)
{
    // error was suppressed with the @-operator
    if (0 === error_reporting()) {
        return false;
    }

    throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
}
set_error_handler('handleErrorVoid');*/

$pngfname = 'previews/'.$_GET['mapid'].'.png';
$phpfname = './maps/'.$_GET['mapid'].'-json.php.gz';
if(!file_exists($phpfname)) {
	$phpfname = './maps/'.$_GET['mapid'].'-json.php';
}

$pngmtime = filemtime($pngfname);
$phpmtime = filemtime($phpfname);

#print "fname here28=$pngfname";

if((!file_exists($pngfname))||($pngmtime<$phpmtime)||(filesize($pngfname)==0)) {

#print 'dont exists';

/* Get Map data */
$filename = './maps/'.$_GET['mapid'].'-json.php.gz';
if (file_exists($filename)) {
    #print 'read gz';
    /* compressed */
    $handle = fopen($filename, 'rb');
    /*$contents = gzuncompress(fread($handle, filesize($filename)));
    set_error_handler('handleErrorThrow');*/
    try {
        $contents = gzdecode(fread($handle, filesize($filename)));
    } catch(ErrorException $e) {
        try {
            fseek($handle,0);
            $contents = gzuncompress(fread($handle, filesize($filename)));
        } catch(ErrorException $e) {
            print '<html><head></head><body><p>'.$e.'</p></body></html>';
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

#print 'wind?';

$windindex = strpos($map_data,'wind = ');
if ($windindex!=false) {
    $wind = substr($map_data,$windindex+strlen('wind = '),1);
}

#print 'parse points';

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
#print 'foreach';
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

#print 'build url';

/* build url */
$centerlat = ($maxlat+$minlat)/2;
$centerlon = ($maxlon+$minlon)/2;
$center_url = "center=$centerlat,$centerlon";
foreach($markers as $mid=>$marker) {
	$markers_ordered[$markers_idx[$mid]] = $marker;
}
#print 'ksort';
ksort($markers_ordered);
#print 'here';
$markers_url = 'markers=size:tiny|'.$start.'|'.$end;
$path_url = "path=weight:3|$start|".implode('|',$markers_ordered)."|$end";
$url = "http://maps.googleapis.com/maps/api/staticmap?size=130x110&maptype=terrain&${markers_url}&${path_url}&sensor=false";

$host = "maps.googleapis.com";
$res = "/maps/api/staticmap?size=130x110&maptype=terrain&${markers_url}&${path_url}&sensor=false";

#print 'here<br/>';
print $url;
exit;

/* download */
$fp = fsockopen("maps.googleapis.com", 80);
if (!$fp) {
     echo "Cannot open\n";
} else {
  fwrite($fp, "GET ".$res." HTTP/1.0\r\n\r\n");
  stream_set_timeout($fp, 2);
  
  		do // loop until the end of the header
		{
			$header .= fgets ( $io, 128 );

		} while ( strpos ( $header, "\r\n\r\n" ) === false );

  $out = '';
  while (!feof($f)) {
    $res = fread($fp, 8192);
    if ($res==false ) { break; }

    $info = stream_get_meta_data($fp);

    if ($info['timed_out']) {
        echo 'Timeout';
    } else {
        echo "ok";
        $out .= $res;
    }
  }
  fclose($fp);
  $fout = fopen($pngfname,'wb');
  //fwrite($fout,substr($response_data, strpos($out,"\r\n\r\n")+4));
  fwrite($fout,$out);
  fclose($fout);
}

/*
$f = fopen($url,'r');
stream_set_timeout($f,3);
$fout = fopen($pngfname,'wb');
while (!feof($f)) {
	fwrite($fout,fread($f, 8192));
}
fclose($fout);
fclose($f);
*/
}

/* output file */
/*header('Content-Type: image/png');
readfile($pngfname);*/
exit;

?>
