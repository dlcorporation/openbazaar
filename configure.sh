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

set -x

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

  #is gpg/sqlite3/python/wget installed?
  for dep in gpg sqlite3 python wget
  do
    which -s $dep
    if [[ $? != 0 ]] ; then
      brew install $dep
    fi
  done

  #more brew prerequisites
  brew install openssl zmq

  #python prerequisites
  #python may be owned by root, or it may be owned by the user
  PYTHON_OWNER=$(stat -n -f %u `which python`)
  if [ "$PYTHON_OWNER" == "0" ]; then
    #root owns python
    EASY_INSTALL="sudo easy_install"
    PIP="sudo pip"
  else
    EASY_INSTALL="easy_install"
    PIP="pip"
  fi

  #setup pip
  which -s pip
  if [[ $? != 0 ]] ; then
    $EASY_INSTALL pip
  fi

  #setup virtualenv
  which -s virtualenv
  if [[ $? != 0 ]] ; then
    $PIP install virtualenv
  fi

  #create a virtualenv for OpenBazaar
  if [ ! -d "./env" ]; then
    virtualenv env
  fi

  # set compile flags for brew's openssl instead of using brew link --force
  export CFLAGS="-I$(brew --prefix openssl)/include"
  export LDFLAGS="-L$(brew --prefix openssl)/lib"

  #install python deps inside our virtualenv
  ./env/bin/pip install -r requirements.txt
  ./env/bin/pip install ./pysqlcipher

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
  sudo apt-get upgrade
  sudo apt-get install python-pip build-essential python-zmq rng-tools
  sudo apt-get install python-dev python-pip g++ libjpeg-dev zlib1g-dev sqlite3 openssl
  sudo apt-get install alien libssl-dev python-virtualenv

  if [ ! -d "./env" ]; then
    virtualenv env
  fi
  ./env/bin/pip install -r requirements.txt
  ./env/bin/pip install ./pysqlcipher

  doneMessage
}

function installArch {
  sudo pacman -Sy
  sudo pacman -S base-devel python2 python2-pip python2-pyzmq rng-tools
  sudo pacman -S gcc libjpeg zlib sqlite3 openssl
  sudo pip2 install -r requirements.txt
  pushd pysqlcipher
  sudo python2.7 setup.py install
  popd
  doneMessage
}

if [[ $OSTYPE == darwin* ]] ; then
  installMac
elif [[ $OSTYPE == linux-gnu -o $OSTYPE == linux-gnueabihf]]; then
  if [ -f /etc/arch-release ]; then
    installArch
  else
    installUbuntu
  fi
fi
