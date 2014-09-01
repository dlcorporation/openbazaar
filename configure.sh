#!/bin/bash

#
# configure.sh - Setup your OpenBazaar development environment in one step.
#
# If you are a Ubuntu or MacOSX user, you can try executing this script
# and you already checked out the OpenBazaar sourcecode from the git repository
# you can try configuring/installing OpenBazaar by simply executing this script
# instead of following the build instructions in the OpenBazaar Wiki 
# https://github.com/OpenBazaar/OpenBazaar/wiki/Build-Instructions
# 
# This script will only get better as its tested on more development environments
# if you can't modify it to make it better, please open an issue with a full
# error report at https://github.com/OpenBazaar/OpenBazaar/issues/new
#
#

function installMac {
  #is brew installed?
  which -s brew
  if [[ $? != 0 ]] ; then
    echo "installing brew..."
    ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
  else
    echo "updating, upgrading, checking brew..."
    brew update
    brew upgrade
    brew doctor
    brew prune
  fi

  #is python installed?
  which -s python
  if [[ $? != 0 ]] ; then
    brew install python
  fi

  #pre-requisites
  brew install wget gpg zmq
  brew install openssl
  brew link openssl --force
  sudo easy_install pip

  #python libraries
  sudo pip install -r --upgrade requirements.txt

  #install sqlite3 from brew and manually link it as brew won't link this for us.
  brew install sqlite3
  SQLITE3_LAST_VERSION=`ls -1t /usr/local/Cellar/sqlite | head -1`
  ln -s /usr/local/Cellar/sqlite/${SQLITE3_LAST_VERSION}/bin/sqlite3 /usr/local/bin/sqlite3

  doneMessage
}

function doneMessage {
echo ""
echo "OpenBazaar configuration finished."
echo "type './run.sh; tail -f logs/production.log' to start your OpenBazaar servent instance and monitor logging output."
echo ""
echo ""
echo ""
echo ""
}


function installUbuntu {
  sudo apt-get update
  sudo apt-get install python-pip build-essential python-zmq tor privoxy rng-tools
  sudo apt-get install python-dev python-pip g++ libjpeg-dev zlib1g-dev sqlite3 openssl
  sudo pip install -r requirements.txt
  pushd pysqlcipher
  sudo python setup.py install
  popd

  doneMessage
}

function installArch {
  sudo pacman -Sy
  sudo pacman -S base-devel python2-pip python2-pyzmq tor privoxy rng-tools
  sudo pacman -S python2 gcc libjpeg zlib sqlite3 openssl
  sudo pip2 install -r requirements.txt
  pushd pysqlcipher
  sudo python2.7 setup.py install
  popd

  doneMessage
}

if [[ $OSTYPE == darwin* ]] ; then
  installMac
elif [[ $OSTYPE == linux-gnu ]]; then
  if [ -f /etc/arch-release ]; then
    installArch
  else
    installUbuntu
  fi
fi
