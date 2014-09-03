#!/bin/bash
set -o errexit
set -o pipefail

ERR=false

for file in $(find . -iname "*.py" -not -path "./env/*"|grep -v pybitmessage|grep -v pysqlcipher); do
    echo "Checking python source: $file"
    if ! flake8 --ignore=E501,E127,F811,F821,F403 $file; then
        ERR=true
    fi
done

for file in $(find . -not -path "./env/*" -and '(' -iname "*.js" ')'|grep -v pybitmessage|grep -v '.min.js'|grep -v bower_components); do
    echo "Checking JS source: $file"
    if ! jshint $file; then
        ERR=true
    fi
done

for file in $(find . -not -path "./env/*" -and '(' -iname "*.py" -o -iname "*.html" -o -iname "*.js" ')'|grep -v pybitmessage|grep -v '.min.js'|grep -v bower_components); do
    if [ "$(tail -c1 $file)" != "" ]; then
        echo "$file: No new line at end of file"
        ERR=true
    fi
done

if $ERR ; then
    exit 1
else
    exit 0
fi
