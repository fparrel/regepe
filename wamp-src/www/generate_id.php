<?php
if(!function_exists('uniqid'))
{
function uniqid() {
    # Cette fonction renvoie un identifiant unique
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
echo uniqid();
?>