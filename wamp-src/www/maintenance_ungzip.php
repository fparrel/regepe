<?php
/* Get Map data */
$filename = './maps/'.$_GET['mapid'].'.php.gz';
if (file_exists($filename)) {
    /* compressed */
    $handle = fopen($filename, 'rb');
    $contents = gzuncompress(fread($handle, filesize($filename)));
    fclose($handle);
    $filename = './maps/'.$_GET['mapid'].'.php';
    $handle = fopen($filename, 'wb');
    fwrite($handle,"<?php\n");
    fwrite($handle,$contents);
    fwrite($handle,"?>\n");
    fclose($handle);    
}
?>
