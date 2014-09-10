#!/bin/bash
for pid in `ps aux | grep "python.*openbazaar_daemon.py" | grep -v grep | awk '{print $2}'`; do
  echo "Sending SIGTERM to ${pid}"
  kill ${pid}
  kill -9 ${pid}
done
