#!/bin/bash
set -o errexit
set -o pipefail

ERR=false

function python_check() {
    for file in $(find . -iname "*.py" -not -path "./env/*"|grep -v pybitmessage|grep -v pysqlcipher); do
        echo "Checking python source: $file"
        if ! flake8 --ignore=E501,F811,F821,F403 $file; then
            ERR=true
        fi
    done
}

function js_check() {
    for file in $(find . -not -path "./env/*" -and '(' -iname "*.js" ')'|grep -v pybitmessage|grep -v '.min.js'|grep -v bower_components|grep -v vendors); do
        echo "Checking JS source: $file"
        if ! jshint --config jshint.conf $file; then
            ERR=true
        fi
    done
}


function new_line_check() {
    for file in $(find . -not -path "./env/*" -and '(' -iname "*.py" -o -iname "*.html" -o -iname "*.js" ')'|grep -v pybitmessage|grep -v '.min.js'|grep -v bower_components); do
        if [ "$(tail -c1 $file)" != "" ]; then
            echo "$file: No new line at end of file"
            ERR=true
        fi
    done
}

case $1 in
python)
    python_check
    ;;
js)
    js_check
    ;;
*)
    python_check
    js_check
esac

if $ERR ; then
    exit 1
else
    exit 0
fi
