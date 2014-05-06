# Market Info
MY_MARKET_IP=127.0.0.1
MY_MARKET_PORT=12345

# Specify a seed URI or you will be put into demo mode
SEED_URI=tcp://seed.openbazaar.org:12345

# Run in local test mode if not production
MODE=production

# Store config file
STOREFILE=ppl/default

# Location of log directory
LOGDIR=logs

if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi


if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi
touch $LOGDIR/server.log

if [ $MODE == production ]; then
	
	$PYTHON node/tornadoloop.py $STOREFILE $MY_MARKET_IP $SEED_URI > $LOGDIR//server.log &
	
else

	# Primary Market - No SEED_URI specified 
	$PYTHON node/tornadoloop.py $STOREFILE $MY_MARKET_IP > $LOGDIR/demo_peer1.log &
	
	# Demo Peer Market
	sleep 2
    STOREFILE2=ppl/s_tec
	touch $LOGDIR/demo_peer2.log
	$PYTHON node/tornadoloop.py $STOREFILE2 127.0.0.2 tcp://127.0.0.1:$MY_MARKET_PORT > $LOGDIR//demo_peer2.log &

	sleep 2
    STOREFILE2=ppl/genjix
	touch $LOGDIR/demo_peer3.log
	$PYTHON node/tornadoloop.py $STOREFILE2 127.0.0.3 tcp://127.0.0.1:$MY_MARKET_PORT > $LOGDIR//demo_peer3.log &


fi
