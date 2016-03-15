<?xml version="1.0" encoding="UTF-8"?>
<upload_res>
<?php
print_r($_SERVER);
print_r($_REQUEST);
//print_r($_FILES);
//print_r($_POST);
print_r($HTTP_RAW_POST_DATA);

$user = $_REQUEST['user'];
$sess = $_REQUEST['sess'];
$filecontents = $HTTP_RAW_POST_DATA;

?>
</upload_res>
