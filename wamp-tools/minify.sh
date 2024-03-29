#!/usr/bin/env bash
if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
	exit -1
elif [[ $1 == --help ]]; then
	echo "Usage: $0 directory"
else
	for i in `ls $1/www/javascript/*.js | grep -v "\.min\.js"`; do
		echo "Processing $i"
		java -jar external_tools/yuicompressor-2.4.8.jar $i -o `echo $i | sed 's/\.js/\.min\.js/'`
	done
	for i in `ls $1/www/fr/javascript/*.js | grep -v "\.min\.js"`; do
		echo "Processing $i"
		java -jar external_tools/yuicompressor-2.4.8.jar $i -o `echo $i | sed 's/\.js/\.min\.js/'`
	done
fi
