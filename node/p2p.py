import json
import logging
from collections import defaultdict
import traceback

from zmq.eventloop import ioloop
import zmq
from multiprocessing import Process, Queue
from threading import Thread
ioloop.install()
import tornado
import constants

from protocol import goodbye
import network_util
import hashlib
import routingtable
import datastore
from urlparse import urlparse

# Connection to one peer
class PeerConnection(object):
    def __init__(self, transport, address, guid):
        # timeout in seconds
        self._timeout = 10
        self._transport = transport
        self._address = address
        self._guid = guid
        self._log = logging.getLogger(self.__class__.__name__)

    def create_socket(self):
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REQ)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.connect(self._address)

    def cleanup_socket(self):
        self._socket.close()

    def send(self, data):
        self.send_raw(json.dumps(data))

    def send_raw(self, serialized):
        Thread(target=self._send_raw, args=(serialized,)).start()
        pass

    def _send_raw(self, serialized):

        # pyzmq sockets are not threadsafe,
        # they have to run in a separate process
        queue = Queue()
        # queue element is false if something went wrong and the peer
        # has to be removed

        p = Process(target=self._send_raw_process, args=(serialized, queue))
        p.start()
        if not queue.get():
            self._log.info("Peer %s timed out." % self._address)
            print 'got here'
            self._transport.remove_peer(self._address, self._guid)

        p.join()

    def _send_raw_process(self, serialized, queue):

        self.create_socket()
        self._socket.send(serialized)

        poller = zmq.Poller()
        poller.register(self._socket, zmq.POLLIN)
        if poller.poll(self._timeout * 3000):
            msg = self._socket.recv()
            self.on_message(msg)
            self.cleanup_socket()
            queue.put(True)

        else:
            self._log.info("Node timed out: %s" % self._address)
            self.cleanup_socket()
            queue.put(False)


    def on_message(self, msg, callback=None):
        self._log.info("Message received: %s" % msg)


# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, my_ip, my_port, my_guid):
        self._peers = {}
        self._callbacks = defaultdict(list)
        self._port = my_port
        self._ip = my_ip
        self._guid = my_guid
        self._uri = 'tcp://%s:%s' % (self._ip, self._port)

        # Routing table
        self._routingTable = routingtable.OptimizedTreeRoutingTable(self.guid)
        self._dataStore = datastore.MongoDataStore()
        self._knownNodes = []


        self._log = logging.getLogger(self.__class__.__name__)
        # signal.signal(signal.SIGTERM, lambda x, y: self.broadcast_goodbye())

    def add_callback(self, section, callback):
        self._callbacks[section].append(callback)



    def trigger_callbacks(self, section, *data):
        for cb in self._callbacks[section]:
            cb(*data)
        if not section == 'all':
            for cb in self._callbacks['all']:
                cb(*data)

    def get_profile(self):
        return {'type': 'hello_request', 'uri': self._uri}

    def join_network(self, seed_uri, seed_guid):

        self.listen() # Turn on zmq socket

        if seed_uri:

            self._log.info('Initializing Seed Peer(s): [%s %s]' % (seed_uri, seed_guid))
            # Turning off peers
            #self.init_peer({'uri': seed_uri, 'guid':seed_guid})

            ip = urlparse(seed_uri).hostname
            port = urlparse(seed_uri).port


            if (ip, port, seed_guid) not in self._knownNodes:
                self._knownNodes.append((ip, port, seed_guid))

            # Add to routing table
            self.addCryptoPeer(seed_uri, '02ca00209fe518b9f13a387a61bafa0f49f8bea416662e7bdc87b5f03a6a534c8b5a6816002004cb93220f7ae28ceafbdcdb8679684adcf5e8906f7987e2b07fe8e2ba88f009', seed_guid)

            self._iterativeFind(self._guid, self._knownNodes, 'findNode')


            # Periodically refresh buckets
            loop = tornado.ioloop.IOLoop.instance()
            refreshCB = tornado.ioloop.PeriodicCallback(self._refreshNode, constants.refreshTimeout, io_loop=loop)
            refreshCB.start()



    def listen(self):
        t = Thread(target=self._listen)
        t.setDaemon(True)
        t.start()

    def _listen(self):
        self._log.info("Listening at: %s:%s" % (self._ip, self._port))
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REP)

        if network_util.is_loopback_addr(self._ip):
            # we are in local test mode so bind that socket on the
            # specified IP
            self._socket.bind(self._uri)
        else:
            try:
              self._socket.bind('tcp://*:%s' % self._port)
            except:
              pass

        while True:
            message = self._socket.recv()
            self.on_raw_message(message)
            self._socket.send(json.dumps({'type': 'ok'}))

    def closed(self, *args):
        self._log.info("client left")

    def _init_peer(self, msg):
        uri = msg['uri']

        if uri not in self._peers:
            self._peers[uri] = CryptoPeerConnection(self, uri)

    def remove_peer(self, uri, guid):
        self._log.info("Removing peer %s", uri)
        ip = urlparse(uri).hostname
        port = urlparse(uri).port
        if (ip, port, guid) in self._shortlist:
            self._shortlist.remove((ip, port, guid))


        self._log.info('Removed')



        # try:
        #     del self._peers[uri]
        #     msg = {
        #         'type': 'peer_remove',
        #         'uri': uri
        #     }
        #     self.trigger_callbacks(msg['type'], msg)
        #
        # except KeyError:
        #     self._log.info("Peer %s was already removed", uri)



    def send(self, data, send_to=None):

        self._log.info("Outgoing Data: %s" % data);

        # Directed message
        if send_to:

            for peer in self._activePeers:
              print peer._address,peer._pub
              if peer._guid == send_to:
                print 'tested here'

            if peer:
              print peer
              if peer.send(data):
                self._log.info('Message sent successfully')
              else:

                self._log.info('Problem sending message %s ' % data)

            return

        # Broadcast to close peers
        for peer in self._activePeers:
            try:

                data['senderGUID'] = self._guid
                if peer._pub:
                    peer.send(data)
                else:
                    serialized = json.dumps(data)
                    peer.send_raw(serialized)
            except:
                self._log.info("Error sending over peer!")
                traceback.print_exc()

    def broadcast_goodbye(self):
        self._log.info("Broadcast goodbye")
        msg = goodbye({'uri': self._uri})
        self.send(msg)

    def on_message(self, msg):

        # here goes the application callbacks
        # we get a "clean" msg which is a dict holding whatever
        self._log.info("Data received: %s" % msg)

        if not self._routingTable.getContact(msg['senderGUID']):
            # Add to contacts if doesn't exist yet
            self.addCryptoPeer(msg['uri'], msg['pubkey'], msg['senderGUID'])

        self.trigger_callbacks(msg['type'], msg)


    def on_raw_message(self, serialized):
        self._log.info("connected " + str(len(serialized)))
        try:
            msg = json.loads(serialized[0])
        except:
            self._log.info("incorrect msg! " + serialized)
            return

        msg_type = msg.get('type')
        if msg_type == 'hello_request' and msg.get('uri'):
            self.init_peer(msg)
        else:
            self.on_message(msg)

    def valid_peer_uri(self, uri):
        try:
            [self_protocol, self_addr, self_port] = \
                network_util.uri_parts(self._uri)
            [other_protocol, other_addr, other_port] = \
                network_util.uri_parts(uri)
        except RuntimeError:
            return False

        if not network_util.is_valid_protocol(other_protocol)  \
                or not network_util.is_valid_port(other_port):
            return False

        if network_util.is_private_ip_address(self_addr):
            if not network_util.is_private_ip_address(other_addr):
                self._log.warning(('Trying to connect to external '
                                   'network with a private ip address.'))
        else:
            if network_util.is_private_ip_address(other_addr):
                return False

        return True
