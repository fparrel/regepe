<?php
header('Content-type: text/javascript; charset=utf-8');
header('Cache-Control: no-cache, must-revalidate');

function handleError($errno, $errstr, $errfile, $errline, array $errcontext)
{
    // error was suppressed with the @-operator
    if (0 === error_reporting()) {
        return false;
    }

    throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
}
set_error_handler('handleError');

/* Get Map data */
$filename = '../maps/'.$_GET['mapid'].'.php.gz';
if (file_exists($filename)) {
    /* compressed */
    $handle = fopen($filename, 'rb');
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
    include('../maps/'.$_GET['mapid'].'.php');
}
echo $map_data;
?>
