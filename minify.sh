#!/usr/bin/bash

for i in `ls lamp-prod/www/javascript/*.js | grep -v "\.min\.js"`
do
echo "Processing $i"
java -jar external_tools/yuicompressor-2.4.8.jar $i -o `echo $i | sed 's/\.js/\.min\.js/'`
#cat `echo $i | sed 's/\.min\.js/\.js/'` | work/JSMin-master/jsmin.exe > $i
done

for i in `ls lamp-prod/www/fr/javascript/*.js | grep -v "\.min\.js"`
do
echo "Processing $i"
java -jar external_tools/yuicompressor-2.4.8.jar $i -o `echo $i | sed 's/\.js/\.min\.js/'`
#cat `echo $i | sed 's/\.min\.js/\.js/'` | work/JSMin-master/jsmin.exe > $i
done
