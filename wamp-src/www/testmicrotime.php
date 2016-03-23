<?php
    # Cette fonction renvoie un identifiant unique
    $micro = substr (microtime(), 2, 6) ;
    echo $micro.'<br/>';
    $concat = time() . $micro ;
    echo $concat.'<br/>';
    $dec_1 = substr ($concat, 0, 8) ;
    echo $dec_1.'<br/>';
    $dec_2 = substr ($concat, 8, 8) ;
    echo $dec_2.'<br/>';
    $hex_1 = dechex ($dec_1) ;
    echo $hex_1.'<br/>';
    $hex_2 = dechex ($dec_2) ;
    echo $hex_2.'<br/>';
    $id = $hex_1 . $hex_2 ;
    echo $id;
    return $id ;

?>
