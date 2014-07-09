import sys, os, hashlib, xmlrpclib
import json
import logging
import traceback
from urlparse import urlparse
import gnupg

import obelisk
from protocol import hello_request, hello_response, proto_response_pubkey
from pymongo import MongoClient
import pyelliptic as ec
from p2p import PeerConnection, TransportLayer
from dht import DHT
from zmq.eventloop import ioloop
from pprint import pprint

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

        #self._log.debug('Sending to peer: %s %s' % (self._ip, data))

        if self._pub == '':
            self._log.info('There is no public key for encryption')
        else:
            #self._log.debug('DATA: %s' % data)
            msg = self.send_raw(self.encrypt(json.dumps(data)), callback)
            return msg

    def peer_to_tuple(self):
        return self._ip, self._port, self._guid

    def get_guid(self):
        return self._guid


class CryptoTransportLayer(TransportLayer):

    def __init__(self, my_ip, my_port, market_id, bm_user=None, bm_pass=None, bm_port=None):

        self._log = logging.getLogger('[%s] %s' % (market_id, self.__class__.__name__))

        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar

        self._bitmessage_api = None
        if (bm_user, bm_pass, bm_port) != (None, None, None):
            print (bm_user, bm_pass, bm_port)
            if not self._connect_to_bitmessage(bm_user, bm_pass, bm_port):
                self._log.info('Bitmessage not available')

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

    def _connect_to_bitmessage(self, bm_user, bm_pass, bm_port):
        # Get bitmessage going
        # First, try to find a local instance
        result = False
        try:
            self._log.info('Connecting to Bitmessage on Port %s %s %s' % (bm_port, bm_user, bm_pass))
            self._bitmessage_api = xmlrpclib.ServerProxy("http://{}:{}@localhost:{}/".format(bm_user, bm_pass, bm_port), verbose=1)
            result = self._bitmessage_api.add(2,3)
            self._log.info("Bitmessage test result: {}, API is live".format(result))
        # If we failed, fall back to starting our own
        except Exception as e:
            self._log.info("Failed to connect to bitmessage instance: {}".format(e))
            self._bitmessage_api = None
            # self._log.info("Spawning internal bitmessage instance")
            # # Add bitmessage submodule path
            # sys.path.insert(0, os.path.join(
            #     os.path.dirname(__file__), '..', 'pybitmessage', 'src'))
            # import bitmessagemain as bitmessage
            # bitmessage.logger.setLevel(logging.WARNING)
            # bitmessage_instance = bitmessage.Main()
            # bitmessage_instance.start(daemon=True)
            # bminfo = bitmessage_instance.getApiAddress()
            # if bminfo is not None:
            #     self._log.info("Started bitmessage daemon at %s:%s".format(
            #         bminfo['address'], bminfo['port']))
            #     bitmessage_api = xmlrpclib.ServerProxy("http://{}:{}@{}:{}/".format(
            #         bm_user, bm_pass, bminfo['address'], bminfo['port']))
            # else:
            #     self._log.info("Failed to start bitmessage dameon")
            #     self._bitmessage_api = None
        return result

    def _checkok(self, msg):
        self._log.info('Check ok')

    def get_guid(self):
        return self._guid

    def getDHT(self):
        return self._dht

    def getBitmessageAPI(self):
        return self._bitmessage_api

    def getMarketID(self):
        return self._market_id

    def getMyself(self):
        return self._myself

    def _ping(self, msg):

        self._log.info('Pinged %s ' % msg)

        pinger = CryptoPeerConnection(self,msg['uri'], msg['pubkey'], msg['senderGUID'])
        pinger.send_raw(json.dumps(
            {"type": "hello_response",
             "senderGUID": self.guid,
             "uri": self._uri,
             "pubkey": self.pubkey,
            }))


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
            self.secret = self.settings['secret'] if self.settings.has_key("secret") else ""
            self.pubkey = self.settings['pubkey'] if self.settings.has_key("pubkey") else ""
            self.guid = self.settings['guid'] if self.settings.has_key("guid") else ""
            self.bitmessage = self.settings['bitmessage'] if self.settings.has_key('bitmessage') else ""

        else:
            self.nickname = 'Default'

            # Generate Bitcoin keypair
            self._generate_new_keypair()

            # Generate Bitmessage address
            if self._bitmessage_api is not None:
                self._generate_new_bitmessage_address()

            # Generate PGP key
            gpg = gnupg.GPG(gnupghome='gpg')
            input_data = gpg.gen_key_input(key_type="RSA", key_length=2048, name_comment="Autogenerated by Open Bazaar", passphrase="P@ssw0rd")
            key = gpg.gen_key(input_data)
            pubkey_text = gpg.export_keys(key.fingerprint)

            self._db.settings.update({"id":'%s' % self._market_id}, {"$set": {"PGPPubKey":pubkey_text, "PGPPubkeyFingerprint":key.fingerprint}}, True)

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

    def _generate_new_bitmessage_address(self):
      # Use the guid generated previously as the key
      self.bitmessage = self._bitmessage_api.createRandomAddress(self.guid.encode('base64'), 
            False, 1.05, 1.1111)
      self._db.settings.update({"id":'%s' % self._market_id}, {"$set": {"bitmessage":self.bitmessage}}, True)


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
            #self._init_peer({'uri': seed_uri, 'guid':seed_guid})

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

    def addCryptoPeer(self, peer_to_add):

        foundOutdatedPeer = False
        for idx, peer in enumerate(self._dht._activePeers):

            if (peer._address, peer._guid, peer._pub) == (peer_to_add._address, peer_to_add._guid, peer_to_add._pub):
                self._log.info('Found existing peer, not adding.')
                return

            if peer._guid == peer_to_add._guid or peer._pub == peer_to_add._pub or peer._address == peer_to_add._address:

                foundOutdatedPeer = True
                self._log.info('Found an outdated peer')

                # Update existing peer
                self._activePeers[idx] = peer_to_add

        if not foundOutdatedPeer and peer_to_add._guid != self._guid:
            self._log.info('Adding crypto peer at %s' % peer_to_add._address)
            self._dht.add_active_peer(self, (peer_to_add._pub, peer_to_add._address, peer_to_add._guid))



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


    def _init_peer(self, msg):

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



    def _on_message(self, msg):

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


    def _on_raw_message(self, serialized):

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

          self._on_message(msg)
        else:
          self._log.error('Received a message with no type')
