#!/bin/bash
sudo docker build -t=obtest/base base
sudo docker build -t=obtest/elk elk
sudo docker build -t=obtest/ob ob