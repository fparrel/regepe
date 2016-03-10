<?php

// Redirige l'utilisateur s'il est deja identifie
if(isset($_COOKIE["USER_ID"]))
{
    //header("Location: index.php");
    $message = "Cookie set";
}
else {
    
    // Check input parameters
    if(!@ereg("^[0-9]+$", $_GET["user_id"]) || !@ereg("^[a-f0-9]{6}$", strtolower($_GET["activation_key"])))
    {
        //header("Location: index.php");
        $message = "Bad input parameters";
    }
    else {
        
        // Connect to DB
        mysql_connect("localhost", "root", "");
        mysql_select_db("test");
        
        // Activate user
        $result = mysql_query("UPDATE USERS SET ACTIVE='1' WHERE USER_ID='".$_GET["user_id"]."' AND ACTIVATION_KEY='".$_GET["activation_key"]."'");
        
        // Si une erreur survient
        if(!$result) {
            $message = "Database access error";
        }
        else {
            $message = "Account activated";                    
        }
        
        //mysql_close();
        
    }
    
}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Activate account</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body>
<p><?php echo $message; ?></p>
</body>
</html>
