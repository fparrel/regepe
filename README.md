# regepe
Source code of regepe.com

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
None, it costs me money (but not a lot!)

## Why does this site use cgi-bin?
CGI was the only solution to use python on OVH's cheap shared hosting. Other solutions whould have need a VM rental, too expensive. I'm waiting for OVH to propose a cheap Docker hosting solution.

## What are the future features to implement?
* Better smartphone display (responsive web design)
* Fix for a bug that I found with VMG and vmax
* "Share" button
* Allow keeping logging on several devices

## How is the code organized?
The testing can be done even with WAMP+Python on Windows or with Apache+PHP+Python on Ubuntu (LAMP)  
`wamp` contains the WAMP version of the code for testing on localhost  
`wamp/www` contains .php and static html/css/js/png files  
`wamp/cgi-bin` contains cgi executables running on Windows' python2.7  
In `wamp/www`, `${GeoPortalApiKey}`, `${GMapsApiKey}` and `${GMapsApiKey2}` have to be replaced by actual value of API Key  
`translate.py` is used to generate french version of the website (on `wamp/www/fr`)  
`lamp-test` contains the LAMP version of the code for testing on localhost  
`lamp-prod` contains the LAMP version of the code for putting on production  
`lamp-test`, `lamp-prod` and `wamp/www/fr` are on `.gitignore` since they are generated from `wamp`  
`realign.py` can be used to realign bettwen `wamp`, `lamp-test` and `lamp-prod` and to have the list of modified files that have to be loaded on production  
`wampconfig.md` contains the modifications to be done on WAMP configuration to serve on localhost from your git clone directory  
`ubuntuconfig.md` contains the modifications to be done on Apache configuration to serve on localhost from your git clone directory (tested on Lubuntu 15.10)  
