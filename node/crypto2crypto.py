import sys, os, hashlib, xmlrpclib
import json
import logging
import traceback
from urlparse import urlparse
import gnupg

import obelisk
from protocol import hello_request, hello_response, proto_response_pubkey
from db_store import Obdb
import pyelliptic as ec
from p2p import PeerConnection, TransportLayer
from dht import DHT
from zmq.eventloop import ioloop
from pprint import pprint
import socket
import time
import requests
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback

ioloop.install()




class CryptoPeerConnection(PeerConnection):

    def __init__(self, transport, address, pub=None, guid=None, nickname=None, callback=lambda msg: None):

        self._priv = transport._myself
        self._pub = pub
        self._ip = urlparse(address).hostname
        self._port = urlparse(address).port
        self._nickname = nickname

        PeerConnection.__init__(self, transport, address)

        self._log = logging.getLogger('[%s] %s' % (transport._market_id, self.__class__.__name__))

        if self.check_port():
            self._log.debug('Peer is listening')
            if guid is not None:
                self._guid = guid
                self._sin = obelisk.EncodeBase58Check('\x0F\x02%s' + self._guid.decode('hex'))
                callback(None)
            else:
                def cb(msg):
                    if msg:
                        self._peer_alive = True
                        msg = msg[0]
                        msg = json.loads(msg)
                        self._guid = msg['senderGUID']

                        self._sin = obelisk.EncodeBase58Check('\x0F\x02%s' + self._guid.decode('hex'))
                        self._pub = msg['pubkey']
                        self._nickname = msg['senderNick']

                        self._log.debug('New Crypt Peer: %s %s %s %s' % (self._address, self._pub, self._guid, self._nickname))
                        if callback != None:
                            callback(msg)
                try:
                    self.send_raw(json.dumps({'type':'hello',
                                              'pubkey':transport.pubkey,
                                              'uri':transport._uri,
                                              'senderGUID':transport.guid,
                                              'senderNick':transport._nickname}), cb)
                except:
                    print 'Sending raw message failed'

        else:
            self._log.debug('Cannot reach this peer. Port may not be open.')


    def __repr__(self):
        return '{ guid: %s, ip: %s, port: %s, pubkey: %s }' % (self._guid, self._ip, self._port, self._pub)

    def heartbeat(self):
        def cb(msg):
            print 'heartbeat'
        self.send_raw(json.dumps({'type':'heartbeat','guid':self._guid, 'pubkey':self._transport.pubkey, 'senderGUID':self._transport.guid, 'uri':self._transport._uri, 'checkPubkey':self._pub}), cb)

    def check_port(self):
        try:
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect((self._ip, self._port))
            s.close()
            return True
        except:
            return False

    def sign(self, data):
        return self._priv.sign(data)

    def encrypt(self, data):
        print data
        try:
            result = self._priv.encrypt(data, self._pub.decode('hex'))
            return result
        except:
            self._log.error('Missing public key')


    def send(self, data, callback=lambda msg: None):

        if hasattr(self, '_guid'):

            # Include guid
            data['guid'] = self._guid
            data['senderGUID'] = self._transport.guid
            data['uri'] = self._transport._uri
            data['pubkey'] = self._transport.pubkey
            data['senderNick'] = self._transport._nickname

            self._log.debug('Sending to peer: %s %s' % (self._ip, data))

            if self._pub == '':
                self._log.info('There is no public key for encryption')
            else:
                signature = self.sign(json.dumps(data))
                self._log.info('signature %s' % signature.encode('hex'))
                data = self.encrypt(json.dumps(data))
                self.send_raw(json.dumps({'sig':signature.encode('hex'),'data':data.encode('hex')}), callback)
        else:
            self._log.error('Cannot send to peer')

    def peer_to_tuple(self):
        return self._ip, self._port, self._guid

    def get_guid(self):
        return self._guid


class CryptoTransportLayer(TransportLayer):

    def __init__(self, my_ip, my_port, market_id, bm_user=None, bm_pass=None, bm_port=None, seed_mode=0, dev_mode=False):

        self._log = logging.getLogger('[%s] %s' % (market_id, self.__class__.__name__))
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.WARNING)

        # Connect to database
        self._db = Obdb()

        self._bitmessage_api = None
        if (bm_user, bm_pass, bm_port) != (None, None, None):
            if not self._connect_to_bitmessage(bm_user, bm_pass, bm_port):
                self._log.info('Bitmessage not available')

        self._market_id = market_id
        self.nick_mapping = {}
        self._uri = "tcp://%s:%s" % (my_ip, my_port)
        self._ip = my_ip
        self._nickname = ""

        # Set up
        self._setup_settings()

        self._dht = DHT(self, market_id, self.settings)

        self._myself = ec.ECC(pubkey=self.pubkey.decode('hex'), privkey=self.secret.decode('hex'), curve='secp256k1')

        TransportLayer.__init__(self, market_id, my_ip, my_port, self.guid, self._nickname)

        # Set up callbacks
        self.add_callback('hello', self._ping)
        self.add_callback('findNode', self._findNode)
        self.add_callback('findNodeResponse', self._findNodeResponse)
        self.add_callback('store', self._storeValue)

        self.listen(self.pubkey)

        self._dht._refreshNode()



        def cb():
            r = requests.get(r'http://icanhazip.com')

            if r and hasattr(r,'text'):
                ip = r.text
                ip = ip.strip(' \t\n\r')
                if ip != self._ip:
                    self._ip = ip
                    self._uri = 'tcp://%s:%s' % (self._ip, self._port)
                    self.stream.close()
                    self.listen(self.pubkey)
            else:
                self._log.error('Could not get ip')

        if seed_mode == 0 and not dev_mode:
            # Check IP periodically for changes
            self.caller = PeriodicCallback(cb, 5000, ioloop.IOLoop.instance())
            self.caller.start()

    def save_peer_to_db(self, peer_tuple):
        pubkey = peer_tuple[0]
        uri = peer_tuple[1]
        guid = peer_tuple[2]
        nickname = peer_tuple[3]

        # Update query
        results = self._db.selectEntries("peers", {"uri": uri})
        if len(results) > 0:
            self._db.updateEntries("peers", {"id":results[0]['id']}, {"market_id":self._market_id,"uri":uri, "pubkey": pubkey, "guid":guid, "nickname": nickname})
        else:
            self._db.insertEntry("peers", { "uri":uri, "pubkey": pubkey, "guid":guid, "nickname": nickname})

    def _connect_to_bitmessage(self, bm_user, bm_pass, bm_port):
        # Get bitmessage going
        # First, try to find a local instance
        result = False
        try:
            self._log.info('Connecting to Bitmessage on Port %s %s %s' % (bm_port, bm_user, bm_pass))
            self._bitmessage_api = xmlrpclib.ServerProxy("http://{}:{}@localhost:{}/".format(bm_user, bm_pass, bm_port), verbose=0)
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
             "senderNick": self._nickname,
             "pubkey": self.pubkey,
            }))


    def _storeValue(self, msg):
        self._dht._on_storeValue(msg)

    def _findNode(self, msg):
        self._dht.on_find_node(msg)

    def _findNodeResponse(self, msg):
        self._dht.on_findNodeResponse(self, msg)

    def _setup_settings(self):

        self.settings = self._db.selectEntries("settings", {"market_id":self._market_id})
        if len(self.settings) == 0:
            self.settings = None
        else:
            self.settings = self.settings[0]
        if self.settings:
            self._nickname = self.settings['nickname'] if self.settings.has_key("nickname") else ""
            self.secret = self.settings['secret'] if self.settings.has_key("secret") else ""
            self.pubkey = self.settings['pubkey'] if self.settings.has_key("pubkey") else ""
            self.guid = self.settings['guid'] if self.settings.has_key("guid") else ""
            self.sin = self.settings['sin'] if self.settings.has_key("sin") else ""
            self.bitmessage = self.settings['bitmessage'] if self.settings.has_key('bitmessage') else ""

        else:

	    self._db.insertEntry("settings", {"market_id": self._market_id})
            self._nickname = 'Default'

            # Generate Bitcoin keypair
            self._generate_new_keypair()

            # Generate Bitmessage address
            if self._bitmessage_api is not None:
                self._generate_new_bitmessage_address()

            # Generate PGP key
            gpg = gnupg.GPG()
            input_data = gpg.gen_key_input(key_type="RSA", key_length=2048, name_comment="Autogenerated by Open Bazaar", passphrase="P@ssw0rd")
            key = gpg.gen_key(input_data)
            pubkey_text = gpg.export_keys(key.fingerprint)

            self._db.updateEntries("settings", {"market_id": self._market_id}, {"PGPPubKey":pubkey_text, "PGPPubkeyFingerprint": key.fingerprint})

            self.settings = self._db.selectEntries("settings", {"market_id":self._market_id})[0]

        self._log.debug('Retrieved Settings: %s', self.settings)


    def _generate_new_keypair(self):

        # Generate new keypair
        key = ec.ECC(curve='secp256k1')
        self.secret = key.get_privkey().encode('hex')
        pubkey = key.get_pubkey()
        signedPubkey = key.sign(pubkey)
        self.pubkey = pubkey.encode('hex')
        self._myself = key

        # Generate SIN
        sha_hash = hashlib.sha256()
        sha_hash.update(pubkey)
        ripe_hash = hashlib.new('ripemd160')
        ripe_hash.update(sha_hash.digest())

        self.guid = ripe_hash.digest().encode('hex')
        self.sin = obelisk.EncodeBase58Check('\x0F\x02%s' + ripe_hash.digest())

        self._db.updateEntries("settings", {"market_id": self._market_id}, {"secret":self.secret, "pubkey":self.pubkey, "guid":self.guid, "sin":self.sin})


    def _generate_new_bitmessage_address(self):
      # Use the guid generated previously as the key
      self.bitmessage = self._bitmessage_api.createRandomAddress(self.guid.encode('base64'),
            False, 1.05, 1.1111)
      self._db.updateEntries("settings", {"market_id": self._market_id}, {"bitmessage":self.bitmessage})


    def join_network(self, dev_mode=0, callback=lambda msg: None):

        if dev_mode:
            self._log.info('DEV MODE')
            seed_peers = ('127.0.0.1')
        else:
            seed_peers = ('seed.openbazaar.org',
                          'seed2.openbazaar.org')

        for seed in seed_peers:
            self._log.info('Initializing Seed Peer(s): [%s]' % seed)

            def cb(msg):
                #self._dht._iterativeFind(self._guid, self._dht._knownNodes, 'findNode')
                callback(msg)

            self.connect('tcp://%s:12345' % seed, callback=cb)

        # Try to connect to known peers
        known_peers = self._db.selectEntries("peers", {"market_id": self._market_id})
        for known_peer in known_peers:

            self._log.info(known_peer['uri'])
            self._dht.add_known_node((urlparse(known_peer['uri']).hostname, urlparse(known_peer['uri']).port, known_peer['guid'], known_peer['nickname']))
            self._dht.add_active_peer(self, (known_peer['pubkey'], known_peer['uri'], known_peer['guid'], known_peer['nickname']))

            def cb(msg):

                self._dht._iterativeFind(self._guid, self._dht._knownNodes, 'findNode')
                callback(msg)

            self.connect(known_peer['uri'], callback=cb)


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
            #self.addCryptoPeer(peer)

            callback(msg)

        peer = CryptoPeerConnection(self, uri, callback=cb)

        return peer


    def get_crypto_peer(self, guid, uri, pubkey=None, nickname=None):

      if guid == self.guid:
        self._log.info('Trying to get crypto peer for yourself')
        return

      self._log.info('%s %s %s %s' % (guid, uri, pubkey, nickname))

      peer = CryptoPeerConnection(self, uri, pubkey, guid=guid, nickname=nickname)
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
            self._log.info('Adding crypto peer at %s' % peer_to_add._nickname)
            self._dht.add_active_peer(self, (peer_to_add._pub, peer_to_add._address, peer_to_add._guid, peer_to_add._nickname))



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

        self.settings = self._db.selectEntries("settings", {"market_id":self._market_id})[0]

        for uri, peer in self._peers.iteritems():
            if peer._pub:
                peers[uri] = peer._pub.encode('hex')
        return {'uri': self._uri, 'pub': self._myself.get_pubkey().encode('hex'),'nickname': self._nickname,
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

    def send(self, data, send_to=None, callback=lambda msg: None):

        self._log.debug("Outgoing Data: %s %s" % (data, send_to))

        # Directed message
        if send_to is not None:

            peer = self._dht._routingTable.getContact(send_to)
            #peer = CryptoPeerConnection(msg['uri'])
            if peer:
                self._log.debug('Directed Data (%s): %s' % (send_to, data))

                try:
                    peer.send(data, callback=callback)
                except:
                    self._log.error('Not sending messing directly to peer')
            else:
                self._log.error('No peer found')

        else:
            # FindKey and then send

            for peer in self._dht._activePeers:
                try:
                    peer = self._dht._routingTable.getContact(peer._guid)
                    data['senderGUID'] = self._guid
                    data['pubkey'] = self.pubkey
                    print data
                    #if peer._pub:
                    #    peer.send(data, callback)
                    #else:


                    def cb(msg):
                        print 'msg %s' % msg

                    peer.send(data, cb)

                except:
                    self._log.info("Error sending over peer!")
                    traceback.print_exc()

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
        nickname = msg.get('senderNick')

        self._log.info('on message %s' % nickname)

        self._dht.add_known_node((ip, port, guid, nickname))
        self._dht.add_active_peer(self, (pubkey, uri, guid, nickname))
        self.trigger_callbacks(msg['type'], msg)


    def _on_raw_message(self, serialized):

        try:
            # Try to de-serialize clear text message
            msg = json.loads(serialized)
            self._log.info("Message Received [%s]" % msg.get('type', 'unknown'))

            if msg.get('type') is None:

                data = msg.get('data').decode('hex')
                sig = msg.get('sig').decode('hex')

                try:

                    data = self._myself.decrypt(data)

                    self._log.debug('Signature: %s' % sig.encode('hex'))
                    self._log.debug('Signed Data: %s' % data)

                    guid =  json.loads(data).get('guid')

                    ecc = ec.ECC(curve='secp256k1',pubkey=json.loads(data).get('pubkey').decode('hex'))

                    # Check signature
                    if ecc.verify(sig, data):
                        self._log.info('Verified')
                    else:
                        self._log.error('Message signature could not be verified %s' % msg)
                        return

                    msg = json.loads(data)
                    self._log.debug('Message Data %s ' % msg)
                except Exception, e:
                    self._log.error('Could not decrypt message properly %s' % e)

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

          self._on_message(msg)
        else:
          self._log.error('Received a message with no type')
