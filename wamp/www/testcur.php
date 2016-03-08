<pre>
<?php
$content = "J ai depense 123 AUD hier soir, et il y avait 10 personnes donc ca fait AUD10,2 par personne, AUD test 4AUD";
$cur='AUD';
//$pat = '/[\d]+,?[\d]*\s?[A-Z][A-Z][A-Z]/';
$pat = '/([\d]+,?[\d]*\s?[A-Z][A-Z][A-Z])|([A-Z][A-Z][A-Z]\s?[\d]+,?[\d]*)/';
preg_match_all($pat,$content,$matches,PREG_OFFSET_CAPTURE);
$post_id = 123;
$prevstartpos=0;
$out='';
$i=0;
print $content."<br/>";
foreach($matches[0] as $match) {
    $startpos = $match[1];
    
    print "prevstartpos=".$prevstartpos."<br/>startpos=".$startpos."<br/>len=".($startpos-$prevstartpos+strlen($match[0]))."<br/>";
    
    $out = $out.substr($content,$prevstartpos,$startpos-$prevstartpos+strlen($match[0])).'<span id="localcurrency'. $post_id.'-'.$i . '"/>';
    
    $prevstartpos = $startpos+strlen($match[0]);
    $i++;
}
print $out;
//print_r($matches[0]);
?>
</pre>
