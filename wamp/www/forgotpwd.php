<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><title>Replay your GPS Tracks with REGEPE - Forgotten password</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<link type="text/css" rel="StyleSheet" href="styles/inputform.css" />
</head>
<body>
    <div id="wrapper">
<?php include('header.html'); ?>
        <div id="body">
            <h2>Forgot password?</h2>
            <form name="submitform" action="/cgi-bin/resendpwd.py" method="POST" enctype="multipart/form-data">
                <b>User/Email:</b> <input id="user_mail" name="user_mail" type="text"/><br/>
                <b>What is the name of the planet you live on? (Anti-Robot):</b> <input name="humaincheck" type="text"/><br/>
                <input name="Submit" value="Send me my password" type="submit"/>
            </form>
        </div>
        <div id="footer_push"></div>
    </div>
<?php include('footer.html'); ?>
</body>
</html>
<script src="javascript/xmlhttprequest.js" type="text/javascript"></script>
<script src="javascript/header.js" type="text/javascript"></script>
<script src="javascript/utils.js" type="text/javascript"></script>
