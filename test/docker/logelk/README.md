## Running it

install docker and fig first.

run a nodex2/seedx1/elkx1 testing network.

```
$ git clone https://github.com/OpenBazaar/OpenBazaar && cd OpenBazaar
$ cd test/docker/logelk
$ bash build.sh
$ sudo fig up -d
$ sudo fig logs
```

kibana : http://DOCKER_HOST:9280

elasticsearch : http://DOCKER_HOST9200

elasticsearch example.

# find host:ob1 event
http://DOCKER_HOST:9200/_search?q=host:ob1&pretty

# find host:ob2 event with loglevel=ERROR
http://DOCKER_HOST:9200/_search?q=host:ob2 AND level:ERROR&pretty

# find host:ob1 event with load/midterm > 1.0
http://DOCKER_HOST:9200/_search?q=host:ob1 AND collectd_type:load AND midterm:>1.0&pretty"
```

