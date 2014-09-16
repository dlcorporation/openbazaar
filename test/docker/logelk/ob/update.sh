#!/bin/bash
# ----------------------------------------
# OpenBazaar image update and build script
# ----------------------------------------

set -e

TARGET=/tmp/obgit
OB=/bazaar
if [ -d $TARGET ]; then
   echo Dir $TARGET Exists.
   rm -rf  $OB
   cp -R $TARGET $OB
   cd $OB/pysqlcipher && python setup.py install
   cd $OB && pip install -r requirements.txt
fi
