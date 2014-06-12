import json
import logging
import routingtable
import datastore
import p2p
import constants
import hashlib
import os
import time
from urlparse import urlparse
import tornado
from multiprocessing import Process, Queue
from threading import Thread


class DHT():

  def __init__(self, market_id, settings):


    self._log = logging.getLogger('[%s] %s' % (market_id, self.__class__.__name__))
    self._settings = settings

    self._knownNodes = []

    self._searches = []

    self._searchKeys = {}
    self._activePeers = []

    self._republishThreads = []

    # Routing table
    self._routingTable = routingtable.OptimizedTreeRoutingTable(self._settings['guid'])
    self._dataStore = datastore.MongoDataStore()



  def start(self, seed_peer):
    ip = seed_peer._ip
    port = seed_peer._port
    self.add_known_node((ip, port, seed_peer._guid))
    self.add_active_peer(seed_peer)

    self._iterativeFind(self._settings['guid'], self._knownNodes, 'findNode')

    # Periodically refresh buckets
    loop = tornado.ioloop.IOLoop.instance()
    refreshCB = tornado.ioloop.PeriodicCallback(self._refreshNode, constants.refreshTimeout, io_loop=loop)
    refreshCB.start()


  def add_active_peer(self, new_peer):

    if new_peer._guid == self._settings['guid']:
      self._log.info('Trying to add yourself to active peers')
      return

    foundPeer = False
    for idx, peer in enumerate(self._activePeers):
      if peer._guid == new_peer._guid:
        foundPeer = True
        peer._pub = new_peer._pub
        self._activePeers[idx] = peer
    if not foundPeer:
      self._log.info('Adding an active Peer: %s' % new_peer._guid)
      self._activePeers.append(new_peer)

    if not self._routingTable.getContact(new_peer._guid):
        self._log.info('Adding contact to routing table')
        self._routingTable.addContact(new_peer)



  def add_known_node(self, node):

    if node not in self._knownNodes:
      #self._log.debug('Adding known node: %s' % node)
      self._knownNodes.append(node)



  def _on_ping(self, msg):
     guid = msg['senderGUID']
     uri = msg['uri']
     pubkey = msg['pubkey']
     peerConnection.send_raw(json.dumps({"type":"pong", "senderGUID":transport[1], "uri":transport[0], "pubkey":transport[2]}))


  def get_known_nodes(self):

    return self._knownNodes


  def _on_findNode(self, msg):

    self._log.info('Received a findNode request: %s' % msg)

    guid = msg['senderGUID']
    key = msg['key']
    uri = msg['uri']
    pubkey = msg['pubkey']
    findID = msg['findID']
    newContact = msg['new_peer']
    msg['new_peer'] = None

    # Add contact to routing table if doesn't exist yet
    if not self._routingTable.getContact(guid):
        self._routingTable.addContact(newContact)


    if msg['type'] == 'findValue' and key in self._dataStore and self._dataStore[key] != None:
        # Found key in local datastore
        newContact.send_raw(json.dumps({"type":"findNodeResponse","senderGUID":newContact._transport.guid, "uri":newContact._transport._uri, "pubkey":newContact._transport.pubkey, "foundKey":self._dataStore[key], "findID":findID}))

    else:
        # Search for contact in routing table
        foundContact = self._routingTable.getContact(key)

        if foundContact:
          self._log.info('Found the node')
          foundNode = (foundContact._guid, foundContact._address, foundContact._pub)
          newContact.send_raw(json.dumps({"type":"findNodeResponse","senderGUID":newContact._transport.guid,"uri":newContact._transport._uri, "pubkey":newContact._transport.pubkey,"foundNode":foundNode, "findID":findID}))
        else:
          contacts = self._routingTable.findCloseNodes(key, constants.k, guid)
          contactTriples = []
          for contact in contacts:
              contactTriples.append( (contact._guid, contact._address, contact._pub) )

          newContact.send_raw(json.dumps({"type":"findNodeResponse","senderGUID":newContact._transport.guid,"uri":newContact._transport._uri, "pubkey":newContact._transport.pubkey,"foundNodes":contactTriples, "findID":findID}))


  def _on_findNodeResponse(self, transport, msg):

    self._log.info('Received a findNode Response: %s' % msg)

    # Update pubkey if necessary - happens for seed server
    # localPeer = next((peer for peer in self._activePeers if peer._guid == msg['senderGUID']), None)

    # Update existing peer's pubkey if active peer
    for idx, peer in enumerate(self._activePeers):
      if peer._guid == msg['senderGUID']:
        peer._pub = msg['pubkey']
        self._activePeers[idx] = peer

    # If key was found by this node then
    if 'foundKey' in msg.keys():
      self._log.debug('Found the key-value pair. Executing callback.')

      self._searches[msg['findID']]._callback(msg['foundKey'])

      # Remove active search
      del self._searches[msg['findID']]

    else:

      if 'foundNode' in msg.keys():

        foundNode = msg['foundNode']
        self._log.debug('Found the node you were looking for: %s' % foundNode)

        # Add foundNode to active peers list and routing table
        new_peer = transport.getCryptoPeer(foundNode[0], foundNode[1], foundNode[2])

        for idx, search in enumerate(self._searches):
          if search._findID == msg['findID']:

            # Execute callback
            if search._callback != None:
              search._callback([new_peer])

            # Clear search
            del self._searches[idx]

      else:

        # Add any close nodes found to the shortlist
        self.extendShortlist(transport, msg)

        findID = msg['findID']
        for s in self._searches:
          if s._findID == findID:
            search = s

        # Remove active probe to this node for this findID
        search_ip = urlparse(msg['uri']).hostname
        search_port = urlparse(msg['uri']).port
        search_guid = msg['senderGUID']
        search_tuple = (search_ip, search_port, search_guid)
        for idx, probe in enumerate(search._activeProbes):
          if probe == search_tuple:
            del search._activeProbes[idx]
        self._log.debug('Find Node Response - Active Probes After: %s' % search._activeProbes)

        # Add this to already contacted list
        search._alreadyContacted.append(search_tuple)
        self._log.debug('Already Contacted: %s' % search._alreadyContacted)

        # If we added more to shortlist then keep searching
        if search._prevShortlistLength < len(search._shortlist):
          self._searchIteration(search)
        else:
          search._callback(search._findID)


  def _refreshNode(self):
      """ Periodically called to perform k-bucket refreshes and data
      replication/republishing as necessary """

      self._refreshRoutingTable()
      self._republishData()


  def _refreshRoutingTable(self):
      self._log.debug('Started Refreshing Routing Table')
      nodeIDs = self._routingTable.getRefreshList(0, False)

      def searchForNextNodeID(dfResult=None):
          if len(nodeIDs) > 0:
              self._log.info('Refreshing Routing Table')
              searchID = nodeIDs.pop()
              self.iterativeFindNode(searchID)
              searchForNextNodeID()
          else:
              # If this is reached, we have finished refreshing the routing table
              return

      # Start the refreshing cycle
      searchForNextNodeID()

  def _republishData(self, *args):
      Thread(target=self._threadedRepublishData, args=()).start()


  def _threadedRepublishData(self, *args):
      """ Republishes and expires any stored data (i.e. stored
      C{(key, value pairs)} that need to be republished/expired

      This method should run in a deferred thread
      """
      self._log.debug('Republishing Data')
      expiredKeys = []

      #self._dataStore.setItem('23e192e685d3ca73d5d56d2f1c85acb1346ba177', 'Brian', int(time.time()), int(time.time()), '23e192e685d3ca73d5d56d2f1c85acb1346ba176' )

      for key in self._dataStore.keys():

          # Filter internal variables stored in the datastore
          if key == 'nodeState':
              continue

          now = int(time.time())
          originalPublisherID = self._dataStore.originalPublisherID(key)
          age = now - self._dataStore.originalPublishTime(key) + 500000

          self._log.debug('oPubID: %s, age: %s' % (originalPublisherID, age))
          #print '  node:',ord(self.id[0]),'key:',ord(key[0]),'orig publishing time:',self._dataStore.originalPublishTime(key),'now:',now,'age:',age,'lastPublished age:',now - self._dataStore.lastPublished(key),'original pubID:', ord(originalPublisherID[0])

          if originalPublisherID == self._settings['guid']:
              # This node is the original publisher; it has to republish
              # the data before it expires (24 hours in basic Kademlia)
              if age >= constants.dataExpireTimeout:
                  self._log.debug('Republishing key: %s' % key)
                  Thread(target=self.iterativeStore, args=(key,self._dataStore[key],)).start()
                  #self.iterativeStore(key, self._dataStore[key])
                  #twisted.internet.reactor.callFromThread(self.iterativeStore, key, self._dataStore[key])
          else:
              # This node needs to replicate the data at set intervals,
              # until it expires, without changing the metadata associated with it
              # First, check if the data has expired
              if age >= constants.dataExpireTimeout:
                  # This key/value pair has expired (and it has not been republished by the original publishing node
                  # - remove it
                  expiredKeys.append(key)
              elif now - self._dataStore.lastPublished(key) >= constants.replicateInterval:
                  # ...data has not yet expired, and we need to replicate it
                  Thread(target=self.iterativeStore, args=(key,self._dataStore[key],originalPublisherID,age,)).start()

      for key in expiredKeys:
          del self._dataStore[key]



  def extendShortlist(self, transport, response):

        for s in self._searches:
          if s._findID == response['findID']:
            search = s

        self._log.debug('Short list before: %s' % search._shortlist)
        print response

        for node in response['foundNodes']:

          node_guid, node_uri, node_pubkey = node
          node_ip = urlparse(node_uri).hostname
          node_port = urlparse(node_uri).port
          cryptopeer = transport.getCryptoPeer(node_guid, node_uri, node_pubkey)

          # Add to shortlist
          if (node_ip, node_port, node_guid) not in search._shortlist:
            search._shortlist.append((node_ip, node_port, node_guid))

          if cryptopeer in self._activePeers or node_guid == self._settings['guid']:
            # Already an active peer or it's myself
            continue
          else:
            self._log.debug('Adding new peer to active peers list: %s' % node)

            if cryptopeer._guid != self._settings['guid']:
              self.add_active_peer(cryptopeer)

        self._log.debug('Short list after: %s' % search._shortlist)

        # # Check if node is in active list or if it's yourself
        # if response['']
        #
        #
        #
        #
        #
        # findValue = False # Need to make this dynamic
        #
        # uri = response['uri']
        # ip = urlparse(uri).hostname
        # port = urlparse(uri).port
        # guid = response['senderGUID']
        # pubkey = response['pubkey']
        # findID = response['findID']
        # result = response['findValue']
        #
        #
        #
        #
        # # Mark this node as active
        # self._log.debug('Start Shortlist: %s' % self._shortlist[findID])
        # # if findID in self._shortlist.keys() and (ip, port, guid) in self._shortlist[findID]:
        # #     self._log.info('Getting node from shortlist')
        # #     # Get the contact information from the shortlist...
        # #     #aContact = shortlist[shortlist.index(responseMsg.nodeID)]
        # #     #aPeer = PeerConnection(self, uri, guid)
        # # else:
        # #     self._log.info('Node is not in the shortlist')
        # #     # If it's not in the shortlist; we probably used a fake ID to reach it
        # #     # - reconstruct the contact, using the real node ID this time
        # #     #aContact = Contact(nodeID, responseTuple['uri'], responseTuple['uri'], self._protocol)
        # #     #aPeer = PeerConnection(self, uri, guid)
        #
        #
        # # for aPeer in result:
        # #   for peer in self._activePeers:
        # #     if peer._guid == aPeer[0] and newPeer._transport.guid:
        # #       self._log.debug('Adding a new active peer')
        # #       aPeer = newPeer.getCryptoPeer(aPeer[1], aPeer[2], aPeer[0])
        # #       self._activePeers.append(aPeer)
        # #       self._log.debug('Active Peers: %s' % self._activePeers)
        #
        # # This makes sure "bootstrap"-nodes with "fake" IDs don't get queried twice
        # if guid not in self._alreadyContacted[findID]:
        #     self._log.debug('Add to Already Connected List')
        #     self._alreadyContacted[findID].append(guid)
        #
        # self._log.debug('Already Contacted: %s' % self._alreadyContacted)
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
        #
        #     # Got some nodes back rather than a result
        #     for node in result:
        #
        #         self._log.debug('Close Node Returned: %s' % node)
        #
        #         ip = urlparse(node[1]).hostname
        #         port = urlparse(node[1]).port
        #         guid = node[0]
        #
        #         testContact = (ip, port, guid)
        #
        #         if testContact not in self._shortlist:
        #             self._shortlist[findID].append(testContact)
        #
        # self._log.debug('Active Peers: %s' % self._activePeers)
        # self._log.debug('Shortlist Updated: %s' % self._shortlist[findID])



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

      self.iterativeFindNode(key, self.storeKeyValue)

      # Find k nodes closest to the key...
      #df = self.iterativeFindNode(key)
      # ...and send them STORE RPCs as soon as they've been found
      #df.addCallback(executeStoreRPCs)
      #return df

  def storeKeyValue(self, msg):
      print 'Store the KVS: %s' % msg

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

  def iterativeFindNode(self, key, callback=None):
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
      self._iterativeFind(key, callback=callback)


  def _iterativeFind(self, key, startupShortlist=None, call='findNode', callback=None):

    # Create a new search object
    new_search = DHTSearch(key, call, callback=callback)
    self._searches.append(new_search)

    # Determine if we're looking for a node or a key
    findValue = True if call != 'findNode' else False

    # If search is for your key abandon search
    if not findValue and key == self._settings['guid']:
      return 'You are looking for yourself'

    # If looking for a node check in your active peers list first to prevent unnecessary searching
    if not findValue:
      for node in self._activePeers:
        if node._guid == key:
          return [node]

    if startupShortlist == [] or startupShortlist == None:

      # Retrieve closest nodes adn add them to the shortlist for the search
      closeNodes = self._routingTable.findCloseNodes(key, constants.alpha, self._settings['guid'])
      for closeNode in closeNodes:
        new_search._shortlist.append((closeNode._ip, closeNode._port, closeNode._guid))
      self._log.debug('Updated short list: %s' % new_search._shortlist)

      # Refresh the k-bucket for this key
      if key != self._settings['guid']:
        self._routingTable.touchKBucket(key)

      # Abandon the search if the shortlist has no nodes
      if len(new_search._shortlist) == 0:
        if(callback != None):
          callback([])
        else:
          return []

    else:
      # On startup of the server the shortlist is pulled from the DB
      # TODO: Right now this is just hardcoded to be seed URIs but should pull from db
      new_search._shortlist = startupShortlist

    self._searchIteration(new_search)


  def _searchIteration(self, new_search, findValue=False):

    # Update slow nodes count
    new_search._slowNodeCount[0] = len(new_search._activeProbes)

    # Sort shortlist from closest to farthest
    #self._activePeers.sort(lambda firstContact, secondContact, targetKey=key: cmp(self._routingTable.distance(firstContact._guid, targetKey), self._routingTable.distance(secondContact._guid, targetKey)))
    #new_search._shortlist.sort(lambda firstContact, secondContact, targetKey=key: cmp(self._routingTable.distance(firstContact._guid, targetKey), self._routingTable.distance(secondContact._guid, targetKey)))
    self._activePeers.sort( lambda firstNode, secondNode, targetKey=new_search._key: cmp(self._routingTable.distance(firstNode._guid, targetKey), self._routingTable.distance(secondNode._guid, targetKey)))

    # while len(self._pendingIterationCalls):
    #   del self._pendingIterationCalls[0]


    if new_search._key in new_search._findValueResult:
      return new_search._findValueResult
    elif len(new_search._shortlist) and findValue == False:

      # If you have more k amount of nodes in your shortlist then stop
      # or ...
      if (len(new_search._shortlist) >= constants.k) or (new_search._shortlist[0] == new_search._prevClosestNode and len(new_search._activeProbes) == new_search._slowNodeCount[0]):
        new_search._callback(new_search._shortlist)
        return

    # Update closest node
    if len(self._activePeers):
      closestPeer = self._activePeers[0]
      closestPeer_ip = urlparse(closestPeer._address).hostname
      closestPeer_port = urlparse(closestPeer._address).port
      new_search._prevClosestNode = (closestPeer_ip, closestPeer_port, closestPeer._guid)
      print 'Previous Closest Node',new_search._prevClosestNode


    # Sort short list again
    new_search._shortlist.sort(lambda firstNode, secondNode, targetKey=new_search._key: cmp(self._routingTable.distance(firstNode[2], targetKey), self._routingTable.distance(secondNode[2], targetKey)))

    new_search._prevShortlistLength = len(new_search._shortlist)

    #
    for node in new_search._shortlist:
      if node not in new_search._alreadyContacted:

          # See if search was cancelled
          if not self.activeSearchExists(new_search._findID):
            return

          new_search._activeProbes.append(node)

          contact = self._routingTable.getContact(node[2])

          if contact:

            msg = {"type":"findNode", "uri":contact._transport._uri, "senderGUID":contact._transport._guid, "key":new_search._key, "findValue":findValue, "findID":new_search._findID, "pubkey":contact._transport.pubkey}
            contact.send_raw(json.dumps(msg))

            new_search._contactedNow += 1

          else:
            self._log.error('No contact was found for this guid: %s' % node[2])

      if new_search._contactedNow == constants.alpha:
          break

  def activeSearchExists(self, findID):

    activeSearchExists = False
    for search in self._searches:
      if findID == search._findID:
        return True
    if not activeSearchExists:
      return False


class DHTSearch():

  def __init__(self, key, call="findNode", callback=None):

    self._key = key                       # Key to search for
    self._call = call                     # Either findNode or findValue depending on search
    self._callback = callback             # Callback for when search finishes
    self._shortlist = []                  # List of nodes that are being searched against
    self._activeProbes = []               #
    self._alreadyContacted = []           # Nodes are added to this list when they've been sent a findXXX action
    self._prevClosestNode = None          # This is updated to be the closest node found during search
    self._findValueResult = {}            # If a findValue search is found this is the value
    self._pendingIterationCalls = []      #
    self._slowNodeCount = [0]             #
    self._contactedNow = 0                # Counter for how many nodes have been contacted
    self._dhtCallbacks = []               # Callback list
    self._prevShortlistLength = 0

    # Create a unique ID (SHA1) for this iterativeFind request to support parallel searches
    self._findID = hashlib.sha1(os.urandom(128)).hexdigest()
