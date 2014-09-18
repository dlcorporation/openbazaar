#!/bin/bash
# ------------------------------------------------------------------
# OpenBazaar ELK log utility image build script
# ------------------------------------------------------------------

set -e

SUBJECT=logelk-build-image-id
VERSION=0.1.0
USAGE="Usage: build.sh -vhoebapk:c: args"
DOCKER='sudo docker'
TARGET=/tmp/obgit
OBIMG=obtest/ob

# --- Option processing --------------------------------------------
if [ $# == 0 ] ; then
    echo "$USAGE"
    exit 1;
fi

function updateimg {
  $DOCKER run -t -v $TARGET:$TARGET "$OBIMG:gmaster" /opt/update.sh
  CID=$($DOCKER ps -q -l)
  $DOCKER commit "$CID" "$OBIMG:$1" > /dev/null
  $DOCKER tag "$OBIMG:$1" "$OBIMG:latest"
  echo [DOCKER] tag "$OBIMG:$1" "$OBIMG:latest"
  $DOCKER rm "$CID"
} 

while getopts ":vhoebapk:c:" optname; do
  case "$optname" in
    "v")
      echo "Version $VERSION"
      exit 0;
      ;;
    "o")
      echo "build the openbazaar image"
      $DOCKER build -t "$OBIMG":gmaster --rm=true ob
      $DOCKER tag "$OBIMG":gmaster "$OBIMG":latest
      exit 0;
      ;;
    "k")
      #  bash build.sh -k "https://github.com/y12studio/OpenBazaar master"
      echo build the openbazaar image "$OPTARG"
      ADDR=($OPTARG)
      GURL=${ADDR[0]}
      GBRANCH=${ADDR[1]}
      echo "git url = " $GURL
      echo "git_branch = " $GBRANCH
      if [ -d $TARGET ]; then 
         rm -rf $TARGET
      fi
      git clone --depth 1 -b $GBRANCH $GURL $TARGET
      updateimg fbranch
      exit 0;
      ;;
    "c")
      #  bash build.sh -c "/home/ob/git/OpenBazaar"
      echo build the local dev branch openbazaar image "$OPTARG"
      if [ -d $TARGET ]; then 
         rm -rf $TARGET
      fi
      /bin/cp -R "$OPTARG" $TARGET
      updateimg dev
      exit 0;
      ;;
    "e")
      echo "build the elk image"
      $DOCKER build -t obtest/elk --rm=true elk
      exit 0;
      ;;
    "b")
      echo "build the base image"
      $DOCKER build -t obtest/base --rm=true base
      exit 0;
      ;;
    "p")
      echo "build the python rest testing image"
      $DOCKER build -t obtest/pyrest --rm=true --no-cache=true pyrest
      exit 0;
      ;;
    "a")
      echo "build all image"
      $DOCKER build -t obtest/base base
      $DOCKER build -t obtest/elk elk
      $DOCKER build -t obtest/ob ob
      exit 0;
      ;;
    "h")
      echo "$USAGE"
      exit 0;
      ;;
    "?")
      echo "Unknown option $OPTARG"
      exit 0;
      ;;
    ":")
      echo "No argument value for option $OPTARG"
      exit 0;
      ;;
    *)
      echo "Unknown error while processing options"
      exit 0;
      ;;
  esac
done

shift "$($OPTIND - 1)"

# -----------------------------------------------------------------

LOCK_FILE=/tmp/${SUBJECT}.lock

if [ -f "$LOCK_FILE" ]; then
echo "Script is already running"
exit
fi

# -----------------------------------------------------------------
trap 'rm -f $LOCK_FILE' EXIT
touch $LOCK_FILE 