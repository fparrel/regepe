<html><head><title>Test photos</title></head>
<body>
<p>Page contents...</p>
<form onsubmit="postImage();" method="post" action="submitphoto.php" rel="async">
<input type="text" name="contents"/>
<input type="submit"/>
</form>
</body></html>
<script src="javascript/xmlhttprequest.js" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[

function postImage() {
    var client = new XMLHttpRequest();
    client.open('POST','submitphoto.php');
    client.send();
    
}

//]]>
</script>
