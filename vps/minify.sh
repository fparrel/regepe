#!/usr/bin/env bash
for i in `ls static/javascript/*.js | grep -v "\.min\.js"`; do
	echo "Processing $i"
	java -jar ../external_tools/yuicompressor-2.4.8.jar $i -o `echo $i | sed 's/\.js/\.min\.js/'`
done

