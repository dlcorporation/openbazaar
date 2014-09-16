#!/bin/bash

PORT=`lsof -i -n -P -i4 | grep TCP | grep python | grep -v \> | grep -v 12345 | awk ' {print $9}' | awk 'BEGIN{FS = "[:]"} {print $2}'`
echo "http://localhost:$PORT"
