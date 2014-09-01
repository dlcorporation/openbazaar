#!/bin/bash
set -o errexit
set -o pipefail

# find . -iname "*.py"|xargs flake8 --ignore=E501,E127,F811,F821,F403 --exclude=*pybitmessage*,*pysqlcipher*

ERR=0

for file in $(find . -iname "*.py" -o -iname "*.html" -o -iname "*.js"|grep -v pybitmessage|grep -v '.min.js'|grep -v bower_components); do
    if [ "$(tail -c1 $file)" != "" ]; then
        echo "$file: No new line at end of file"
        ERR=1
    fi
done

if [ $ERR ]; then
    exit 1
fi
