FROM ubuntu:14.04

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y python-pip build-essential python-zmq rng-tools
RUN apt-get install -y python-dev g++ libjpeg-dev zlib1g-dev sqlite3 openssl
RUN apt-get install -y alien libssl-dev wget

ADD . /bazaar
RUN cd /bazaar && pip install -r requirements.txt &&\
    cd pysqlcipher && python setup.py install

ENV RUNSH_ARGS -q 8888 -p 12345

WORKDIR /bazaar
ENV LOG_PATH /bazaar/logs/production.log
# touch log file before bash run.sh to keep tail -f work
RUN mkdir -p /bazaar/logs && touch $LOG_PATH
CMD IP=$(/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}') && \
    bash run.sh --disable-open-browser -k $IP $RUNSH_ARGS && tail -f $LOG_PATH
# clean tmp file
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
