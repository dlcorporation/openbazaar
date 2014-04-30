#OpenBazaar

OpenBazaar is a decentralized marketplace proof of concept. It is based off of the POC code by the darkmarket team and protected by the GPL.

Currently soliciting feedback on the project. http://www.reddit.com/r/Bitcoin/comments/23y80c/solicitation_of_darkmarketbased_alternative/
Also official site will be at http://openbazaar.org

## Features (Notional)
- Full market editor for management of items catalog
- Order management system
- Escrow-based transactions
- Arbiter management
- Private messaging
- Identity/Reputation system

## Dependencies
- https://github.com/warner/python-ecdsa
- https://github.com/darkwallet/python-obelisk
- MongoDB

`pip install pyzmq`
`pip install tornado`
`pip install pyelliptic`
`pip install pymongo`

1. Install python-obelisk
2. git clone https://github.com/darkwallet/python-obelisk
3. python setup.py install


### MongoDB

OpenBazaar now uses MongoDB as the backend for storing persistent data. At the moment only orders are being tracked there, but this will be fleshed out ongoing. You will need to set up a MongoDB instance on your machine outside of this software and create a database called 'openbazaar'. There is no authentication or encryption configured, but I will be adding in support for this soon.

- Install MongoDB with OpenSSL
- Start MongoDB 
- Create database named openbazaar

From command line:
`mongo`
`use openbazaar`


###Vagrant VM

#### Quick dev setup:
- Install Vagrant (http://www.vagrantup.com/downloads.html)
- `git clone https://github.com/OpenBazaar/OpenBazaar.git && cd OpenBazaar`
- `vagrant up && vagrant ssh`
- `cd /vagrant && ./run_dev.sh`
- Open http://localhost:8888


### OSX Users

For OSX there is a CLANG error when installing pyzmq but you can use the following command to ignore warnings:

`sudo ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future easy_install pyzmq`

### Issues with ./run_dev.sh
If you're getting errors saying `ZMQError: Can't assign requested address` then you probably need to bring up some loopback adapters for those 
IPs higher than 127.0.0.1.

sudo ifconfig lo0 alias 127.0.0.2 up
sudo ifconfig lo0 alias 127.0.0.3 up
sudo ifconfig lo0 alias 127.0.0.4 up









## Screenshot

This screen shot looks horrible and is just a placeholder ATM. Designers wanted. Apply to brian@openbazaar.org if you're interested in helping out.

![Screen 1](http://i.imgur.com/hYliE45.png)
=======


