<?php

// Redirect already identified user
if(isset($_COOKIE["USER_ID"]))
{
    header("Location: index.php");
}
else {
    
    // Formulaire visible par défaut
    $show_form = true;
    
    // Une fois le formulaire envoyé
    if(isset($_POST["Register"])) {
    
        // Check inputs
        if(!@ereg("^[A-Za-z0-9]{4,}$", $_POST["pwd1"])) {
            $message = "You password must be at least 4 chars long";
        }
        elseif($_POST["pwd1"] != $_POST["pwd2"]) {
            $message = "The two password differ";
        }
        elseif(!@ereg("^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]{2,}[.][a-zA-Z]{2,4}$",$_POST["mail"])) {
            $message = "Incorrect email adress";
        }
        elseif( strtolower($_POST["humaincheck"]) != "earth" ) {
            $message = "Anti robot check error";
        }
        else {
            // Connect to DB
            mysql_connect("localhost", "root", "");
            mysql_select_db("test");
            
            // Check email unicity
            $result = mysql_query("SELECT 1 FROM USERS WHERE EMAIL='".$_POST["mail"]."'");
            
            // Error handling
            if(!$result) {
                $message = "Database access error";
            }
            else {
                // If data found
                if(mysql_num_rows($result) > 0) {
                    $message = "This email has already been registered";
                }
                else {
                    // Generated activation key
                    $activation_key = sprintf("%6x",rand(0,0xFFFFFF));
                    
                    // Create account
                    $result = mysql_query("INSERT INTO USERS(EMAIL,PASSWORD,REGISTER_DATE,ACTIVE,ACTIVATION_KEY)
                    VALUES('".$_POST["mail"]."','".$_POST["pwd1"]."','".date('Y-m-d')."','0','".$activation_key."')");
                    
                    // Error handling
                    if(!$result)
                    {
                        $message = "Database access error";
                    }
                    else {
                    
                        // Build activation mail
                        $mail_subject = "User account activation";
                        
                        $mail_message = "To validate your account please follow this link :\n";
                        $mail_message .= "http://" . $_SERVER["SERVER_NAME"];
                        $mail_message .= "/activateaccount.php?user_id=" . mysql_insert_id();
                        $mail_message .= "&activation_key=" . $activation_key;
                        
                        // Send mail
                        if(!@mail($_POST["mail"], $mail_subject, $mail_message)) {
                            $message = "Error while sending mail<!-- ".$mail_message."-->";
                        }
                        else {
                            $message = "Your account has been created. Now please check your mail to activate it";
                            $show_form = false;
                        }
                    }
                }
            }
            
            //mysql_close();
        }
        
    }
    
}

?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><title>Register</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf8">
<!--<link type="text/css" rel="StyleSheet" href="styles/register.css" />-->
</head>
<body>
<h1>Register</h1>
<?php if(isset($message)) { ?>
<p><?php echo $message; ?></p>
<?php }
if ($show_form) { ?>
<form action="register.php" method="POST">
    <b>Mail:</b> <input name="mail" type="text"/><br/>
    <b>Password:</b> <input name="pwd1" type="text"/><br/>
    <b>Confirm password:</b> <input name="pwd2" type="text"/><br/>
    <b>What is the name of the planet you live on? (Anti-Robot):</b> <input name="humaincheck" type="text"/><br/>
    <input type="submit" name="Register" value="Register"/>
</form>
<?php } ?>
</body>
</html>
