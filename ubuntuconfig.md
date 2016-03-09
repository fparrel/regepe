There is how to configure your test server on Ubuntu (tested with Lubuntu 15.10). Example if the git repository has been cloned into `/home/fred/regepe`

1. In `/etc/apache2/apache2.conf`, add
```html
<Directory /home/fred/regepe/lamp-test/>
  Options Indexes FollowSymLinks
  AllowOverride None
  Require all granted
</Directory>
```
2. Create `/etc/apache2/sites-enabled/regepe.conf`
```html
    <VirtualHost *:80>
    
	    ServerAdmin webmaster@localhost
    	DocumentRoot /home/fred/regepe/lamp-test/www
    
	    ErrorLog ${APACHE_LOG_DIR}/error.log
    	CustomLog ${APACHE_LOG_DIR}/access.log combined
    
	    <IfModule mod_alias.c>
    		<IfModule mod_cgi.c>
    			Define ENABLE_USR_LIB_CGI_BIN
    		</IfModule>
    
		    <IfModule mod_cgid.c>
    			Define ENABLE_USR_LIB_CGI_BIN
    		</IfModule>
    
		    <IfDefine ENABLE_USR_LIB_CGI_BIN>
    			ScriptAlias /cgi-bin/ /home/fred/regepe/lamp-test/cgi-bin/
    			<Directory "/home/fred/regepe/lamp-test/cgi-bin">
    				AllowOverride None
    				Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
    				Require all granted
    			</Directory>
    		</IfDefine>
    	</IfModule>
    
    </VirtualHost>
```

3. Then activate the host and restart apache:
```
sudo a2ensite regepe
sudo service apache2 restart
```

4. Put right permissions on `cgi-bin` folder
```shell
chmod +x `grep "#\!/usr/bin/python" lamp-test/cgi-bin/*.py -l`
```
