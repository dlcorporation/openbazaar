#!/bin/bash
for pid in `ps aux | grep "python.*openbazaar_daemon.py" | grep -v grep | awk '{print $2}'`; do
  echo "Sending SIGTERM to ${pid}"
  kill ${pid}
  sleep 5s
  if ps -p $pid > /dev/null
    then
    echo "Still running, sending SIGKILL to ${pid}"
    kill -9 ${pid}
  fi
done
