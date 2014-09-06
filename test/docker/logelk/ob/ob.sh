#!/bin/bash
LOG_PATH=/bazaar/logs/production.log
# touch log file before bash run.sh to keep tail -f work
mkdir -p /bazaar/logs && touch $LOG_PATH
IP=$(/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')
cd /bazaar && ./run.sh -j --disable-open-browser -k $IP $RUNSH_ARGS && tail -f $LOG_PATH
