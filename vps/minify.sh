#!/usr/bin/env bash
for i in `ls static/javascript/*.js | grep -v "\.min\.js"`; do
	MINIFIED=`echo $i | sed 's/\.js/\.min\.js/'`
	if [ ! -f $MINIFIED ] || [ `stat -c %Y $i` -gt `stat -c %Y $MINIFIED` ]; then
		echo "Processing $i"
		java -jar ../external_tools/yuicompressor-2.4.8.jar $i -o $MINIFIED
	fi
done

