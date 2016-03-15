<pre>
<?php
    print phpversion();
    $filename = 'hw.txt.gz';
    $handle = fopen($filename, 'rb');
    $contents = gzdecode(fread($handle, filesize($filename)));
    fclose($handle);
    print $contents;
?>
</pre>
