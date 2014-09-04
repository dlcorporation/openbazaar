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
RUN apt-get install -y collectd

# build logstash-forwarder
ENV LFSCONF /opt/logstash-forwarder/lfs.json
RUN mkdir -p /opt/logstash-forwarder/bin/
RUN git clone git://github.com/elasticsearch/logstash-forwarder.git /tmp/logstash-forwarder
RUN cd /tmp/logstash-forwarder && go build && \
    mv logstash-forwarder /opt/logstash-forwarder/bin/

ENV CTDCONF /opt/collectd/collectd.conf
ADD collectd.conf $CTDCONF
ENV CTD_RUN /etc/service/collectd/run
ADD collectd.sh $CTD_RUN
RUN chmod +x $CTD_RUN

ENV LFS_RUN /etc/service/lfs/run
ADD lfs.sh $LFS_RUN
RUN chmod +x $LFS_RUN

CMD ["/sbin/my_init"]
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*