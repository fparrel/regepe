Here are the modifications to be done in `httpd.conf` for testing on WAMP. Example if you cloned repository on `D:`

Replace
```html
    DocumentRoot "D:/wamp/www"
    <Directory "D:/wamp/www">
```
by
```html
    DocumentRoot "D:/regepe/wamp/www"
    <Directory "D:/regepe/wamp/www">
```

Replace
```
    ScriptAlias /cgi-bin/ "D:/wamp/cgi-bin/"
```
by
```
    ScriptAlias /cgi-bin/ "D:/regepe/wamp/cgi-bin/"
```

Replace
```html
    <Directory "D:/wamp/cgi-bin">
```
by
```html
    <Directory "D:/regepe/wamp/cgi-bin">
```
