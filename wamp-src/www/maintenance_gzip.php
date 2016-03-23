<?php
/* Get Map data */
$filename = './maps/'.$_GET['mapid'].'.php';
if (file_exists($filename)) {
    /* compressed */
    $handle = fopen($filename, 'rb');
    $contents = fread($handle, filesize($filename));
    fclose($handle);
    $filename = './maps/'.$_GET['mapid'].'.php.gz';
    $handle = fopen($filename, 'wb');
    //$contentsgz = gzcompress($contents);
    $contentsgz = gzencode($contents);
    fwrite($handle,$contentsgz);
    fclose($handle);    
}
?>
