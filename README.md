# regepe
Source code of regepe.com

## Quickstart
```
git clone https://github.com/fparrel/regepe
cd regepe
docker build -t regepe .
# Prod
#docker run -d -p 80:80 regepe
# Dev
mkdir -p $(pwd)/vps/config/
cp config-default.json $(pwd)/vps/config/config.json
cp keysnpwds-default.json $(pwd)/vps/config/keysnpwds.json
docker run -p 8080:8080 -v $(pwd):/regepe --name regepe_dev regepe
firefox localhost:8080
```

## What is regepe.com
It's a website allowing to analyze and keep the results of GPS tracking for outdoor sports.

## In what way is regepe.com different from strava, movescount, etc...?
I made this site specialized for the unusual sports I practice: snowkiting, kitesurfing and skitouring.
So it features:
* Polar, and VMG (Velocity Made Good) analysis
* Max speed analysis on 50, 100, 200 and 500m, 1 nautical mile, 2, 5, 10, 60 seconds
* Max ascent speed on 50, 100, 200 vertical meters, and on 1, 10, 30, 60, 120 minutes
* IGN Maps (French Institut National Geographic), that are much more detailled than Google Maps

## What is regepe.com business model?
None, it costs me money (but not a lot)

## What are the future features to implement?
* Better smartphone display for showmap page (responsive web design)
* Fix for a bug that I found with VMG and vmax
* "Share" button
* Allow keeping logging on several devices
* Fix a strange issue we have with uswgi

## How is the code organized?
### New VPS (Virtual Private Server) version
Cf. quickstart for testing
* `vps/*.py` contains all the code
* `vps/regepe_flask_server.py` is the program entry point. Either via uwsgi on production or launching `python regepe_flask_server.py` for debugging
* `vps/config` contains configuration data such as keys and domain name. Obviously not commited to Git
* `vps/data` contains all the data. Not commited to Git
* `vps/dem` contains Digital Elevation Model static data for the Alps. Not commited to Git given the huge amount of data. Data has been taken from NASA website
* `vps/logs` contains the logs generated by Regepe. Not commited to Git
* `vps/static` contains static data: javascript code, images, CSS
* `vps/templates` contains .html and .js templates that are processed by Jinja2 before being sent to client
* `vps/translations` contains Babel translation strings (currently French and Spanish)
* `vps/uploads` contains a backup of uploaded files (for debugging). Not commited to Git
* `vps/admin_*.py` are the administrations tools for the website
* `vps/babel.cfg`, `vps/translations_*.sh` are the script used for Babel translations
* `vps/minify.sh` is the minify script used for putting code on production
* `vps_tools` contains some tools usefull for debugging

### Legacy WAMP Version
The testing can be done even with WAMP+Python on Windows or with Apache+PHP+Python on Ubuntu (LAMP)  
`wamp-src` contains the WAMP version of the code with keys and password hidden  
`wamp-lamp` contains the WAMP version of the code with real keys and passwords for testing on localhost  
`wamp-src/www` contains .php and static html/css/js/png files  
`wamp-src/cgi-bin` contains cgi executables running on Windows' python2.7  
In `wamp-src/www`, `${GeoPortalApiKey}`, `${GMapsApiKey}` and `${GMapsApiKey2}` are meant to be replaced by actual value of API Key (by script `realign.ph`)  
`translate.py` is used to generate french version of the website (on `wamp-src/www/fr`). Translation data is on `translations.txt`  
`lamp-test` contains the LAMP version of the code for testing on localhost  
`lamp-prod` contains the LAMP version of the code for putting on production  
`lamp-test`, `lamp-prod` and `wamp/www/fr` are on `.gitignore` since they are generated from `wamp`  
`realign.py` can be used to realign bettwen `wamp`, `lamp-test` and `lamp-prod` and to have the list of modified files that have to be loaded on production  
`wampconfig.md` contains the modifications to be done on WAMP configuration to serve on localhost from your git clone directory  
`ubuntuconfig.md` contains the modifications to be done on Apache configuration to serve on localhost from your git clone directory (tested on Lubuntu 15.10)  
`minify.sh` is used to minify .js files in `lamp-prod`  

## What technologies/libraries/services are used?
### New VPS Version
nginx uwsgi Python Flask Javascript BerkelyDB D3.js flotcharts JQuery Geoportail GoogleMaps HTML CSS Jinga2 Babel
### Legacy WAMP Version
CGI Python PHP Javascript BerkelyDB D3.js flotcharts JQuery Geoportail GoogleMaps HTML CSS

## Why is there a cgi-bin version of this site?
CGI was the only solution to use python on OVH's cheap shared hosting. Other solutions whould have need a VM rental, was too expensive. But since OVH proposes a cheap VPS solution, website has been migrated from WAMP+cgi-bin Python to nginx uswgi python flask

