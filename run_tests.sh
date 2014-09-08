#!/bin/bash -ex

PYTHON="./env/bin/python"
if [ ! -x $PYTHON ]; then
  echo "No python executable found at ${PYTHON}"
  if type python2 &>/dev/null; then
    PYTHON=python2
  elif type python &>/dev/null; then
    PYTHON=python
  else
    echo "No python executable found anywhere"
    exit
  fi
fi

$PYTHON -m unittest discover -s . -p '*_test.py'
