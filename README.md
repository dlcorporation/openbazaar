#OpenBazaar

OpenBazaar is a decentralized marketplace proof of concept. It is based off of the POC code by the darkmarket team and protected by the GPL.

Currently soliciting feedback on the project. http://www.reddit.com/r/Bitcoin/comments/23y80c/solicitation_of_darkmarketbased_alternative/
Also official site will be at http://openbazaar.org

`pip install pyzmq`
`pip install tornado`
`pip install pyelliptic`
`pip install pymongo`

1. Install python-obelisk
2. git clone https://github.com/darkwallet/python-obelisk
3. python setup.py install


## MongoDB
- Install MongoDB with OpenSSL
- Configure parameters for connecting 
- Start MongoDB 
- Create database named openbazaar
`use openbazaar`
`db.createCollection("orders")`

## OSX Users

For OSX there is a CLANG error when installing pyzmq but you can use the following command to ignore warnings:

`sudo ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future easy_install pyzmq`

## Issues with ./run_dev.sh
If you're getting errors saying `ZMQError: Can't assign requested address` then you probably need to bring up some loopback adapters for those 
IPs higher than 127.0.0.1.

sudo ifconfig lo0 alias 127.0.0.2 up
sudo ifconfig lo0 alias 127.0.0.3 up
sudo ifconfig lo0 alias 127.0.0.4 up

## List of libraries used
1. https://github.com/warner/python-ecdsa
2. https://github.com/darkwallet/python-obelisk

###Vagrant VM

# Quick dev setup:
- Install Vagrant (http://www.vagrantup.com/downloads.html)
- `git clone https://github.com/darkwallet/darkmarket.git && cd darkmarket`
- `vagrant up && vagrant ssh`
- `cd /vagrant && ./run_dev.sh`
- Open http://localhost:8888


## Screenshot

![Screen 1](http://i.imgur.com/PaemnhJ.png)
=======


