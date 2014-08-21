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
  brew install autoenv
  brew install openssl
  brew link openssl --force
  sudo easy_install pip

  #virtualenv
  sudo pip install virtualenv
  sudo pip install virtualenvwrapper
  mkdir ~/.virtualenvs
 
  #python libraries
  pip install -r --upgrade requirements.txt

  #install sqlite3 from brew and manually link it as brew won't link this for us.
  brew install sqlite3
  SQLITE3_LAST_VERSION=`ls -1t /usr/local/Cellar/sqlite | head -1`
  echo ln -s /usr/local/Cellar/sqlite/${SQLITE3_LAST_VERSION}/bin/sqlite3 /usr/local/bin/sqlite3

  clear

  echo "To finish the OpenBazaar installation copy the following 2 lines towards the end of your ~/.bash_profile"
  echo ""
  echo "export WORKON_HOME=~/.virtualenvs" 
  echo "source /usr/local/bin/virtualenvwrapper.sh"
  echo ""
  echo "After you're done type the following command"
  echo ""
  echo "mkvirtualenv open_bazaar"
  echo ""
  echo ""
  echo "type './run.sh' to start your OpenBazaar servent instance."
}


function installUbuntu {
  print "installUbuntu not implemented."
}

if [[ $OSTYPE == darwin* ]] ; then
  installMac
elif [[ $OSTYPE == linux-gnu ]]; then
  installUbuntu
fi


