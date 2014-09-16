FROM obtest/base
MAINTAINER Y12STUDIO <y12studio@gmail.com>

# 
# package for OB
#
RUN apt-get -y update
RUN apt-get install -y build-essential python-zmq rng-tools
RUN apt-get install -y python-dev g++ libjpeg-dev zlib1g-dev sqlite3 openssl
RUN apt-get install -y alien libssl-dev wget lintian libjs-jquery
#
# install pip from source. 
# workaround https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1363642
# and https://github.com/OpenBazaar/OpenBazaar/commit/224f12a371d4eaa36ee7955930c60704e31d61d9
#
RUN curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python2.7
#
# install requirements
#
ENV OB /bazaar
RUN git clone -v --depth 1 --branch master https://github.com/OpenBazaar/OpenBazaar $OB    
RUN cd $OB/pysqlcipher && python setup.py install
RUN cd $OB && pip install -r requirements.txt

ENV RUNSH_ARGS -q 8888 -p 12345

ADD logstash.conf $LS_CONF

ENV OB_RUN /etc/service/openbazaar/run
ADD ob.sh $OB_RUN
RUN chmod +x $OB_RUN
#
# update source after image build.
#
ADD update.sh /opt/update.sh
RUN chmod +x /opt/update.sh

ADD ob.pattern /opt/logstash/patterns/ob

CMD ["/sbin/my_init"]
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*