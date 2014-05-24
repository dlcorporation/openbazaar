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

    def on_message(self, msg):
        # this are just acks
        pass


class CryptoTransportLayer(TransportLayer):

    def __init__(self, my_ip, my_port, market_id):

        TransportLayer.__init__(self, my_ip, my_port)

        self._myself = ec.ECC(curve='secp256k1')

        self.nick_mapping = {}

        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar

        self.settings = self._db.settings.find_one({'id':"%s"%market_id})
        self.market_id = market_id

        # Set up callbacks for pinging peers
        self.add_callback('ping', self._on_ping)
        self.add_callback('pong', self._on_pong)

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
            self.settings = self._db.settings.find_one({'id':"%s"%market_id})

        self._log = logging.getLogger(self.__class__.__name__)

    def _on_ping(self, peer):
      uri = peer['uri']
      print uri
      self._peers[uri].send_raw(json.dump({"type":"pong", "guid": self._guid}))
      self._log.info("Got a ping")

    def _on_pong(self, msg):


      self._log.info("PONG")

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

        self.settings = self._db.settings.find_one({'id':"%s"%self.market_id})
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
        self._log.info('Initialize Peer: %s' % msg)

        uri = msg['uri']
        pub = msg.get('pub')
        nickname = msg.get('nickname')
        msg_type = msg.get('type')

        if not self.valid_peer_uri(uri):
            self._log.info("Peer " + uri + " is not valid.")
            return

        node_ip = urlparse(uri).hostname
        node_port = urlparse(uri).port
        node_guid = hashlib.new('sha1')
        node_guid.update("%s:%s" % (node_ip, node_port))
        node_guid = node_guid.digest().encode('hex')

        if (node_ip, node_port, node_guid) not in self._knownNodes:
            self._knownNodes.append((node_ip, node_port, node_guid))

        if uri not in self._peers:
            # unknown peer
            self._log.info('Create New Peer: %s' % uri)
            self.create_peer(uri, pub, node_guid)


            if not msg_type:
                self.send_enc(uri, hello_request(self.get_profile()))
            elif msg_type == 'hello_request':
                self.send_enc(uri, hello_response(self.get_profile()))

        else:
            # known peer
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

    def extendShortlist(responseTuple):
          """ @type responseMsg: kademlia.msgtypes.ResponseMessage """
          # The "raw response" tuple contains the response message, and the originating address info
          responseMsg = responseTuple[0]
          originAddress = responseTuple[1] # tuple: (ip adress, udp port)
          # Make sure the responding node is valid, and abort the operation if it isn't
          if responseMsg.nodeID in activeContacts or responseMsg.nodeID == self.id:
              return responseMsg.nodeID

          # Mark this node as active
          if responseMsg.nodeID in shortlist:
              # Get the contact information from the shortlist...
              aContact = shortlist[shortlist.index(responseMsg.nodeID)]
          else:
              # If it's not in the shortlist; we probably used a fake ID to reach it
              # - reconstruct the contact, using the real node ID this time
              aContact = Contact(responseMsg.nodeID, originAddress[0], originAddress[1], self._protocol)
          activeContacts.append(aContact)
          # This makes sure "bootstrap"-nodes with "fake" IDs don't get queried twice
          if responseMsg.nodeID not in alreadyContacted:
              alreadyContacted.append(responseMsg.nodeID)
          # Now grow extend the (unverified) shortlist with the returned contacts
          result = responseMsg.response
          #TODO: some validation on the result (for guarding against attacks)
          # If we are looking for a value, first see if this result is the value
          # we are looking for before treating it as a list of contact triples
          if findValue == True and type(result) == dict:
              # We have found the value
              findValueResult[key] = result[key]
          else:
              if findValue == True:
                  # We are looking for a value, and the remote node didn't have it
                  # - mark it as the closest "empty" node, if it is
                  if 'closestNodeNoValue' in findValueResult:
                      if self._routingTable.distance(key, responseMsg.nodeID) < self._routingTable.distance(key, activeContacts[0].id):
                          findValueResult['closestNodeNoValue'] = aContact
                  else:
                      findValueResult['closestNodeNoValue'] = aContact
              for contactTriple in result:
                  if isinstance(contactTriple, (list, tuple)) and len(contactTriple) == 3:
                      testContact = Contact(contactTriple[0], contactTriple[1], contactTriple[2], self._protocol)
                      if testContact not in shortlist:
                          shortlist.append(testContact)
          return responseMsg.nodeID

    def _iterativeFind(self, key, startupShortlist=None, call='findNode'):

      # Determine if we're looking for a node or a key
      if call != 'findNode':
        findValue = True
      else:
        findValue = False

      shortlist = []

      if startupShortlist == None:
        shortlist = self._routingTable.findCloseNodes(key, constants.alpha)
        if key != self._guid:
          self._routingTable.touchKBucket(key)
        if len(shortlist) == 0:
          fakeDf = defer.Deferred()
          fakeDf.callback([])
          return fakeDf
      else:
        shortlist = startupShortlist

      activeProbes = []
      alreadyContacted = []
      activeContacts = []
      pendingIterationCalls = []
      prevClosestNode = [None]
      findValueResult = {}
      slowNodeCount = [0]

      def searchIteration():
        slowNodeCount[0] = len(activeProbes)

        # Sort closest to farthest
        activeContacts.sort(lambda firstContact, secondContact, targetKey=key: cmp(self._routingTable.distance(firstContact.id, targetKey), self._routingTable.distance(secondContact.id, targetKey)))

        while len(pendingIterationCalls):
          del pendingIterationCalls[0]

        if key in findValueResult:
          #outerDf.callback(findValueResult)
          return findValueResult

        elif len(activeContacts) and findValue == False:
          if (len(activeContacts) >= constants.k) or (activeContacts[0] == prevClosestNode[0] and len(activeProbes) == slowNodeCount[0]):
            #outerDf.callback(activeContacts)
            return activeContacts

        if len(activeContacts):
          prevClosestNode[0] = activeContacts[0]

        contactedNow = 0

        shortlist.sort(lambda firstContact, secondContact, targetKey=key: cmp(self._routingTable.distance(firstContact.id, targetKey), self._routingTable.distance(secondContact.id, targetKey)))

        prevShortlistLength = len(shortlist)
        print shortlist
        for node in shortlist:
          if node[2] not in alreadyContacted:
              activeProbes.append(node[2])

              #rpcMethod = getattr(node, rpc)
              #df = rpcMethod(key, rawResponse=True)

              # Ping peer
              uri = "tcp://%s:%s" % (node[0], node[1])
              msg = {"type":"ping", "uri":self._uri}
              print msg
              self._peers[uri].send_raw(json.dumps(msg))


              # df.addCallback(extendShortlist)
              # df.addErrback(removeFromShortlist)
              # df.addCallback(cancelActiveProbe)

              # Send method call which returns some raw response
              # and send it to extendShortlist

              #alreadyContacted.append(node[2])
              #contactedNow += 1

        #   if contactedNow == constants.alpha:
        #       break
        # if len(activeProbes) > slowNodeCount[0] \
        #     or (len(shortlist) < constants.k and len(activeContacts) < len(shortlist) and len(activeProbes) > 0):
        #     #print '----------- scheduling next call -------------'
        #     # Schedule the next iteration if there are any active calls (Kademlia uses loose parallelism)
        #     call = twisted.internet.reactor.callLater(constants.iterativeLookupDelay, searchIteration) #IGNORE:E1101
        #     pendingIterationCalls.append(call)
        # # Check for a quick contact response that made an update to the shortList
        # elif prevShortlistLength < len(shortlist):
        #     # Ensure that the closest contacts are taken from the updated shortList
        #     searchIteration()
        # else:
        #     #print '++++++++++++++ DONE (logically) +++++++++++++\n\n'
        #     # If no probes were sent, there will not be any improvement, so we're done
        #     outerDf.callback(activeContacts)





      #outerDf = defer.Deferred()

      # Start searching
      results = searchIteration()

      return results


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
