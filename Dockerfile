FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y python-pip build-essential python-zmq tor privoxy rng-tools
RUN apt-get install -y python-dev python-pip g++ libjpeg-dev zlib1g-dev sqlite3 openssl
RUN apt-get install -y alien libssl-dev wget
ADD . /bazaar
RUN cd /bazaar && pip install -r requirements.txt
RUN cd /bazaar/pysqlcipher && python setup.py install
#
# workround https://github.com/OpenBazaar/OpenBazaar/pull/302/
#
RUN sed -i "s/http_ip = '127.0.0.1'/http_ip = '0.0.0.0'/g" /bazaar/node/tornadoloop.py

EXPOSE 8888 8889 8890 12345

WORKDIR /bazaar
ENV LOG_PATH /bazaar/logs/production.log
# touch log file before bash run.sh to keep tail -f work
RUN mkdir -p /bazaar/logs && touch $LOG_PATH
CMD bash run.sh && tail -f $LOG_PATH
