<?php
    $id = $_GET['id'];
    if(ctype_alnum($id)) {
        $f = fopen('prepare/'.$id.'.txt','r');
        $s = fgets($f);
        fclose($f);
        print $s;
    }
?>
