import hashlib
import json
import logging
import traceback
from urlparse import urlparse

import obelisk
from protocol import hello_request, hello_response, proto_response_pubkey
from pymongo import MongoClient
import pyelliptic as ec
from p2p import PeerConnection, TransportLayer
from dht import DHT
from zmq.eventloop import ioloop

ioloop.install()
import time

import tornado


class CryptoPeerConnection(PeerConnection):

    def __init__(self, transport, address, pub=None, guid=None, callback=lambda msg: None):

        self._priv = transport._myself
        self._pub = pub
        self._ip = urlparse(address).hostname
        self._port = urlparse(address).port
        PeerConnection.__init__(self, transport, address)
        self._log = logging.getLogger('[%s] %s' % (transport._market_id, self.__class__.__name__))

        self._peer_alive = False

        if guid is not None:
            self._guid = guid
            callback(None)
        else:
            def cb(msg):
                self._peer_alive = True
                msg = msg[0]
                msg = json.loads(msg)
                self._guid = msg['senderGUID']
                self._pub = msg['pubkey']

                self._log.debug('New Crypt Peer: %s %s %s' % (self._address, self._pub, self._guid))

                callback(msg)
            try:
                self.send_raw(json.dumps({'type':'hello', 'pubkey':transport.pubkey,
                                      'uri':transport._uri,
                                      'senderGUID':transport.guid }), cb)
            except:
                print 'error'

            def remove_dead_peer():
                if not self._peer_alive:
                    self._log.info('Dead Peer')
                    return False

            # Set timer for checking if peer alive
            ioloop.IOLoop.instance().add_timeout(time.time() + 3, remove_dead_peer)


    def __repr__(self):
        return '{ guid: %s, ip: %s, port: %s, pubkey: %s }' % (self._guid, self._ip, self._port, self._pub)

    def setPub(self, msg):
        print 'setpub',msg

    def heartbeat(self):
        def cb(msg):
            print 'heartbeat'
        self.send_raw(json.dumps({'type':'heartbeat','guid':self._guid, 'pubkey':self._transport.pubkey, 'senderGUID':self._transport.guid, 'uri':self._transport._uri, 'checkPubkey':self._pub}), cb)

    def encrypt(self, data):
        return self._priv.encrypt(data, self._pub.decode('hex'))

    def send(self, data, callback=lambda msg: None):

        # Include guid        
        data['guid'] = self._guid
        data['senderGUID'] = self._transport.guid
        data['uri'] = self._transport._uri
        data['pubkey'] = self._transport.pubkey

        #self._log.debug('Sending to peer: %s %s' % (self._guid, data))

        if self._pub == '':
            self._log.info('There is no public key for encryption')
        else:
            #self._log.debug('DATA: %s' % data)
            msg = self.send_raw(self.encrypt(json.dumps(data)), callback)
            return msg

    def on_message(self, msg, callback=None):

        # Need to validate that the pubkey coming back is the one we sent out in
        # case the node updated their keys
        remote_pub = json.loads(msg[0]).get('pubkey')
        print 'Local:%s Remote:%s' % (self._pub, remote_pub)

        if self._pub is not None and self._pub != remote_pub:
            print 'Pubkey doesnt match the GUID, removing active peer'
            activePeers = self._transport._dht._activePeers


        if callback is not None:
            callback(msg)

    def peer_to_tuple(self):
        return self._ip, self._port, self._guid

    def get_guid(self):
        return self._guid


class CryptoTransportLayer(TransportLayer):

    def __init__(self, my_ip, my_port, market_id):

        self._log = logging.getLogger('[%s] %s' % (market_id, self.__class__.__name__))

        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar

        self._market_id = market_id
        self.nick_mapping = {}
        self._uri = "tcp://%s:%s" % (my_ip, my_port)

        # Set up
        self._setup_settings()

        self._dht = DHT(self, market_id, self.settings)

        self._myself = ec.ECC(pubkey=self.pubkey.decode('hex'), privkey=self.secret.decode('hex'), curve='secp256k1')

        TransportLayer.__init__(self, market_id, my_ip, my_port, self.guid)

        # Set up callbacks
        self.add_callback('hello', self._ping)
        self.add_callback('findNode', self._findNode)
        self.add_callback('findNodeResponse', self._findNodeResponse)
        self.add_callback('store', self._storeValue)

        self.listen(self.pubkey)


    def _checkok(self, msg):
        self._log.info('Check ok')

    def get_guid(self):
        return self._guid

    def getDHT(self):
        return self._dht

    def getMarketID(self):
        return self._market_id

    def getMyself(self):
        return self._myself

    def _ping(self, msg):

        self._log.info('Pinged %s ' % msg)

        pinger = CryptoPeerConnection(self,msg['uri'], msg['pubkey'], msg['senderGUID'])
        msg = pinger.send_raw(json.dumps(
            {"type": "hello_response",
             "senderGUID": self.guid,
             "uri": self._uri,
             "pubkey": self.pubkey,
            }))
        print msg


    def _storeValue(self, msg):
        self._dht._on_storeValue(msg)

    def _findNode(self, msg):
        self._dht.on_find_node(msg)

    def _findNodeResponse(self, msg):
        self._dht.on_findNodeResponse(self, msg)

    def _setup_settings(self):

        self.settings = self._db.settings.find_one({'id':"%s" % self._market_id})

        if self.settings:
            self.nickname = self.settings['nickname'] if self.settings.has_key("nickname") else ""
            self.secret = self.settings['secret']
            self.pubkey = self.settings['pubkey']
            self.guid = self.settings['guid']
        else:
            self.nickname = 'Default'
            self._generate_new_keypair()
            self.settings = self._db.settings.find_one({'id':"%s" % self._market_id})

        self._log.debug('Retrieved Settings: %s', self.settings)


    def _generate_new_keypair(self):

      # Generate new keypair
      key = ec.ECC(curve='secp256k1')
      self.secret = key.get_privkey().encode('hex')
      pubkey = key.get_pubkey()
      signedPubkey = key.sign(pubkey)
      self.pubkey = pubkey.encode('hex')
      self._myself = key

      # Generate a node ID by ripemd160 hashing the signed pubkey
      guid = hashlib.new('ripemd160')
      guid.update(signedPubkey)
      self.guid = guid.digest().encode('hex')

      self._db.settings.update({"id":'%s' % self._market_id}, {"$set": {"secret":self.secret, "pubkey":self.pubkey, "guid":self.guid}}, True)


    def join_network(self, seed_uri, callback=lambda msg: None):

        if seed_uri:
            self._log.info('Initializing Seed Peer(s): [%s]' % (seed_uri))

            def cb(msg):
                self._dht._iterativeFind(self._guid, self._dht._knownNodes, 'findNode')
                callback(msg)

            self.connect(seed_uri, callback=cb)

        # self.listen(self.pubkey) # Turn on zmq socket
        #
        # if seed_uri:
        #     self._log.info('Initializing Seed Peer(s): [%s]' % seed_uri)
        #     seed_peer = CryptoPeerConnection(self, seed_uri)
        #     self._dht.start(seed_peer)

    def connect(self, uri, callback):

        def cb(msg):
            ip = urlparse(uri).hostname
            port = urlparse(uri).port

            self._dht.add_known_node((ip, port, peer._guid))

            # Turning off peers
            #self.init_peer({'uri': seed_uri, 'guid':seed_guid})

            # Add to routing table
            self.addCryptoPeer(peer)
            callback(msg)

        peer = CryptoPeerConnection(self, uri, callback=cb)

        return peer


    def get_crypto_peer(self, guid, uri, pubkey=None):

      if guid == self.guid:
        self._log.info('Trying to get cryptopeer for yourself')
        return

      peer = CryptoPeerConnection(self, uri, pubkey, guid=guid)
      return peer

    def addCryptoPeer(self, peer):

      peerExists = False
      for idx, aPeer in enumerate(self._dht._activePeers):

        if aPeer._guid == peer._guid or aPeer._pub == peer._pub or aPeer._address == peer._address:

          self._log.info('guids or pubkey match')
          peerExists = True
          if peer._pub and aPeer._pub == '':
            self._log.info('no pubkey')
            aPeer._pub = peer._pub
            self._activePeers[idx] = aPeer

      if not peerExists and peer._guid != self._guid:
        self._log.info('Adding crypto peer %s' % peer._pub)
        self._dht._routingTable.addContact(peer)
        self._dht.add_active_peer(self, (peer._pub, peer._address, peer._guid))



    # Return data array with details from the crypto file
    # TODO: This needs to be protected better; potentially encrypted file or DB
    @staticmethod
    def load_crypto_details(store_file):
        with open(store_file) as f:
            data = json.loads(f.read())
        assert "nickname" in data
        assert "secret" in data
        assert "pubkey" in data
        assert len(data["secret"]) == 2 * 32
        assert len(data["pubkey"]) == 2 * 33

        return data["nickname"], data["secret"].decode("hex"), \
            data["pubkey"].decode("hex")

    def get_profile(self):
        peers = {}

        self.settings = self._db.settings.find_one({'id':"%s" % self._market_id})

        for uri, peer in self._peers.iteritems():
            if peer._pub:
                peers[uri] = peer._pub.encode('hex')
        return {'uri': self._uri, 'pub': self._myself.get_pubkey().encode('hex'),'nickname': self.nickname,
                'peers': peers}

    def respond_pubkey_if_mine(self, nickname, ident_pubkey):

        if ident_pubkey != self.pubkey:
            self._log.info("Public key does not match your identity")
            return

        # Return signed pubkey
        pubkey = self._myself.pubkey
        ec_key = obelisk.EllipticCurveKey()
        ec_key.set_secret(self.secret)
        digest = obelisk.Hash(pubkey)
        signature = ec_key.sign(digest)

        # Send array of nickname, pubkey, signature to transport layer
        self.send(proto_response_pubkey(nickname, pubkey, signature))

    def pubkey_exists(self, pub):

        for uri, peer in self._peers.iteritems():
            self._log.info('PEER: %s Pub: %s' %
                           (peer._pub.encode('hex'), pub.encode('hex')))
            if peer._pub.encode('hex') == pub.encode('hex'):
                return True

        return False

    def create_peer(self, uri, pub, node_guid):

        if pub:
            pub = pub.decode('hex')

        # Create the peer if public key is not already in the peer list
        # if not self.pubkey_exists(pub):
        self._peers[uri] = CryptoPeerConnection(self, uri, pub, node_guid)

        # Call 'peer' callbacks on listeners
        self.trigger_callbacks('peer', self._peers[uri])

        # else:
        #    print 'Pub Key is already in peer list'

    def send_enc(self, uri, msg):
        peer = self._peers[uri]
        pub = peer._pub

        # Now send a hello message to the peer
        if pub:
            self._log.info("Sending encrypted [%s] message to %s"
                           % (msg['type'], uri))
            peer.send(msg)
        else:
            # Will send clear profile on initial if no pub
            self._log.info("Sending unencrypted [%s] message to %s"
                           % (msg['type'], uri))
            self._peers[uri].send_raw(json.dumps(msg))


    def init_peer(self, msg):

        uri = msg['uri']
        pub = msg.get('pub')
        nickname = msg.get('nickname')
        msg_type = msg.get('type')
        guid = msg['guid']

        if not self.valid_peer_uri(uri):
            self._log.error("Invalid Peer: %s " % uri)
            return

        if uri not in self._peers:
            # Unknown peer
            self._log.info('Add New Peer: %s' % uri)
            self.create_peer(uri, pub, guid)

            if not msg_type:
                self.send_enc(uri, hello_request(self.get_profile()))
            elif msg_type == 'hello_request':
                self.send_enc(uri, hello_response(self.get_profile()))

        else:
            # Known peer
            if pub:
                # test if we have to update the pubkey
                if not self._peers[uri]._pub:
                    self._log.info("Setting public key for seed node")
                    self._peers[uri]._pub = pub.decode('hex')
                    self.trigger_callbacks('peer', self._peers[uri])

                if self._peers[uri]._pub != pub.decode('hex'):
                    self._log.info("Updating public key for node")
                    self._peers[uri]._nickname = nickname
                    self._peers[uri]._pub = pub.decode('hex')

                    self.trigger_callbacks('peer', self._peers[uri])

            if msg_type == 'hello_request':
                # reply only if necessary
                self.send_enc(uri, hello_response(self.get_profile()))



    def on_message(self, msg):

        # here goes the application callbacks
        # we get a "clean" msg which is a dict holding whatever
        #self._log.info("[On Message] Data received: %s" % msg)

        pubkey = msg.get('pubkey')
        uri = msg.get('uri')
        ip = urlparse(uri).hostname
        port = urlparse(uri).port
        guid = msg.get('senderGUID')

        self._dht.add_known_node((ip, port, guid))

        self._dht.add_active_peer(self, (pubkey, uri, guid))


        self.trigger_callbacks(msg['type'], msg)


    def on_raw_message(self, serialized):

        try:
            # Try to deserialize cleartext message
            msg = json.loads(serialized)
            self._log.info("Message Received [%s]" % msg.get('type', 'unknown'))

        except ValueError:
            try:
                # Encrypted?
                try:
                  msg = self._myself.decrypt(serialized)
                  msg = json.loads(msg)

                  self._log.info("Decrypted Message [%s]"
                               % msg.get('type', 'unknown'))
                except:
                  self._log.error("Could not decrypt message: %s" % msg)
                  return
            except:

                self._log.error('Message probably sent using incorrect pubkey')

                return

        if msg.get('type') is not None:

          msg_type = msg.get('type')
          msg_uri = msg.get('uri')
          msg_guid = msg.get('guid')

          self._log.info('Type: %s' % msg.get('type'))

          self.on_message(msg)
        else:
          self._log.error('Received a message with no type')
