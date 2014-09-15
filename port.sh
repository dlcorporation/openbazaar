#!/bin/bash

PORT=`netstat -tap  --numeric-ports | grep python | grep \* | grep -v 12345 | awk ' {print $4}' | awk 'BEGIN{FS = "[:]"} {print $2}'`
echo "http://localhost:$PORT"
