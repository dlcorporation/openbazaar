#!/bin/bash
for pid in `pgrep -f "python.*tornadoloop.py"`; do
  echo "Sending SIGTERM to ${pid}"
  kill ${pid}
  kill -9 ${pid}
done
