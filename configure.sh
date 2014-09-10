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

#exit on error
set -e

function command_exists {
  #this should be a very portable way of checking if something is on the path
  #usage: "if command_exists foo; then echo it exists; fi"
  type "$1" &> /dev/null
}

function brewDoctor {
    if ! brew doctor; then
      echo ""
      echo "'brew doctor' did not exit cleanly! This may be okay. Read above."
      echo ""
      read -p "Press [Enter] to continue anyway or [ctrl + c] to exit and do what the doctor says..."
    fi
}

function brewUpgrade {
    if ! brew upgrade; then
      echo ""
      echo "There were errors when attempting to 'brew upgrade' and there could be issues with the installation of OpenBazaar."
      echo ""
      read -p "Press [Enter] to continue anyway or [ctrl + c] to exit and fix those errors."
    fi
}

function installMac {
  #print commands (useful for debugging)
  #set -x  #disabled because the echos and stdout are verbose enough to see progress

  #install brew if it is not installed, otherwise upgrade it
  if ! command_exists brew ; then
    echo "installing brew..."
    ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
  else
    echo "updating, upgrading, checking brew..."
    brew update
    brewDoctor
    brewUpgrade 
    brew prune
  fi
  
  #install gpg/sqlite3/python/wget if they aren't installed
  for dep in gpg sqlite3 python wget
  do
    if ! command_exists $dep ; then
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

  #install pip if it is not installed
  if ! command_exists pip ; then
    $EASY_INSTALL pip
  fi

  #install python's virtualenv if it is not installed
  if ! command_exists virtualenv ; then
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
  ./env/bin/pip install ./pysqlcipher
  ./env/bin/pip install -r requirements.txt

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
  #print commands
  set -x

  sudo apt-get update
  sudo apt-get upgrade
  sudo apt-get install python-pip build-essential python-zmq rng-tools
  sudo apt-get install python-dev python-pip g++ libjpeg-dev zlib1g-dev sqlite3 openssl
  sudo apt-get install alien libssl-dev python-virtualenv lintian libjs-jquery

  if [ ! -d "./env" ]; then
    virtualenv env
  fi

  ./env/bin/pip install ./pysqlcipher
  ./env/bin/pip install -r requirements.txt

  doneMessage
}

function installArch {
  #print commands
  set -x

  sudo pacman -Sy
  sudo pacman -S base-devel python2 python2-pip python2-pyzmq rng-tools
  sudo pacman -S gcc libjpeg zlib sqlite3 openssl
  pushd pysqlcipher
  sudo python2.7 setup.py install
  popd
  sudo pip2 install -r requirements.txt
  doneMessage
}

if [[ $OSTYPE == darwin* ]] ; then
  installMac
elif [[ $OSTYPE == linux-gnu || $OSTYPE == linux-gnueabihf ]]; then
  if [ -f /etc/arch-release ]; then
    installArch
  else
    installUbuntu
  fi
fi
