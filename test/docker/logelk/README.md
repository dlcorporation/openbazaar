## Build all docker images

Install [docker/docker](https://github.com/docker/docker) and [fig](https://github.com/docker/fig) first.

```
$ git clone https://github.com/OpenBazaar/OpenBazaar && cd OpenBazaar
$ cd test/docker/logelk
$ bash build.sh -a
```

## Run a node base on github offical repo master branch with a elk container.

```
$ sudo fig up -d
$ sudo fig logs
```

## Run a node base on your fork repo and branch with a elk container.

example git_url = https://github.com/y12studio/OpenBazaar and branch = hello_ob_fix

```
$ sudo fig stop
$ bash build.sh -k "https://github.com/y12studio/OpenBazaar hello_ob_fix"
$ sudo fig up -d
$ sudo fig logs
```

## Browser URL

OpenBazaar  http://DOCKER_HOST:8888/

Kibana http://DOCKER_HOST:9280/

ElasticSearch http://DOCKER_HOST:9200/

## screenshots

![ob-geoip-logstash](https://cloud.githubusercontent.com/assets/1840874/4216758/a0af7b28-38de-11e4-941c-ed4339a8552b.jpg)

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
