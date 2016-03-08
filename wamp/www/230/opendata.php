<?php
header('Content-type: text/plain');
$f = fopen("Log230.csv","r");
if(!$f) {
    print "Cannot open database";
}
else {
    $ips = Array();
    while(($line = fgets($f))!==false) {
        $contents=explode(',',$line,2);
        if(array_key_exists($contents[0],$ips)) {
            $ipanonymized = $ips[$contents[0]];
        }
        else {
            $ipanonymized = count($ips);
            $ips[$contents[0]] = $ipanonymized;
        }
        print $ipanonymized.','.$contents[1];
    }
    if (!feof($f)) {
        echo "Error while reading database";
    }
    fclose($f);
}
?>
