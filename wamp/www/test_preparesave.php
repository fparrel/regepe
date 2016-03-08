<?php

if(!function_exists('uniqid'))
{
    function uniqid() {
        $micro = substr (microtime(), 2, 6) ;
        $concat = time() . $micro ;
        $dec_1 = substr ($concat, 0, 8) ;
        $dec_2 = substr ($concat, 8, 8) ;
        $hex_1 = dechex ($dec_1) ;
        $hex_2 = dechex ($dec_2) ;
        $id = $hex_1 . $hex_2 ;
        return $id ;
    }
}

    if(array_key_exists('id',$_GET)) {
        $id = $_GET['id'];
    }
    else {
        $id = uniqid();
    }
    if(ctype_alnum($id)) {
        $s = 'ptlist='.$_GET['ptlist'].'&names='.$_GET['names']."\n".$_SERVER['REMOTE_ADDR'];
        $f = fopen('prepare/'.$id.'.txt','w');
        fwrite($f,$s);
        fclose($f);
        print $id;
    }
?>
