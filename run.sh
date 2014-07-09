#!/bin/bash

usage()
{
cat << EOF
usage: $0 options

This script starts up the OpenBazaar client and server.

OPTIONS:
  -h    Help information
  -s    Seed URI
  -p    Server Port
  -l    Log file
  -d    Development mode
  -n    Number of Dev nodes to start up
  -a    Bitmessage API username
  -b    Bitmessage API password
  -c    Bitmessage API port
  -u    Market ID
EOF
}

if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi

# Default values
SERVER_IP=$(wget -qO- icanhazip.com)
SERVER_PORT=12345
LOGDIR=logs
DEVELOPMENT=0
SEED_URI=tcp://seed.openbazaar.org:12345
LOG_FILE=production.log
NODES=3
BM_USERNAME=username
BM_PASSWORD=password
BM_PORT=8442

# Tor Information
# - If you enable Tor here you will be operating a hidden
#   service behind your Tor proxy (notional)
TOR_ENABLE=0
TOR_CONTROL_PORT=9051
TOR_SERVER_PORT=9050
TOR_COOKIE_AUTHN=1
TOR_HASHED_CONTROL_PASSWORD=
TOR_PROXY_IP=127.0.0.1
TOR_PROXY_PORT=7000

while getopts "hs:p:l:dn:a:b:c:u:" OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         s)
             SEED_URI=$OPTARG
             ;;
         p)
             SERVER_PORT=$OPTARG
             ;;
         l)
             LOG_FILE=$OPTARG
             ;;
         d)
             DEVELOPMENT=1
             ;;
         n)
             NODES=$OPTARG
             ;;
         a)
             BM_USERNAME=$OPTARG
             ;;
         b)
             BM_PASSWORD=$OPTARG
             ;;
         c)
             BM_PORT=$OPTARG
             ;;
         u)
             MARKET_ID=$OPTARG
             ;;
         ?)
             usage
             exit
             ;;
     esac
done

if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi


if [ $DEVELOPMENT == 0 ]; then
	$PYTHON node/tornadoloop.py $SERVER_IP -s $SEED_URI -p $SERVER_PORT --bmuser $BM_USERNAME --bmpass $BM_PASSWORD --bmport $BM_PORT -l $LOGDIR/production.log -u 1 &
else

	# Primary Market - No SEED_URI specified
	$PYTHON node/tornadoloop.py 127.0.0.1 --bmuser $BM_USERNAME --bmpass $BM_PASSWORD --bmport $BM_PORT -l $LOGDIR/development.log -u 1 &
    ((NODES=NODES+1))
    i=2
    while [[ $i -le $NODES ]]
    do
        sleep 2
	    $PYTHON node/tornadoloop.py 127.0.0.$i -s tcp://127.0.0.1:$SERVER_PORT --bmuser $BM_USERNAME --bmpass $BM_PASSWORD --bmport $BM_PORT -l $LOGDIR/development.log -u $i &
	    ((i=i+1))
    done



fi
