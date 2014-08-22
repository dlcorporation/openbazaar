#!/bin/bash

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
  brew install wget gpg
  brew install openssl
  brew link openssl --force
  sudo easy_install pip

  #python libraries
  pip install -r --upgrade requirements.txt

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
  sudo apt-get install python-pip
  sudo apt-get install python-dev python-pip g++ libjpeg-dev zlib1g-dev sqlite3 openssl
  sudo pip install -r requirements.txt

  doneMessage
}

if [[ $OSTYPE == darwin* ]] ; then
  installMac
elif [[ $OSTYPE == linux-gnu ]]; then
  installUbuntu
fi

