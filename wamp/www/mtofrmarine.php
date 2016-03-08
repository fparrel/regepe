<html>
<head></head><body>
Results: <br/>
<?php 
$result = file_get_contents('http://localhost/cgi-bin/mtofrmarine.py');
print $result;
?>
<br/>End
</body></html>
