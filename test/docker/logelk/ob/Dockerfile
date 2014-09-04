FROM obtest/base
MAINTAINER Y12STUDIO <y12studio@gmail.com>

RUN apt-get -y update
RUN apt-get install -y python-pip build-essential python-zmq rng-tools
RUN apt-get install -y python-dev g++ libjpeg-dev zlib1g-dev sqlite3 openssl
RUN apt-get install -y alien libssl-dev wget

RUN git clone https://github.com/OpenBazaar/OpenBazaar /bazaar
RUN cd /bazaar && pip install -r requirements.txt &&\
    cd pysqlcipher && python setup.py install

ENV RUNSH_ARGS -q 8888 -p 12345

ADD lfs.json $LFSCONF

ENV OB_RUN /etc/service/openbazaar/run
ADD ob.sh $OB_RUN
RUN chmod +x $OB_RUN

CMD ["/sbin/my_init"]
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*