<html>
<head></head><body>
Results: <br/>
<?php 
$result = file_get_contents('http://localhost/cgi-bin/dorebuildinv.py');
print $result;
?>
<br/>End
</body></html>
