export PYTHONPATH=$PYTHONPATH:$PWD

# Location of log directory
LOGDIR=logs

killall -9 python
killall -9 python2

if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi

# Running on the server because.
#$PYTHON ident/identity.py &
touch $LOGDIR/development.log

#$PYTHON node/tornadoloop.py $STOREFILE $MY_MARKET_IP -s $SEED_URI -p $MY_MARKET_PORT -l $LOGDIR/development.log &

$PYTHON node/tornadoloop.py ppl/novaprospekt 127.0.0.1  -p 12345  -l $LOGDIR/development.log &
sleep 1
$PYTHON node/tornadoloop.py ppl/genjix 127.0.0.2 -s tcp://127.0.0.1:12345   -p 12345  -l $LOGDIR/development.log  &
sleep 1
$PYTHON node/tornadoloop.py ppl/default 127.0.0.3 -s tcp://127.0.0.1:12345 -p 12345  -l $LOGDIR/development.log  &
sleep 1
$PYTHON node/tornadoloop.py ppl/s_tec 127.0.0.4 -s tcp://127.0.0.1:12345 -p 12345  -l $LOGDIR/development.log  &
