<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><title>Replay your GPS Tracks with REGEPE - Register</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<link type="text/css" rel="StyleSheet" href="styles/header.css" />
<link type="text/css" rel="StyleSheet" href="styles/inputform.css" />
</head>
<body>
    <div id="wrapper">
<?php include('header.html'); ?>
        <div id="body">
            <h2>Register</h2>
            <form action="/cgi-bin/doregister.py" method="POST">
                <b>Mail:</b> <input name="mail" type="text" id="mail"/><br/>
                <b>User:</b> <input name="user" type="text" id="user" /> <input type="button" value="Generate from mail" onclick="onGenerateUserClick();"/><br/>
                <b>Password:</b> <input name="pwd1" type="password"/><br/>
                <b>Confirm password:</b> <input name="pwd2" type="password"/><br/>
                <b>What is the name of the planet you live on? (Anti-Robot):</b> <input name="humaincheck" type="text"/><br/>
                <input type="submit" name="Register" value="Register"/>
            </form>
        </div>
        <div id="footer_push"></div>
    </div>
<?php include('footer.html'); ?>
</body>
</html>
<script type="text/javascript" src="javascript/xmlhttprequest.js"></script>
<script type="text/javascript" src="javascript/header.js"></script>
<script type="text/javascript" src="javascript/db.js"></script>
<script type="text/javascript">
//<![CDATA[

function generateUser(email) {
    var left;
    var i = email.indexOf('@');
    if (i>18) {
        i = 18;
    }
    if (i==-1) {
        left = email;
    }
    else {
        left = email.substring(0,i);
    }
    return left.replace(/[^a-z0-9_]/,'_');
}

function onGenerateUserClick() {
    document.getElementById("user").value = generateUser(document.getElementById("mail").value);
}

//]]>
</script>
