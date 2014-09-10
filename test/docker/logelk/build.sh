#!/bin/bash
# ------------------------------------------------------------------
# [Author] OpenBazaar ELK log utility image build script
# ------------------------------------------------------------------

SUBJECT=some-unique-id
VERSION=0.1.0
USAGE="Usage: build.sh -hvoeba args"

# --- Option processing --------------------------------------------
if [ $# == 0 ] ; then
    echo $USAGE
    exit 1;
fi

while getopts ":vhoeba" optname; do
  case "$optname" in
    "v")
      echo "Version $VERSION"
      exit 0;
      ;;
    "o")
      echo "build the openbazaar image"
      sudo docker build -t obtest/ob --rm=true --no-cache=true ob
      exit 0;
      ;;
    "e")
      echo "build the elk image"
      sudo docker build -t obtest/elk --rm=true --no-cache=true elk
      exit 0;
      ;;
    "b")
      echo "build the base image"
      sudo docker build -t obtest/base --rm=true --no-cache=true base
      exit 0;
      ;;
    "a")
      echo "build all image"
      sudo docker build -t obtest/base base
      sudo docker build -t obtest/elk elk
      sudo docker build -t obtest/ob ob
      exit 0;
      ;;
    "h")
      echo $USAGE
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

shift $(($OPTIND - 1))

# -----------------------------------------------------------------

LOCK_FILE=/tmp/${SUBJECT}.lock

if [ -f "$LOCK_FILE" ]; then
echo "Script is already running"
exit
fi

# -----------------------------------------------------------------
trap "rm -f $LOCK_FILE" EXIT
touch $LOCK_FILE 