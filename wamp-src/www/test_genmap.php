<?php
function exception_handler($exception) {
    header('Content-Type: text/html');
  echo "Exception : " , $exception->getMessage(), "\n";
}
function error_handler($errno, $errstr, $errfile, $errline) {
    header('Content-Type: text/html');
  echo "Erreur : " , $errstr, "\n";
  exit;
}

set_exception_handler('exception_handler');
set_error_handler('error_handler');

$row1 = $_GET['row1'];
$row2 = $_GET['row2'];
$col1 = $_GET['col1'];
$col2 = $_GET['col2'];
$matrix = $_GET['matrix'];
$apikey = $_GET['key'];
$img = imagecreate(($row2-$row1+1)*256,($col2-$col1+1)*256);
$bg = imagecolorallocate($img, 0, 0, 0);
imagefill($img, 0, 0, $bg);
$col_ellipse = imagecolorallocate($img, 255, 255, 255);

$url = "http://gpp3-wxs.ign.fr/${apikey}/autoconf/?output=json&callback=OpenLayers.Protocol.Script.registry.regId1";
$lines = file($url);

for($y=0,$col=$col1;$col<=$col2;$col++,$y+=256) {
    for($x=0,$row=$row1;$row<=$row2;$row++,$x+=256) {
        $url = "http://wxs.ign.fr/".$apikey."/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX=".$matrix."&TILEROW=".$row."&TILECOL=".$col."&FORMAT=image%2Fjpeg";
        $tile = imagecreatefromjpeg($url);
        /*if($tile) {
            imagecopy($img,$tile,$x,$y,0,0,256,256);
        }*/
        imageellipse($img,$x+128,$y+128,50,50,$col_ellipse);
    }
}
header('Content-Type: image/jpeg');
imagejpeg($img);
imagedestroy($img);
?>