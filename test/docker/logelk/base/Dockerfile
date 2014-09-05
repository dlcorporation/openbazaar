FROM phusion/baseimage:0.9.13
MAINTAINER Y12STUDIO <y12studio@gmail.com>

ENV HOME /root
ENV LANG en_US.UTF-8
RUN update-locale
ENV DEBIAN_FRONTEND noninteractive
# Use the phusion baseimage's insecure key
RUN /usr/sbin/enable_insecure_key

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -yq curl wget git golang python
RUN apt-get install -yq openjdk-7-jre-headless

# 
# prebuild for OB
#
RUN apt-get -y update
RUN apt-get install -y python-pip build-essential python-zmq rng-tools
RUN apt-get install -y python-dev g++ libjpeg-dev zlib1g-dev sqlite3 openssl
RUN apt-get install -y alien libssl-dev wget
ADD requirements.txt /opt/ob/requirements.txt
RUN pip install -r /opt/ob/requirements.txt
#
# collectd conf and run script
#
RUN apt-get install -y collectd
ENV CTDCONF /opt/collectd/collectd.conf
ADD collectd.conf $CTDCONF
ENV CTD_RUN /etc/service/collectd/run
ADD collectd.sh $CTD_RUN
RUN chmod +x $CTD_RUN
#
# logstash 
#
# Download version 1.4.2 of logstash
RUN wget -qO- https://download.elasticsearch.org/logstash/logstash/logstash-1.4.2.tar.gz | tar xvz -C /tmp && \
    mv /tmp/logstash-* /opt/logstash

ENV LS_CONF /opt/logstash.conf
ENV LS_RUN /etc/service/logstash/run
ADD logstash.sh $LS_RUN
RUN chmod +x $LS_RUN

ENV JAVA_HOME  /usr/lib/jvm/java-7-openjdk-amd64/

CMD ["/sbin/my_init"]
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*