Here are the modifications to be done in `httpd.conf` for testing on WAMP. Example if you cloned repository on `D:`

Replace
    DocumentRoot "D:/wamp/www"
    <Directory "D:/wamp/www">
by
    DocumentRoot "D:/regepe/wamp/www"
    <Directory "D:/regepe/wamp/www">

Replace
    ScriptAlias /cgi-bin/ "D:/wamp/cgi-bin/"
by
    ScriptAlias /cgi-bin/ "D:/regepe/wamp/cgi-bin/"

Replace
    <Directory "D:/wamp/cgi-bin">
by
    <Directory "D:/regepe/wamp/cgi-bin">
