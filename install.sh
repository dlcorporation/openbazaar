#!/bin/bash

function installMac {
  #is brew installed?
  if [[ $(which -s brew) != 0 ]] ; then
    ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
  fi

  #is python installed?
  if [[ $(which -s python) != 0 ]] ; then
    brew install python
  fi

  #pre-requisites
  brew update
  brew upgrade
  brew doctor
  brew install wget gpg
  brew install autoenv
  sudo easy_install pip

  #virtualenv
  sudo pip install virtualenv
  sudo pip install virtualenvwrapper
  mkdir ~/.virtualenvs
  echo -n "export WORKON_HOME=~/.virtualenvs" >> ~/.bash_profile
  echo -n "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bash_profile
  source ~/.bash_profile
  mkvirtualenv open_bazaar
  
  #python libraries
  pip install -r requirements.txt

  #install sqlite3 from brew and manually link it as brew won't link this for us.
  brew install sqlite3
  SQLITE3_LAST_VERSION=`ls -1t /usr/local/Cellar/sqlite | head -1`
  echo ln -s /usr/local/Cellar/sqlite/${SQLITE3_LAST_VERSION}/bin/sqlite3 /usr/local/bin/sqlite3

  print "Everything should be there now. type ./run.sh to start your OpenBazaar servent."
}


if [[ $OSTYPE == darwin* ]] ; then
  installMac
elif [[ $OSTYPE == linux-gnu ]]; then
  installUbuntu
fi


