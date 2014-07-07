#!/bin/bash -ex

python -m unittest discover -s . -p '*_test.py'
