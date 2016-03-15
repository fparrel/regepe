<?php


function gz2gz($mapid) {
    /* Get Map data */
    $filename = './maps/'.$mapid.'.php';
    if (file_exists($filename)) {
        /* compressed */
        $handle = fopen($filename, 'rb');
        $contents = fread($handle, filesize($filename));
        fclose($handle);
    }
    else {
        $filename = './maps/'.$mapid.'.php.gz';
        if (file_exists($filename)) {
            $handle = fopen($filename, 'rb');
            $contents = gzuncompress(fread($handle, filesize($filename)));
            fclose($handle);
        }
        else {
            $contents = NULL;
        }
    }
    if($contents) {
        $filename = './maps/'.$mapid.'.php.gz';
        $handle = fopen($filename, 'wb');
        //$contentsgz = gzcompress($contents);
        $contentsgz = gzencode($contents);
        fwrite($handle,$contentsgz);
        fclose($handle);    
    }
}

function endsWith($haystack, $needle)
{
    return $needle === "" || substr($haystack, -strlen($needle)) === $needle;
}

if ($handle = opendir('maps')) {
    while (false !== ($entry = readdir($handle))) {
        if(endsWith($entry,'.php')) {
            $mapid = substr($entry,0,-4);
        } else if(endsWith($entry,'.php.gz')) {
            $mapid = substr($entry,0,-7);
        }
        else {
            $mapid = NULL;
        }
        if($mapid) {
            //print "<a href='gz2gz.php?mapid=$mapid'>$mapid</a><br/>";
            gz2gz($mapid);
            print $mapid.'<br/>';
        }
    }
    closedir($handle);
}
?>
