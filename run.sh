#!/bin/bash
set -x

usage()
{
cat << EOF
usage: $0 options

This script starts up the OpenBazaar client and server.

OPTIONS:
  -h    Help information
  -o    Seed Mode
  -i    Server IP
  -p    Server Port
  -l    Log file
  -d    Development mode
  -n    Number of Dev nodes to start up
  -a    Bitmessage API username
  -b    Bitmessage API password
  -c    Bitmessage API port
  -u    Market ID
  -j    Disable upnp
  -s    List of additional seeds
EOF
}

PYTHON="./env/bin/python"
if [ ! -x $PYTHON ]; then
  echo "No python executable found at ${PYTHON}"
  if which python2 2>/dev/null; then
    PYTHON=python2
  elif which python 2>/dev/null; then
    PYTHON=python
  else
    echo "No python executable found anywhere"
    exit
  fi
fi

export DYLD_LIBRARY_PATH=$(brew --prefix openssl)/lib:${DYLD_LIBRARY_PATH}

# Default values
SERVER_PORT=12345
LOGDIR=logs
DBDIR=db
DBFILE=ob.db
DEVELOPMENT=0
SEED_URI='seed.openbazaar.org seed2.openbazaar.org'
LOG_FILE=production.log
DISABLE_UPNP=0

# CRITICAL   50
# ERROR      40
# WARNING    30
# INFO       20
# DEBUG      10
# NOTSET      0
LOG_LEVEL=10

NODES=3
BM_USERNAME=brian
BM_PASSWORD=P@ssw0rd
BM_PORT=8442

HTTP_IP=127.0.0.1
HTTP_PORT=8888

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

while getopts "hp:l:dn:a:b:c:u:oi:jk:q:s:" OPTION
do
     case ${OPTION} in
         h)
             usage
             exit 1
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
         o)
             SEED_MODE=1
             ;;
         i)
             SERVER_IP=$OPTARG
             ;;
         j)
             DISABLE_UPNP=1
             ;;
         k)
             HTTP_IP=$OPTARG
             ;;
         q)
             HTTP_PORT=$OPTARG
             ;;
         s)
             SEED_URI_ADD=$OPTARG
             ;;
         ?)
             usage
             exit
             ;;
     esac
done

SEED_URI+=" $SEED_URI_ADD"
HTTP_OPTS="-k $HTTP_IP -q $HTTP_PORT"

if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(wget -qO- icanhazip.com)
fi

if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi

if [ ! -d "$DBDIR" ]; then
  mkdir $DBDIR
fi

if [ "$DISABLE_UPNP" == 1 ]; then
    echo "Disabling upnp"
    DISABLE_UPNP="--disable_upnp"
else
    DISABLE_UPNP=""
fi

if [ "$SEED_MODE" == 1 ]; then
    echo "Seed Mode $SERVER_IP"

    if [ ! -f $DBDIR/$DBFILE ]; then
       echo "File $DBFILE does not exist. Running setup script."
       $PYTHON node/setup_db.py db/ob.db
       wait
    fi

    $PYTHON node/tornadoloop.py $SERVER_IP $HTTP_OPTS -p $SERVER_PORT $DISABLE_UPNP -s 1 --bmuser $BM_USERNAME --bmpass $BM_PASSWORD --bmport $BM_PORT -l $LOGDIR/production.log -u 1 --log_level $LOG_LEVEL &

elif [ "$DEVELOPMENT" == 0 ]; then
    echo "Production Mode"

    if [ ! -f $DBDIR/$DBFILE ]; then
       echo "File $DBFILE does not exist. Running setup script."
       export PYTHONPATH=$PYTHONPATH:`pwd`
       $PYTHON node/setup_db.py db/ob.db
       wait
    fi

	$PYTHON node/tornadoloop.py $SERVER_IP $HTTP_OPTS -p $SERVER_PORT $DISABLE_UPNP --bmuser $BM_USERNAME --bmpass $BM_PASSWORD --bmport $BM_PORT -S $SEED_URI -l $LOGDIR/production.log -u 1 --log_level $LOG_LEVEL &

else
	# Primary Market - No SEED_URI specified
	echo "Development Mode"

	if [ ! -f $DBDIR/ob-dev.db ]; then
       echo "File $DBFILE does not exist. Running setup script."
       export PYTHONPATH=$PYTHONPATH:`pwd`
       $PYTHON node/setup_db.py db/ob-dev.db
       wait
    fi

	$PYTHON node/tornadoloop.py 127.0.0.1 $HTTP_OPTS $DISABLE_UPNP --database db/ob-dev.db -s 1 --bmuser $BM_USERNAME -d --bmpass $BM_PASSWORD --bmport $BM_PORT -l $LOGDIR/development.log -u 1 --log_level $LOG_LEVEL &
    ((NODES=NODES+1))
    i=2
    while [[ $i -le $NODES ]]
    do
        sleep 2
        if [ ! -f db/ob-dev-$i.db ]; then
           echo "File db/ob-dev-$i.db does not exist. Running setup script."
           export PYTHONPATH=$PYTHONPATH:`pwd`
           $PYTHON node/setup_db.py db/ob-dev-$i.db
           wait
        fi
	    $PYTHON node/tornadoloop.py 127.0.0.$i $HTTP_OPTS $DISABLE_UPNP --database db/ob-dev-$i.db -d --bmuser $BM_USERNAME --bmpass $BM_PASSWORD --bmport $BM_PORT -S 127.0.0.1 -l $LOGDIR/development.log -u $i --log_level $LOG_LEVEL &
	    ((i=i+1))
    done
fi
