<html>
<head>
<title><?php 
$dir = getcwd();
$subdir = "";
if(array_key_exists ("subdir",$_GET)) {
    $subdir = urldecode($_GET["subdir"]);
    $dir = $dir."/".$subdir;
}
echo $dir; ?></title>
<body>
<h1><?php echo $dir; ?></h1>
<?php

function showvideo($file) {
    $mime = "video/quicktime";
    $w = 1280/2;
    $h = 720/2;
    echo '<video width="'.$w.'" height="'.$h.'" controls>
                <source src="'.$file.'" type="video/mp4">
                <object data="'.$file.'" width="'.$w.'" height="'.$h.'">
                    <embed src="'.$file.'" width="'.$w.'" height="'.$h.'">
                </object> 
            </video>';
}

function shownef($file) {
    $mime = "image/x-raw";
    $w=640;
    $h=480;
    echo '<object data="'.$file.'" width="'.$w.'" height="'.$h.'">
                <embed src="'.$file.'" width="'.$w.'" height="'.$h.'">
            </object>';
}

function endsWith( $str, $sub ) {
    return ( substr( $str, strlen( $str ) - strlen( $sub ) ) === $sub );
}


function listsubdirs($dir) {
    if ($dh = opendir($dir)) {
        while (($file = readdir($dh)) !== false) {
            if(($file!=".")&&($file!="..")&&(is_dir($dir."/".$file))) {
                echo "<a href='index.php?subdir=".urlencode($file)."'>".$file."</a> ".countdir($dir."/".$file)." elements<br/>";
            }
        }
    }
    else {
        echo "Erreur!";
    }
}

function countdir($dir) {
    $cptr=0;
    if ($dh = opendir($dir)) {
        while (($file = readdir($dh)) !== false) {
            if(($file!=".")&&($file!="..")) {
                $cptr++;
            }
        }
        closedir($dh);
    }
    else {
        return "Erreur!";
    }
    return $cptr;
}

function listphotosvideos($dir,$subdir) {
    if ($dh = opendir($dir)) {
        while (($file = readdir($dh)) !== false) {
            echo "<p>".$file."<br/>";
            if(endsWith($file,".JPG")) {
                $size = getimagesize($dir."/".$file);
                $w = round($size[0] / 8);
                $h = round($size[0] / 8);
                echo "<img src='".$subdir."/".$file."' height='".$h."' width='".$w."'/>\n";
            }
            else if(endsWith($file,".MOV")) {
                showvideo($subdir."/".$file);
            }
            else if(endsWith($file,".NEF")) {
                shownef($subdir."/".$file);
            }
            echo "</p>";
        }
        closedir($dh);
    }
    else {
        echo "Erreur!";
    }
}

if(endsWith($dir,"fotos")) {
    listsubdirs($dir);
}
else {
    listphotosvideos($dir,$subdir);
}

?>
</body>
</html>
