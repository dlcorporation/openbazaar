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
    for file in $(find . -not -path "./env/*" -and '(' -iname "*.html" -o -iname "*.js" ')'|grep -v pybitmessage|grep -v '.min.js'|grep -v bower_components); do
        if [ "$(tail -c1 $file)" != "" ]; then
            echo "$file: No new line at end of file"
            ERR=true
        fi
    done
}

function execute_bit_check() {
    echo "Test for non-executable files with execute bit set..."
    for file in $(find . -executable -and '('\
        -name "LICENSE"\
        -name "README"\
        -o -name "*.cpp"\
        -o -name "*.css"\
        -o -name "*.eot"\
        -o -name "*.html"\
        -o -name "*.js"\
        -o -name "*.json"\
        -o -name "*.less"\
        -o -name "*.map"\
        -o -name "*.md"\
        -o -name "*.png"\
        -o -name "*.scss"\
        -o -name "*.svg"\
        -o -name "*.txt"\
        -o -name "*.ttf"\
        -o -name "*.woff"\
        -o -name "*.yml" ')' ); do
        echo "$file: Execute bit set; please remove."
        ERR=true
    done
    echo "Done."
}

case $1 in
python)
    python_check
    ;;
js)
    js_check
    ;;
exc)
    execute_bit_check
    ;;
*)
    python_check
    js_check
    execute_bit_check
esac

if $ERR ; then
    exit 1
else
    exit 0
fi
