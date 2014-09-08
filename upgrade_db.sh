#!/bin/bash

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

# Execute from root dir as: bash upgrade_db.sh <db_path>
for file in db/migrations/*
do
  $PYTHON $file $1 upgrade
done
