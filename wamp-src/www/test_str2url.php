<?php
/*
$a = "àáâãäåòóôõöøèéêëçìíîïùúûüÿñ";
for($i=0;$i<strlen($a);$i++) print '\\'.ord($a[$i]);
print urlencode($a);
'%E0%E1%E2%E3%E4%E5%F2%F3%F4%F5%F6%F8%E8%E9%EA%EB%E7%EC%ED%EE%EF%F9%FA%FB%FC%FF%F1';
*/
$s = '(Déjà  la (test)';

function str2urlutf8($input) {
    /*
    $accents =   'ÀÁÂÃÄÅàáâãäåÒÓÔÕÖØòóôõöøÈÉÊËèéêëÇçÌÍÎÏìíîïÙÚÛÜùúûüÿÑñÆæ¼½';
    $converted = 'AAAAAAaaaaaaOOOOOOooooooEEEEeeeeCcIIIIiiiiUUUUuuuuyNn----';
    for($i=0;$i<strlen($accents);$i++) {
        $utf8 = utf8_encode($accents[$i]);
        $tohex = '';
        for($j=0;$j<strlen($utf8);$j++) {
            $tohex = $tohex.'\x'.strtoupper(dechex (ord($utf8[$j])));
        }
        print '<br/>$s = str_replace("'.$tohex.'","'.$converted[$i].'",$s);';
    }*/
    $s = strtr($input," -'/:()[]&","---------");
    $s = str_replace("\xC3\x80","A",$s);
    $s = str_replace("\xC3\x81","A",$s);
    $s = str_replace("\xC3\x82","A",$s);
    $s = str_replace("\xC3\x83","A",$s);
    $s = str_replace("\xC3\x84","A",$s);
    $s = str_replace("\xC3\x85","A",$s);
    $s = str_replace("\xC3\xA0","a",$s);
    $s = str_replace("\xC3\xA1","a",$s);
    $s = str_replace("\xC3\xA2","a",$s);
    $s = str_replace("\xC3\xA3","a",$s);
    $s = str_replace("\xC3\xA4","a",$s);
    $s = str_replace("\xC3\xA5","a",$s);
    $s = str_replace("\xC3\x92","O",$s);
    $s = str_replace("\xC3\x93","O",$s);
    $s = str_replace("\xC3\x94","O",$s);
    $s = str_replace("\xC3\x95","O",$s);
    $s = str_replace("\xC3\x96","O",$s);
    $s = str_replace("\xC3\x98","O",$s);
    $s = str_replace("\xC3\xB2","o",$s);
    $s = str_replace("\xC3\xB3","o",$s);
    $s = str_replace("\xC3\xB4","o",$s);
    $s = str_replace("\xC3\xB5","o",$s);
    $s = str_replace("\xC3\xB6","o",$s);
    $s = str_replace("\xC3\xB8","o",$s);
    $s = str_replace("\xC3\x88","E",$s);
    $s = str_replace("\xC3\x89","E",$s);
    $s = str_replace("\xC3\x8A","E",$s);
    $s = str_replace("\xC3\x8B","E",$s);
    $s = str_replace("\xC3\xA8","e",$s);
    $s = str_replace("\xC3\xA9","e",$s);
    $s = str_replace("\xC3\xAA","e",$s);
    $s = str_replace("\xC3\xAB","e",$s);
    $s = str_replace("\xC3\x87","C",$s);
    $s = str_replace("\xC3\xA7","c",$s);
    $s = str_replace("\xC3\x8C","I",$s);
    $s = str_replace("\xC3\x8D","I",$s);
    $s = str_replace("\xC3\x8E","I",$s);
    $s = str_replace("\xC3\x8F","I",$s);
    $s = str_replace("\xC3\xAC","i",$s);
    $s = str_replace("\xC3\xAD","i",$s);
    $s = str_replace("\xC3\xAE","i",$s);
    $s = str_replace("\xC3\xAF","i",$s);
    $s = str_replace("\xC3\x99","U",$s);
    $s = str_replace("\xC3\x9A","U",$s);
    $s = str_replace("\xC3\x9B","U",$s);
    $s = str_replace("\xC3\x9C","U",$s);
    $s = str_replace("\xC3\xB9","u",$s);
    $s = str_replace("\xC3\xBA","u",$s);
    $s = str_replace("\xC3\xBB","u",$s);
    $s = str_replace("\xC3\xBC","u",$s);
    $s = str_replace("\xC3\xBF","y",$s);
    $s = str_replace("\xC3\x91","N",$s);
    $s = str_replace("\xC3\xB1","n",$s);
    $s = str_replace("\xC3\x86","AE",$s);
    $s = str_replace("\xC3\xA6","ae",$s);
    $s = str_replace("\xC2\xBC","OE",$s);
    $s = str_replace("\xC2\xBD","oe",$s);
    $s = strtolower($s);
    $s = preg_replace('/[^a-z0-9\-]/','',$s);
    $s = preg_replace('/\-+/','-',$s);
    if ($s[0]=='-') {
        $s = substr($s,1);
    }
    if ($s[strlen($s)-1]=='-') {
        $s = substr($s,0,-1);
    }
    return $s;
}

function str2url($s) {
    $out = strtr($s, "ÀÁÂÃÄÅàáâãäåÒÓÔÕÖØòóôõöøÈÉÊËèéêëÇçÌÍÎÏìíîïÙÚÛÜùúûüÿÑñ -'/:()", "AAAAAAaaaaaaOOOOOOooooooEEEEeeeeCcIIIIiiiiUUUUuuuuyNn-------");
    $out = str_replace('Æ','AE',$out);
    $out = str_replace('æ','ae',$out);
    $out = str_replace('¼','OE',$out);
    $out = str_replace('½','oe',$out);
    $out = strtolower($out);
    $out = preg_replace('/[^a-z0-9\-]/','',$out);
    $out = preg_replace('/\-+/','-',$out);
    if ($out[0]=='-') {
        $out = substr($out,1);
    }
    if ($out[strlen($out)-1]=='-') {
        $out = substr($out,0,-1);
    }
    return $out;
}

print urlencode('abc-def');
print $s." = ".str2urlutf8(utf8_encode($s));

/*
$s = strtr($s,
"\224\225\226\227\228\229\242\243\244\245\246\248\232\233\234\235\231\236\237\238\239\249\250\251\252\255\241",
"aaaaaaooooooeeeeciiiiuuuuyn");
*/



?>
