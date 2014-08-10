FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y python-dev python-pip g++ libjpeg-dev wget git

RUN wget https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py
RUN python get-pip.py
RUN pip install tornado pyzmq python-gnupg ecdsa twisted pymongo pyelliptic pycountry requests qrcode pillow

RUN git clone https://github.com/darkwallet/python-obelisk.git
RUN cd /python-obelisk && python setup.py install

ADD . /bazaar

EXPOSE 8888 8889 8890 12345

WORKDIR /bazaar

CMD bash run.sh && tail -f /bazaar/logs/production.log
