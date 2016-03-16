#!/usr/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
	exit -1
elif [[ $1 == --help ]]; then
	echo "Usage: $0 directory"
else
	for i in `find $1/ -name "*.py" -o -name "*.php" -o -name "*.js" -o -name "*.css" -o -name "*.html" -o -name "*.svg"`; do dos2unix $i; done
fi
