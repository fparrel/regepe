<?php
/* Get Map data */
$filename = './maps/'.$_GET['mapid'].'.php';
if (file_exists($filename)) {
    /* compressed */
    $handle = fopen($filename, 'rb');
    $contents = fread($handle, filesize($filename));
    fclose($handle);
}
else {
    $filename = './maps/'.$_GET['mapid'].'.php.gz';
    if (file_exists($filename)) {
        $handle = fopen($filename, 'rb');
        $contents = "<?php\n".gzuncompress(fread($handle, filesize($filename)))."\n?>\n";
        fclose($handle);
    }
    else {
        $contents = NULL;
    }
}
if($contents) {
    $filename = './maps/'.$_GET['mapid'].'.php.gz';
    $handle = fopen($filename, 'wb');
    //$contentsgz = gzcompress($contents);
    $contentsgz = gzencode($contents);
    fwrite($handle,$contentsgz);
    fclose($handle);    
}
?>
