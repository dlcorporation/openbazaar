# Market Info
MY_MARKET_IP=$(wget -qO- icanhazip.com)
MY_MARKET_PORT=12345

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


if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi

if [ $MODE == production ]; then

  # Identity server is coming soon
  #$PYTHON ident/identity.py &
	$PYTHON node/tornadoloop.py $MY_MARKET_IP -s $SEED_URI -p $MY_MARKET_PORT -l $LOGDIR/node.log -u 1 &

else

	# Primary Market - No SEED_URI specified
	$PYTHON node/tornadoloop.py 127.0.0.1 -l $LOGDIR/demo_node1.log -u 2 &

	# Demo Peer Market
	sleep 4
	$PYTHON node/tornadoloop.py 127.0.0.2 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/demo_node1.log -u 3 &

	sleep 2
	$PYTHON node/tornadoloop.py 127.0.0.3 -s tcp://127.0.0.1:$MY_MARKET_PORT -l $LOGDIR/demo_node1.log -u 4 &

fi
