## Running it

install docker and fig first.

```
$ git clone https://github.com/OpenBazaar/OpenBazaar && cd OpenBazaar
$ cd test/docker/logelk
$ bash build.sh
$ sudo fig up -d
$ sudo fig logs
```

kibana port : http://DOCKER_HOST:9280
elasticsearch port : http://DOCKER_HOST9200

```
# find ob1 event
curl "http://DOCKER_HOST:9200/_search?q=host:ob1&pretty"

# find ob1 event with loglevel=ERROR
curl "http://DOCKER_HOST:9200/_search?q=host:ob1%20AND%20level:ERROR&pretty"

# find ob1 event with load/midterm > 1.0
curl "http://DOCKER_HOST:9200/_search?q=host:ob1%20AND%20collectd_type:load%20AND%20midterm:>1.0&pretty"
```

