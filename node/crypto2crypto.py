from dht import DHT
from p2p import PeerConnection, TransportLayer
from pprint import pformat
from protocol import hello_request, hello_response, proto_response_pubkey
from urlparse import urlparse
from zmq.eventloop import ioloop
from zmq.eventloop.ioloop import PeriodicCallback
import gnupg
import xmlrpclib
import logging
import pyelliptic as ec
import requests
import socket
import traceback
from threading import Thread
import zlib
import obelisk
import arithmetic
from pybitcointools import *

ioloop.install()


class CryptoPeerConnection(PeerConnection):

    def __init__(self, transport, address, pub=None, guid=None, nickname=None,
                 sin=None, callback=lambda msg: None):

        # self._priv = transport._myself
        self.pub = pub
        self.ip = urlparse(address).hostname
        self.port = urlparse(address).port
        self.nickname = nickname
        self.sin = sin
        self.connected = False
        self.guid = guid

        PeerConnection.__init__(self, transport, address)

        self.log = logging.getLogger('[%s] %s' % (transport.market_id,
                                                   self.__class__.__name__))

    def start_handshake(self, handshake_cb=None):
        if self.check_port():
            def cb(msg):
                if msg:

                    self.log.debug('ALIVE PEER %s' % msg[0])
                    msg = msg[0]
                    msg = json.loads(msg)

                    # Update Information
                    self.guid = msg['senderGUID']
                    self.sin = self.generate_sin(self.guid)
                    self.pub = msg['pubkey']
                    self.nickname = msg['senderNick']

                    self._peer_alive = True

                    # Add this peer to active peers list
                    for idx, peer in enumerate(self.transport.dht.activePeers):
                        if peer.guid == self.guid or peer.address == self.address:
                            self.transport.dht.activePeers[idx] = self
                            self.transport.dht.add_peer(self.transport,
                                                          self.address,
                                                          self.pub,
                                                          self.guid,
                                                          self.nickname)
                            return

                    self.transport.dht.activePeers.append(self)
                    self.transport.dht._routingTable.addContact(self)

                    if handshake_cb is not None:
                        handshake_cb()

            self.send_raw(json.dumps({'type': 'hello',
                                      'pubkey': self.transport.pubkey,
                                      'uri': self.transport.uri,
                                      'senderGUID': self.transport.guid,
                                      'senderNick': self.transport.nickname}), cb)

    def __repr__(self):
        return '{ guid: %s, ip: %s, port: %s, pubkey: %s }' % (self.guid, self.ip, self.port, self.pub)

    def generate_sin(self, guid):
        return obelisk.EncodeBase58Check('\x0F\x02%s' + guid.decode('hex'))

    def check_port(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.ip, self.port))
        except socket.error:
            try:
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.ip, self.port))
            except socket.error as e:
                self.log.error("socket error on %s: %s" % (self.ip, e))
                return False
        except TypeError:
            self.log.error("tried connecting to invalid address: %s" % self.ip)
            return False

        s.close()
        return True

    def sign(self, data):
        self.log.info('secret %s' % self.transport.settings['secret'])
        cryptor = CryptoTransportLayer.makeCryptor(self.transport.settings['secret'])
        return cryptor.sign(data)

    @staticmethod
    def hexToPubkey(pubkey):
        pubkey_raw = arithmetic.changebase(pubkey[2:], 16, 256, minlen=64)
        pubkey_bin = '\x02\xca\x00 ' + pubkey_raw[:32] + '\x00 ' + pubkey_raw[32:]
        return pubkey_bin

    def encrypt(self, data):
        try:
            if self.pub is not None:
                result = ec.ECC(curve='secp256k1').encrypt(data, CryptoPeerConnection.hexToPubkey(self.pub))

                return result
            else:
                self.log.error('Public Key is missing')
                return False
        except Exception as e:
            self.log.error('Encryption failed. %s' % e)

    def send(self, data, callback=lambda msg: None):

        if hasattr(self, 'guid'):

            # Include guid
            data['guid'] = self.guid
            data['senderGUID'] = self.transport.guid
            data['uri'] = self.transport.uri
            data['pubkey'] = self.transport.pubkey
            data['senderNick'] = self.transport.nickname

            self.log.debug('Sending to peer: %s %s' % (self.ip, pformat(data)))

            if self.pub == '':
                self.log.info('There is no public key for encryption')
            else:
                signature = self.sign(json.dumps(data))
                data = self.encrypt(json.dumps(data))

                try:
                    if data is not None:
                        encoded_data = data.encode('hex')
                        if self.check_port():
                            self.send_raw(json.dumps({'sig': signature.encode('hex'), 'data': encoded_data}), callback)
                        else:
                            self.log.error('Cannot reach this peer to send raw')
                    else:
                        self.log.error('Data was empty')
                except Exception:
                    self.log.error("Was not able to encode empty data: %e")
        else:
            self.log.error('Cannot send to peer')

    def peer_to_tuple(self):
        return self.ip, self.port, self.guid

    def get_guid(self):
        return self.guid


class CryptoTransportLayer(TransportLayer):

    def __init__(self, my_ip, my_port, market_id, db, bm_user=None, bm_pass=None,
                 bm_port=None, seed_mode=0, dev_mode=False):

        self.log = logging.getLogger('[%s] %s' % (market_id,
                                                   self.__class__.__name__))
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.WARNING)

        # Connect to database
        self.db = db

        self._bitmessage_api = None
        if (bm_user, bm_pass, bm_port) != (None, None, None):
            if not self._connect_to_bitmessage(bm_user, bm_pass, bm_port):
                self.log.info('Bitmessage not installed or started')

        try:
            socket.inet_pton(socket.AF_INET6, my_ip)
            my_uri = "tcp://[%s]:%s" % (my_ip, my_port)
        except socket.error:
            my_uri = "tcp://%s:%s" % (my_ip, my_port)

        self.market_id = market_id
        self.nick_mapping = {}
        self.uri = my_uri
        self.ip = my_ip
        self.nickname = ""
        self._dev_mode = dev_mode

        # Set up
        self._setup_settings()

        self.dht = DHT(self, self.market_id, self.settings, self.db)

        # self._myself = ec.ECC(pubkey=self.pubkey.decode('hex'),
        #                       privkey=self.secret.decode('hex'),
        #                       curve='secp256k1')

        TransportLayer.__init__(self, market_id, my_ip, my_port,
                                self.guid, self.nickname)

        self.setup_callbacks()
        self.listen(self.pubkey)

        if seed_mode == 0 and not dev_mode:
            self.start_ip_address_checker()

    def setup_callbacks(self):
        self.add_callbacks([('hello', self._ping),
                            ('findNode', self._find_node),
                            ('findNodeResponse', self._find_node_response),
                            ('store', self._store_value)])

    def start_ip_address_checker(self):
        '''Checks for possible public IP change'''
        self.caller = PeriodicCallback(self._ip_updater_periodic_callback, 5000, ioloop.IOLoop.instance())
        self.caller.start()

    def _ip_updater_periodic_callback(self):
        try:
            r = requests.get('https://icanhazip.com')

            if r and hasattr(r, 'text'):
                ip = r.text
                ip = ip.strip(' \t\n\r')
                if ip != self.ip:
                    self.ip = ip
                    try:
                        socket.inet_pton(socket.AF_INET6, self.ip)
                        my_uri = 'tcp://[%s]:%s' % (self.ip, self.port)
                    except socket.error:
                        my_uri = 'tcp://%s:%s' % (self.ip, self.port)
                    self.uri = my_uri
                    self.stream.close()
                    self.listen(self.pubkey)

                    self.dht._iterativeFind(self.guid, [], 'findNode')
            else:
                self.log.error('Could not get IP')
        except Exception as e:
            self.log.error('[Requests] error: %s' % e)

    def save_peer_to_db(self, peer_tuple):
        uri = peer_tuple[0]
        pubkey = peer_tuple[1]
        guid = peer_tuple[2]
        nickname = peer_tuple[3]

        # Update query
        self.db.deleteEntries("peers", {"uri": uri, "guid": guid}, "OR")
        # if len(results) > 0:
        #     self.db.updateEntries("peers", {"id": results[0]['id']}, {"market_id": self.market_id, "uri": uri, "pubkey": pubkey, "guid": guid, "nickname": nickname})
        # else:
        if guid is not None:
            self.db.insertEntry("peers", {
                "uri": uri,
                "pubkey": pubkey,
                "guid": guid,
                "nickname": nickname,
                "market_id": self.market_id
            })

    def _connect_to_bitmessage(self, bm_user, bm_pass, bm_port):
        # Get bitmessage going
        # First, try to find a local instance
        result = False
        try:
            self.log.info('[_connect_to_bitmessage] Connecting to Bitmessage on port %s' % bm_port)
            self._bitmessage_api = xmlrpclib.ServerProxy("http://{}:{}@localhost:{}/".format(bm_user, bm_pass, bm_port), verbose=0)
            result = self._bitmessage_api.add(2, 3)
            self.log.info("[_connect_to_bitmessage] Bitmessage API is live".format(result))
        # If we failed, fall back to starting our own
        except Exception as e:
            self.log.info("Failed to connect to bitmessage instance: {}".format(e))
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
        self.log.info('Check ok')

    def get_guid(self):
        return self.guid

    def get_dht(self):
        return self.dht

    def get_bitmessage_api(self):
        return self._bitmessage_api

    def get_market_id(self):
        return self.market_id

    # def get_myself(self):
    #     return self._myself

    def _ping(self, msg):

        self.log.info('Pinged %s ' % pformat(msg))
        #
        # pinger = CryptoPeerConnection(self, msg['uri'], msg['pubkey'], msg['senderGUID'])
        # pinger.send_raw(json.dumps(
        #     {"type": "hello_response",
        #      "senderGUID": self.guid,
        #      "uri": self.uri,
        #      "senderNick": self.nickname,
        #      "pubkey": self.pubkey,
        #     }))

    def _store_value(self, msg):
        self.dht._on_storeValue(msg)

    def _find_node(self, msg):
        self.dht.on_find_node(msg)

    def _find_node_response(self, msg):
        self.dht.on_findNodeResponse(self, msg)

    def _setup_settings(self):

        self.settings = self.db.selectEntries("settings", "market_id = '%s'" % self.market_id.replace("'", "''"))
        if len(self.settings) == 0:
            self.settings = None
            self.db.insertEntry("settings", {"market_id": self.market_id, "welcome": "enable"})
        else:
            self.settings = self.settings[0]

        # Generate PGP key during initial setup or if previous PGP gen failed
        if not self.settings or not ('PGPPubKey' in self.settings and self.settings["PGPPubKey"]):
            try:
                self.log.info('Generating PGP keypair. This may take several minutes...')
                gpg = gnupg.GPG()
                input_data = gpg.gen_key_input(key_type="RSA",
                                               key_length=2048,
                                               name_email='gfy@gfy.com',
                                               name_comment="Autogenerated by Open Bazaar",
                                               passphrase="P@ssw0rd")
                assert input_data is not None
                key = gpg.gen_key(input_data)
                assert key is not None

                pubkey_text = gpg.export_keys(key.fingerprint)
                pgp_dict = {"PGPPubKey": pubkey_text, "PGPPubkeyFingerprint": key.fingerprint}
                self.db.updateEntries("settings", {"market_id": self.market_id}, pgp_dict)
                if self.settings:
                    self.settings.update(pgp_dict)

                self.log.info('PGP keypair generated.')
            except Exception as e:
                self.log.error("Encountered a problem with GPG: %s" % e)

        if self.settings:
            self.nickname = self.settings['nickname'] if 'nickname' in self.settings else ""
            self.secret = self.settings['secret'] if 'secret' in self.settings else ""
            self.pubkey = self.settings['pubkey'] if 'pubkey' in self.settings else ""
            self.privkey = self.settings.get('privkey')
            self.btc_pubkey = privkey_to_pubkey(self.privkey)
            self.guid = self.settings['guid'] if 'guid' in self.settings else ""
            self.sin = self.settings['sin'] if 'sin' in self.settings else ""
            self.bitmessage = self.settings['bitmessage'] if 'bitmessage' in self.settings else ""

            self._myself = ec.ECC(
                pubkey=CryptoTransportLayer.pubkey_to_pyelliptic(self.pubkey).decode('hex'),
                raw_privkey=self.secret.decode('hex'),
                curve='secp256k1'
            )
        else:
            self.nickname = 'Default'

            # Generate Bitcoin keypair
            self._generate_new_keypair()

            # Generate Bitmessage address
            if self._bitmessage_api is not None:
                self._generate_new_bitmessage_address()

            self.settings = self.db.selectEntries("settings", "market_id = '%s'" % self.market_id.replace("'", "''"))[0]

        self.log.debug('Retrieved Settings: \n%s', pformat(self.settings))

    @staticmethod
    def pubkey_to_pyelliptic(pubkey):
        # Strip 04
        pubkey = pubkey[2:]

        # Split it in half
        pub_x = pubkey[0:len(pubkey) / 2]
        pub_y = pubkey[len(pubkey) / 2:]

        # Add pyelliptic content
        print "02ca0020" + pub_x + "0020" + pub_y
        return "02ca0020" + pub_x + "0020" + pub_y

    def _generate_new_keypair(self):
        secret = str(random.randrange(2 ** 256))
        self.secret = hashlib.sha256(secret).hexdigest()
        self.pubkey = privtopub(self.secret)
        self.privkey = random_key()
        print 'PRIVATE KEY: ', self.privkey
        self.btc_pubkey = privtopub(self.privkey)
        print 'PUBLIC KEY: ', self.btc_pubkey

        # Generate SIN
        sha_hash = hashlib.sha256()
        sha_hash.update(self.pubkey)
        ripe_hash = hashlib.new('ripemd160')
        ripe_hash.update(sha_hash.digest())

        self.guid = ripe_hash.digest().encode('hex')
        self.sin = obelisk.EncodeBase58Check('\x0F\x02%s' + ripe_hash.digest())

        self.db.updateEntries("settings", {"market_id": self.market_id}, {"secret": self.secret,
                                                                            "pubkey": self.pubkey,
                                                                            "privkey": self.privkey,
                                                                            "guid": self.guid,
                                                                            "sin": self.sin})

    def _generate_new_bitmessage_address(self):
        # Use the guid generated previously as the key
        self.bitmessage = self._bitmessage_api.createRandomAddress(
            self.guid.encode('base64'),
            False,
            1.05,
            1.1111
        )
        self.db.updateEntries(
            "settings", {
                "market_id": self.market_id
            }, {
                "bitmessage": self.bitmessage
            }
        )

    def join_network(self, seed_peers=[], callback=lambda msg: None):

        self.log.info('Joining network')

        known_peers = []

        # Connect up through seed servers
        for idx, seed in enumerate(seed_peers):
            try:
                socket.inet_pton(socket.AF_INET6, seed)
                seed_peers[idx] = "tcp://[%s]:12345" % seed
            except socket.error:
                seed_peers[idx] = "tcp://%s:12345" % seed

        # Connect to persisted peers
        db_peers = self.get_past_peers()

        known_peers = list(set(seed_peers)) + list(set(db_peers))

        print 'known_peers', known_peers

        self.connect_to_peers(known_peers)

        # Populate routing table by searching for self
        if len(known_peers) > 0:
            self.search_for_my_node()

        if callback is not None:
            callback('Joined')

    def get_past_peers(self):
        peers = []
        result = self.db.selectEntries("peers", "market_id = '%s'" % self.market_id.replace("'", "''"))
        for peer in result:
            peers.append(peer['uri'])
        return peers

    def search_for_my_node(self):
        print 'Searching for myself'
        self.dht._iterativeFind(self.guid, self.dht.knownNodes, 'findNode')

    def connect_to_peers(self, known_peers):
        for known_peer in known_peers:
            t = Thread(target=self.dht.add_peer, args=(self, known_peer,))
            t.start()

    def get_crypto_peer(self, guid=None, uri=None, pubkey=None, nickname=None,
                        callback=None):
        if guid == self.guid:
            self.log.error('Cannot get CryptoPeerConnection for your own node')
            return

        self.log.debug('Getting CryptoPeerConnection\nGUID:%s\nURI:%s\nPubkey:%s\nNickname:%s' % (guid, uri, pubkey, nickname))

        return CryptoPeerConnection(self, uri, pubkey, guid=guid,
                                    nickname=nickname, callback=callback)

    def addCryptoPeer(self, peer_to_add):

        foundOutdatedPeer = False
        for idx, peer in enumerate(self.dht.activePeers):

            if (peer.address, peer.guid, peer.pub) == (peer_to_add.address, peer_to_add.guid, peer_to_add.pub):
                self.log.info('Found existing peer, not adding.')
                return

            if peer.guid == peer_to_add.guid or peer.pub == peer_to_add.pub or peer.address == peer_to_add.address:

                foundOutdatedPeer = True
                self.log.info('Found an outdated peer')

                # Update existing peer
                self.activePeers[idx] = peer_to_add

        if not foundOutdatedPeer and peer_to_add.guid != self.guid:
            self.log.info('Adding crypto peer at %s' % peer_to_add.nickname)
            self.dht.add_peer(self, peer_to_add.address, peer_to_add.pub, peer_to_add.guid, peer_to_add.nickname)

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

        self.settings = self.db.selectEntries("settings", "market_id = '%s'" % self.market_id.replace("'", "''"))[0]

        for uri, peer in self.peers.iteritems():
            if peer.pub:
                peers[uri] = peer.pub.encode('hex')
        return {'uri': self.uri, 'pub': self._myself.get_pubkey().encode('hex'), 'nickname': self.nickname,
                'peers': peers}

    def respond_pubkey_if_mine(self, nickname, ident_pubkey):

        if ident_pubkey != self.pubkey:
            self.log.info("Public key does not match your identity")
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

        for uri, peer in self.peers.iteritems():
            self.log.info('PEER: %s Pub: %s' %
                           (peer.pub.encode('hex'), pub.encode('hex')))
            if peer.pub.encode('hex') == pub.encode('hex'):
                return True

        return False

    def create_peer(self, uri, pub, node_guid):

        if pub:
            pub = pub.decode('hex')

        # Create the peer if public key is not already in the peer list
        # if not self.pubkey_exists(pub):
        self.peers[uri] = CryptoPeerConnection(self, uri, pub, node_guid)

        # Call 'peer' callbacks on listeners
        self.trigger_callbacks('peer', self.peers[uri])

        # else:
        #    print 'Pub Key is already in peer list'

    def send(self, data, send_to=None, callback=lambda msg: None):

        self.log.debug("Outgoing Data: %s %s" % (data, send_to))

        # Directed message
        if send_to is not None:

            peer = self.dht._routingTable.getContact(send_to)
            if not peer:
                for activePeer in self.dht.activePeers:
                    if activePeer.guid == send_to:
                        peer = activePeer
                        break

            # peer = CryptoPeerConnection(msg['uri'])
            if peer:
                self.log.debug('Directed Data (%s): %s' % (send_to, data))
                try:
                    peer.send(data, callback=callback)
                except Exception as e:
                    self.log.error('Not sending message directly to peer %s' % e)
            else:
                self.log.error('No peer found')

        else:
            # FindKey and then send

            for peer in self.dht.activePeers:
                try:
                    peer = self.dht._routingTable.getContact(peer.guid)
                    data['senderGUID'] = self.guid
                    data['pubkey'] = self.pubkey

                    def cb(msg):
                        self.log.debug('Message Back: \n%s' % pformat(msg))

                    peer.send(data, cb)

                except:
                    self.log.info("Error sending over peer!")
                    traceback.print_exc()

    def send_enc(self, uri, msg):
        peer = self.peers[uri]
        pub = peer.pub

        # Now send a hello message to the peer
        if pub:
            self.log.info("Sending encrypted [%s] message to %s"
                           % (msg['type'], uri))
            peer.send(msg)
        else:
            # Will send clear profile on initial if no pub
            self.log.info("Sending unencrypted [%s] message to %s"
                           % (msg['type'], uri))
            self.peers[uri].send_raw(json.dumps(msg))

    def _init_peer(self, msg):

        uri = msg['uri']
        pub = msg.get('pub')
        nickname = msg.get('nickname')
        msg_type = msg.get('type')
        guid = msg['guid']

        if not self.valid_peer_uri(uri):
            self.log.error("Invalid Peer: %s " % uri)
            return

        if uri not in self.peers:
            # Unknown peer
            self.log.info('Add New Peer: %s' % uri)
            self.create_peer(uri, pub, guid)

            if not msg_type:
                self.send_enc(uri, hello_request(self.get_profile()))
            elif msg_type == 'hello_request':
                self.send_enc(uri, hello_response(self.get_profile()))

        else:
            # Known peer
            if pub:
                # test if we have to update the pubkey
                if not self.peers[uri].pub:
                    self.log.info("Setting public key for seed node")
                    self.peers[uri].pub = pub.decode('hex')
                    self.trigger_callbacks('peer', self.peers[uri])

                if self.peers[uri].pub != pub.decode('hex'):
                    self.log.info("Updating public key for node")
                    self.peers[uri].nickname = nickname
                    self.peers[uri].pub = pub.decode('hex')

                    self.trigger_callbacks('peer', self.peers[uri])

            if msg_type == 'hello_request':
                # reply only if necessary
                self.send_enc(uri, hello_response(self.get_profile()))

    def _on_message(self, msg):

        # here goes the application callbacks
        # we get a "clean" msg which is a dict holding whatever
        # self.log.info("[On Message] Data received: %s" % msg)

        pubkey = msg.get('pubkey')
        uri = msg.get('uri')
        ip = urlparse(uri).hostname
        port = urlparse(uri).port
        guid = msg.get('senderGUID')
        nickname = msg.get('senderNick')[:120]

        self.dht.add_known_node((ip, port, guid, nickname))
        self.log.info('ON MESSAGE %s' % msg)

        self.dht.add_peer(self, uri, pubkey, guid, nickname)

        self.trigger_callbacks(msg['type'], msg)

    @staticmethod
    def makeCryptor(privkey):
        privkey_bin = '\x02\xca\x00 ' + arithmetic.changebase(privkey, 16, 256, minlen=32)
        pubkey = arithmetic.changebase(arithmetic.privtopub(privkey), 16, 256, minlen=65)[1:]
        pubkey_bin = '\x02\xca\x00 ' + pubkey[:32] + '\x00 ' + pubkey[32:]
        cryptor = ec.ECC(curve='secp256k1', privkey=privkey_bin, pubkey=pubkey_bin)
        return cryptor

    @staticmethod
    def makePubCryptor(pubkey):
        pubkey_bin = CryptoPeerConnection.hexToPubkey(pubkey)
        return ec.ECC(curve='secp256k1', pubkey=pubkey_bin)

    def _on_raw_message(self, serialized):

        try:

            # Decompress message
            serialized = zlib.decompress(serialized)

            msg = json.loads(serialized)
            self.log.info("Message Received [%s]" % msg.get('type', 'unknown'))

            if msg.get('type') is None:

                data = msg.get('data').decode('hex')
                sig = msg.get('sig').decode('hex')

                try:

                    cryptor = CryptoTransportLayer.makeCryptor(self.secret)

                    try:
                        data = cryptor.decrypt(data)
                    except Exception as e:
                        self.log.info('Exception: %s' % e)

                    self.log.debug('Signature: %s' % sig.encode('hex'))
                    self.log.debug('Signed Data: %s' % data)

                    # Check signature
                    data_json = json.loads(data)
                    sigCryptor = CryptoTransportLayer.makePubCryptor(data_json['pubkey'])
                    if sigCryptor.verify(sig, data):
                        self.log.info('Verified')
                    else:
                        self.log.error('Message signature could not be verified %s' % msg)
                        # return

                    msg = json.loads(data)
                    self.log.debug('Message Data %s ' % msg)
                except Exception as e:
                    self.log.error('Could not decrypt message properly %s' % e)

        except ValueError:
            try:
                # Encrypted?
                try:
                    msg = self._myself.decrypt(serialized)
                    msg = json.loads(msg)

                    self.log.info(
                        "Decrypted Message [%s]" % msg.get('type', 'unknown')
                    )
                except:
                    self.log.error("Could not decrypt message: %s" % msg)
                    return
            except:
                self.log.error('Message probably sent using incorrect pubkey')

                return

        if msg.get('type') is not None:
            self._on_message(msg)
        else:
            self.log.error('Received a message with no type')
