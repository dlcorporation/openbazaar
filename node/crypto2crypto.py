import json
import pyelliptic as ec

from p2p import PeerConnection, TransportLayer
import traceback
from pymongo import MongoClient
from protocol import hello_request, hello_response, proto_response_pubkey
import obelisk
import logging
from market import Market
from obelisk import bitcoin
from urlparse import urlparse
import hashlib
from contact import Contact
import constants

class CryptoPeerConnection(PeerConnection):

    def __init__(self, transport, address, pub, node_guid):
        self._priv = transport._myself
        self._pub = pub
        self._guid = node_guid
        PeerConnection.__init__(self, transport, address, node_guid)

    def encrypt(self, data):
        return self._priv.encrypt(data, self._pub)

    def send(self, data):
        self.send_raw(self.encrypt(json.dumps(data)))

    def on_message(self, msg, callback=None):
        # this are just acks
        pass


class CryptoTransportLayer(TransportLayer):

    def __init__(self, my_ip, my_port, market_id):

        TransportLayer.__init__(self, my_ip, my_port)

        self._myself = ec.ECC(curve='secp256k1')
        self._market_id = market_id
        self.nick_mapping = {}

        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar

        # Set up callbacks
        self.add_callback('ping', self._on_ping)
        self.add_callback('pong', self._on_pong)
        self.add_callback('findNode', self._on_findNode)
        self.add_callback('findNodeResponse', self._on_findNodeResponse)

        self._init_dht()
        self._setup_settings()

        self._log = logging.getLogger(self.__class__.__name__)

    def _init_dht(self):
        self._activePeers = []
        self._shortlist = []
        self._alreadyContacted = []
        self._findValueResult = {}
        self._activeProbes = []
        self._pendingIterationCalls = []
        self._slowNodeCount = [0]
        self._contactedNow = 0
        self._dhtCallbacks = []

    def _setup_settings(self):

        self.settings = self._db.settings.find_one({'id':"%s" % self._market_id})

        if self.settings:
            self.nickname = self.settings['nickname'] if self.settings.has_key("nickname") else ""
            self.secret = self.settings['secret']
            self.pubkey = self.settings['pubkey']
        else:
            self.nickname = 'Default'
            key = bitcoin.EllipticCurveKey()
            key.new_key_pair()
            hexkey = key.secret.encode('hex')
            self._db.settings.insert({"id":'%s'%market_id, "secret":hexkey, "pubkey":bitcoin.GetPubKey(key._public_key.pubkey, False).encode('hex')})
            self.settings = self._db.settings.find_one({'id':"%s" % self._market_id})

    # CALLBACKS

    def _on_ping(self, peer):
      uri = peer['uri']
      self._peers[uri].send_raw(json.dumps({"type":"pong", "guid": self._guid, "uri":self._uri, "findValue":peer['findValue']}))
      self._log.info("Got a ping")

    def _on_pong(self, msg):
      self._log.info("PONG %s" % msg)
      nodeID = self.extendShortlist(msg)

    def _on_findNode(self, msg):
      """ Finds a number of known nodes closest to the node/value with the
      specified key.

      @param key: the 160-bit key (i.e. the node or value ID) to search for
      @type key: str

      """
      # Get the sender's ID (if any)
      senderID = msg['senderID']
      key = msg['key']
      uri = msg['uri']

      # Add contact to routing table
      newContact = PeerConnection(self, uri, senderID)
      if not self._routingTable.getContact(senderID):
          self._routingTable.addContact(newContact)

      contacts = self._routingTable.findCloseNodes(key, constants.k, senderID)
      contactTriples = []
      for contact in contacts:
          contactTriples.append( (contact._guid, contact._address) )
          foundContact = self._routingTable.getContact(senderID)

      newContact.send_raw(json.dumps({"type":"findNodeResponse","guid":self._guid,"uri":self._uri,"findValue":contactTriples}))


    def _on_findNodeResponse(self, msg):

      nodeID = self.extendShortlist(msg)

      if nodeID != False:
          self.cancelActiveProbe(nodeID)
      else:
          print 'Remove from shortlist'

      self._alreadyContacted.append(nodeID)
      self._contactedNow += 1

      if self._contactedNow == constants.alpha:
        return

      if len(self._activeProbes) > self._slowNodeCount[0] or (len(self._shortlist) < constants.k and len(self._activeContacts) < len(self._shortlist) and len(self._activeProbes) > 0):
        #print '----------- scheduling next call -------------'
        # Schedule the next iteration if there are any active calls (Kademlia uses loose parallelism)
        #call = twisted.internet.reactor.callLater(constants.iterativeLookupDelay, searchIteration) #IGNORE:E1101
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + constants.iterativeLookupDelay)
        self.searchIteration()
      # Check for a quick contact response that made an update to the shortList
      elif self._prevShortlistLength < len(self._shortlist):
        # Ensure that the closest contacts are taken from the updated shortList
        self.searchIteration()
      else:
        #print '++++++++++++++ DONE (logically) +++++++++++++\n\n'
        # If no probes were sent, there will not be any improvement, so we're done
        #outerDf.callback(activeContacts)
        print 'Done'

    # KADEMLIA

    def cancelActiveProbe(self,   contactID):
      self._activeProbes.pop()
      if len(self._activeProbes) <= constants.alpha/2 and len(self._pendingIterationCalls):
          # Force the iteration
          self._pendingIterationCalls[0].cancel()
          del self._pendingIterationCalls[0]
          #print 'forcing iteration ================='
          self.searchIteration()

    def iterativeStore(self, key, value, originalPublisherID=None, age=0):
        """ The Kademlia store operation

        Call this to store/republish data in the DHT.

        @param key: The hashtable key of the data
        @type key: str
        @param value: The actual data (the value associated with C{key})
        @type value: str
        @param originalPublisherID: The node ID of the node that is the
                                    B{original} publisher of the data
        @type originalPublisherID: str
        @param age: The relative age of the data (time in seconds since it was
                    originally published). Note that the original publish time
                    isn't actually given, to compensate for clock skew between
                    different nodes.
        @type age: int
        """
        if originalPublisherID == None:
            originalPublisherID = self._guid

        self.iterativeFindNode(key, 'store')

        # Find k nodes closest to the key...
        #df = self.iterativeFindNode(key)
        # ...and send them STORE RPCs as soon as they've been found
        #df.addCallback(executeStoreRPCs)
        #return df

    def executeStoreRPCs(nodes):
        #print '        .....execStoreRPCs called'
        if len(nodes) >= constants.k:
            # If this node itself is closer to the key than the last (furthest) node in the list,
            # we should store the value at ourselves as well
            if self._routingTable.distance(key, self.id) < self._routingTable.distance(key, nodes[-1].id):
                nodes.pop()
                self.store(key, value, originalPublisherID=originalPublisherID, age=age)
        else:
            self.store(key, value, originalPublisherID=originalPublisherID, age=age)
        for contact in nodes:
            contact.store(key, value, originalPublisherID, age)
        return nodes

    def iterativeFindNode(self, key):
        """ The basic Kademlia node lookup operation

        Call this to find a remote node in the P2P overlay network.

        @param key: the 160-bit key (i.e. the node or value ID) to search for
        @type key: str

        @return: This immediately returns a deferred object, which will return
                 a list of k "closest" contacts (C{kademlia.contact.Contact}
                 objects) to the specified key as soon as the operation is
                 finished.
        @rtype: twisted.internet.defer.Deferred
        """
        return self._iterativeFind(key)




    def _iterativeFind(self, key, startupShortlist=None, call='findNode', callback=None):

      # Determine if we're looking for a node or a key
      if call != 'findNode':
        findValue = True
      else:
        findValue = False

      if startupShortlist == []:
        closeNodes = self._routingTable.findCloseNodes(key, constants.alpha)

        for closeNode in closeNodes:
          ip = urlparse(closeNode._address).hostname
          port = urlparse(closeNode._address).port
          guid = closeNode._guid
          self._shortlist.append((ip, port, guid))

        if key != self._guid:
          self._routingTable.touchKBucket(key)

        if len(self._shortlist) == 0:
          if(callback != None):
            callback([])
          else:
            return []

      else:
        self._shortlist = startupShortlist

      prevClosestNode = [None]

      def searchIteration():

        self._slowNodeCount[0] = len(self._activeProbes)

        # Sort closest to farthest
        self._activePeers.sort(lambda firstContact, secondContact, targetKey=key: cmp(self._routingTable.distance(firstContact._guid, targetKey), self._routingTable.distance(secondContact._guid, targetKey)))
        while len(self._pendingIterationCalls):
          del self._pendingIterationCalls[0]

        if key in self._findValueResult:
          return findValueResult

        elif len(self._activePeers) and findValue == False:
          if (len(self._activePeers) >= constants.k) or (self._activeContacts[0] == prevClosestNode[0] and len(self._activeProbes) == self._slowNodeCount[0]):

            return self._activePeers

        if len(self._activePeers):
          prevClosestNode[0] = self._activePeers[0]

        contactedNow = 0

        self._shortlist.sort(lambda firstContact, secondContact, targetKey=key: cmp(self._routingTable.distance(firstContact._guid, targetKey), self._routingTable.distance(secondContact._guid, targetKey)))
        prevShortlistLength = len(self._shortlist)

        for node in self._shortlist:
          if node not in self._alreadyContacted:

              self._activeProbes.append(node)

              uri = "tcp://%s:%s" % (node[0], node[1])
              msg = {"type":"findNode", "uri":self._uri, "senderID":self._guid, "key":key, "findValue":findValue}

              contact = self._routingTable.getContact(node[2])

              def extendShortlist(response):

                    print response
                    # """ @type response: json response """
                    # nodeID = response['guid']
                    # nodeURI = response['uri']
                    # findValue = False
                    # result = response['findValue']
                    #
                    # uri = response['uri'] # tuple: (ip adress, udp port)
                    # print self._activePeers, response
                    #
                    # # Make sure the responding node is valid, and abort the operation if it isn't
                    # if nodeID in self._activePeers or nodeID == self._guid:
                    #     return nodeID
                    #
                    # # Mark this node as active
                    # if nodeID in self._shortlist:
                    #     print 'Mark node active'
                    #     # Get the contact information from the shortlist...
                    #     #aContact = shortlist[shortlist.index(responseMsg.nodeID)]
                    #     aPeer = PeerConnection(self, nodeURI, nodeID)
                    # else:
                    #     print 'Mark node with real node ID'
                    #     # If it's not in the shortlist; we probably used a fake ID to reach it
                    #     # - reconstruct the contact, using the real node ID this time
                    #     #aContact = Contact(nodeID, responseTuple['uri'], responseTuple['uri'], self._protocol)
                    #     aPeer = PeerConnection(self, nodeURI, nodeID)
                    #
                    # self._activePeers.append(aPeer)
                    # print 'Active Peers:', self._activePeers
                    #
                    # # This makes sure "bootstrap"-nodes with "fake" IDs don't get queried twice
                    # if nodeID not in self._alreadyContacted:
                    #     self._alreadyContacted.append(nodeID)
                    #
                    # print 'Already Contacted: ', self._alreadyContacted
                    #
                    # # Now grow extend the (unverified) shortlist with the returned contacts
                    # #result = responseMsg.response
                    #
                    # #TODO: some validation on the result (for guarding against attacks)
                    #
                    # # If we are looking for a value, first see if this result is the value
                    # # we are looking for before treating it as a list of contact triples
                    # if findValue == True and type(result) == dict:
                    #     # We have found the value
                    #     self._findValueResult[key] = result[key]
                    # else:
                    #     if findValue == True:
                    #         # We are looking for a value, and the remote node didn't have it
                    #         # - mark it as the closest "empty" node, if it is
                    #         if 'closestNodeNoValue' in self._findValueResult:
                    #             if self._routingTable.distance(key, responseMsg.nodeID) < self._routingTable.distance(key, activeContacts[0].id):
                    #                 self._findValueResult['closestNodeNoValue'] = aContact
                    #         else:
                    #             self._findValueResult['closestNodeNoValue'] = aContact
                    #     for contactTriple in result:
                    #         print contactTriple
                    #         #if isinstance(contactTriple, (list, tuple)) and len(contactTriple) == 3:
                    #         testContact = Contact(contactTriple[0], contactTriple[1])
                    #         if testContact not in self._shortlist:
                    #             self._shortlist.append(testContact)
                    # return nodeID

              contact.send_raw(json.dumps(msg), extendShortlist)


      # Start searching
      results = searchIteration()

      if(callback != None):
        callback(results)
      else:
        return results





    # Return data array with details from the crypto file
    # TODO: This needs to be protected better; potentially encrypted file or DB
    def load_crypto_details(self, store_file):
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
        self._log.info('SETTINGS %s' % self.settings)
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

        if not self.valid_peer_uri(uri):
            self._log.info("Peer " + uri + " is not valid.")
            return

        # Insert peer into k-bucket

        node_ip = urlparse(uri).hostname
        node_port = urlparse(uri).port
        node_guid = "AFDSDAFDAS"
        # node_guid = self.generate_guid(node_ip, node_port)
        #
        # if (node_ip, node_port, node_guid) not in self._knownNodes:
        #     self._knownNodes.append((node_ip, node_port, node_guid))
        #
        # # Add to routing table
        # aContact = Contact(node_guid, uri)
        # self._routingTable.addContact(aContact)


        if uri not in self._peers:
            # Unknown peer
            self._log.info('Add unknown peer: %s' % uri)
            self.create_peer(uri, pub, node_guid)

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

                if (self._peers[uri]._pub != pub.decode('hex')):
                    self._log.info("Updating public key for node")
                    self._peers[uri]._nickname = nickname
                    self._peers[uri]._pub = pub.decode('hex')

                    self.trigger_callbacks('peer', self._peers[uri])

            if msg_type == 'hello_request':
                # reply only if necessary
                self.send_enc(uri, hello_response(self.get_profile()))

    def on_raw_message(self, serialized):

        try:
            msg = json.loads(serialized)
            self._log.info("receive [%s]" % msg.get('type', 'unknown'))
        except ValueError:
            try:
                msg = json.loads(self._myself.decrypt(serialized))
                self._log.info("Decrypted raw message [%s]"
                               % msg.get('type', 'unknown'))
            except:
                self._log.info("incorrect msg ! %s..."
                               % self._myself.decrypt(serialized))
                traceback.print_exc()
                return

        msg_type = msg.get('type')
        msg_uri = msg.get('uri')

        if msg_type != '':

            if msg_type.startswith('hello') and msg_uri:
                self.init_peer(msg)
                for uri, pub in msg.get('peers', {}).iteritems():
                    # Do not add yourself as a peer
                    if uri != self._uri:
                        self.init_peer({'uri': uri, 'pub': pub})
                self._log.info("Update peer table [%s peers]" % len(self._peers))

            elif msg_type == 'goodbye' and msg_uri:
                self._log.info("Received goodbye from %s" % msg_uri)
                self.remove_peer(msg_uri)

            else:
                self.on_message(msg)
