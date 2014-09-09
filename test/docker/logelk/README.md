## Build Docker Image

Install [docker/docker](https://github.com/docker/docker) and [fig](https://github.com/docker/fig) first.

```
$ git clone https://github.com/OpenBazaar/OpenBazaar && cd OpenBazaar
$ cd test/docker/logelk
$ bash build.sh -a
```

## Run a node with a elk container.

```
$ sudo fig up -d
$ sudo fig logs
```

OB node http://DOCKER_HOST:8888/

ElasticSearch/Logstash/Kibana http://DOCKER_HOST:9280/

## ELK example

elasticsearch : http://DOCKER_HOST:9200/_search?pretty

```
find host:ob event

http://DOCKER_HOST:9200/_search?q=host:ob&pretty

find host:ob event with loglevel=ERROR

http://DOCKER_HOST:9200/_search?q=host:ob AND level:ERROR&pretty

find host:ob event with load/midterm > 1.0

http://DOCKER_HOST:9200/_search?q=host:ob AND collectd_type:load AND midterm:>1.0&pretty

```