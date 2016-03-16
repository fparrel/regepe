Here are the modifications to be done in `httpd.conf` for testing on WAMP. Example if you cloned repository on `D:`

* Replace
```html
DocumentRoot "D:/wamp/www"
<Directory "D:/wamp/www">
```
by
```html
DocumentRoot "D:/regepe/wamp-test/www"
<Directory "D:/regepe/wamp-test/www">
```

* Replace
```
ScriptAlias /cgi-bin/ "D:/wamp/cgi-bin/"
```
by
```
ScriptAlias /cgi-bin/ "D:/regepe/wamp-test/cgi-bin/"
```

* Replace
```html
<Directory "D:/wamp/cgi-bin">
```
by
```html
<Directory "D:/regepe/wamp-test/cgi-bin">
```

Depending on your version of Windows and WAMP, you may have to set rights (I use `chmod` on cygwin)
