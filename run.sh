#!/bin/bash

# Market Info
MY_MARKET_IP=$(wget -qO- icanhazip.com)
MY_MARKET_PORT=12345

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

# Specify a seed URI or you will be put into demo mode
#SEED_URI=tcp://205.186.154.163:12345
SEED_URI=tcp://seed.openbazaar.org:12345

# Check for argument to turn on production
DEVMODE=development
MODE=${1:-$DEVMODE}
if [ $MODE == "production" ]; then
    MODE=production
else
    MODE=development
fi

# Location of log directory
LOGDIR=logs

if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi

# Bitmessage User Info
BM_USERNAME=username
BM_PASSWORD=password
BM_PORT=8442

if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi

if [ $MODE == production ]; then

  # Identity server is coming soon
  #$PYTHON ident/identity.py &
	$PYTHON node/tornadoloop.py $MY_MARKET_IP -s $SEED_URI -p $MY_MARKET_PORT --bmuser $BM_USERNAME --bmpass $BM_PASSWORD --bmport $BM_PORT -l $LOGDIR/production.log -u 1 &

else

	# Primary Market - No SEED_URI specified
	$PYTHON node/tornadoloop.py 127.0.0.1 -l $LOGDIR/development.log -u 2 &

	# Demo Peer Market
	sleep 2
	$PYTHON node/tornadoloop.py 127.0.0.2 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 3 &

	sleep 2
	$PYTHON node/tornadoloop.py 127.0.0.3 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 4 &

#	sleep 2
#	$PYTHON node/tornadoloop.py 127.0.0.4 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 5 &
#
#	sleep 2
#	$PYTHON node/tornadoloop.py 127.0.0.5 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 6 &
#
#	sleep 2
#	$PYTHON node/tornadoloop.py 127.0.0.6 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 7 &
#
#	sleep 2
#	$PYTHON node/tornadoloop.py 127.0.0.7 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 8 &
#
#	sleep 2
#	$PYTHON node/tornadoloop.py 127.0.0.8 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 9 &
#
#	sleep 2
#	$PYTHON node/tornadoloop.py 127.0.0.9 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/development.log -u 10 &

fi
