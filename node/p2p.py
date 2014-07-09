import json
import logging
from collections import defaultdict
import traceback
from multiprocessing import Process, Queue
from threading import Thread
from random import randint

from zmq.eventloop import ioloop, zmqstream
import zmq

ioloop.install()
import tornado
from protocol import goodbye, hello_request
import network_util
from urlparse import urlparse
import sys, time, random
from ws import ProtocolHandler


class PeerConnection(object):
    def __init__(self, transport, address):
        # timeout in seconds
        self._timeout = 10
        self._transport = transport
        self._address = address
        self._responses_received = {}
        self._log = logging.getLogger('[%s] %s' % (self._transport._market_id, self.__class__.__name__))
        self.create_socket()

    def create_socket(self):
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REQ)
        self._socket.setsockopt(zmq.LINGER, 0)
        #self._socket.setsockopt(zmq.SOCKS_PROXY, "127.0.0.1:9051");
        self._socket.connect(self._address)
        self._stream = zmqstream.ZMQStream(self._socket, io_loop=ioloop.IOLoop.current())

    def cleanup_socket(self):
        self._socket.close()

    def send(self, data, callback):
        msg = self.send_raw(json.dumps(data), callback)
        return msg

    def send_raw(self, serialized, callback=lambda msg: None):

        self._stream.send(serialized)

        # Generate message ID
        message_id = random.randint(0, 1000000)

        self._responses_received[message_id] = False

        def cb(msg):
            self._log.debug('callback received: %s ' % message_id)
            if self._responses_received.has_key(message_id):
                del self._responses_received[message_id]

            #XXX: Might be a good idea to remove peer if pubkey changes. This
            # should be handled in CrytpoPeerConnection.
            if callback is not None:
                callback(msg)

        self._stream.on_recv(cb)

        def remove_dead_peer():
            self._log.debug('Responses Received: %s' % self._responses_received)

            if self._responses_received.has_key(message_id):
                #del self._responses_received[message_id]
                self._log.info('Unreachable Peer. Check your firewall settings. %s' % message_id)
                self._transport._dht.remove_active_peer(self._address)
                callback(False)

        # Set timer for checking if peer alive
        ioloop.IOLoop.instance().add_timeout(time.time() + 10, remove_dead_peer)

# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, market_id, my_ip, my_port, my_guid):

        self._peers = {}
        self._callbacks = defaultdict(list)
        self._port = my_port
        self._ip = my_ip
        self._guid = my_guid
        self._market_id = market_id
        self._uri = 'tcp://%s:%s' % (self._ip, self._port)

        self._log = logging.getLogger('[%s] %s' % (market_id, self.__class__.__name__))

    def add_callback(self, section, callback):
        self._callbacks[section].append(callback)

    def trigger_callbacks(self, section, *data):
        # Run all callbacks in specified section
        for cb in self._callbacks[section]:
            cb(*data)

        # Run all callbacks registered under the 'all' section. Don't duplicate
        # calls if the specified section was 'all'.
        if not section == 'all':
            for cb in self._callbacks['all']:
                cb(*data)

    def get_profile(self):
        return hello_request({ 'uri': self._uri })

    def listen(self, pubkey):
        self._log.info("Listening at: %s:%s" % (self._ip, self._port))
        ctx = zmq.Context()
        socket = ctx.socket(zmq.REP)

        if network_util.is_loopback_addr(self._ip):
            # we are in local test mode so bind that socket on the
            # specified IP
            socket.bind(self._uri)
        else:
            socket.bind('tcp://*:%s' % self._port)

        stream = zmqstream.ZMQStream(socket, io_loop=ioloop.IOLoop.current())

        def handle_recv(message):
            for msg in message:
                self._on_raw_message(msg)

            self._log.info('Sending back OK')
            stream.send(json.dumps({'type': 'ok', 'senderGUID': self._guid, 'pubkey': pubkey}))

        stream.on_recv(handle_recv)

    def closed(self, *args):
        self._log.info("client left")

    def _init_peer(self, msg):
        uri = msg['uri']

        if uri not in self._peers:
            self._peers[uri] = PeerConnection(self, uri)

    def remove_peer(self, uri, guid):
        self._log.info("Removing peer %s", uri)
        ip = urlparse(uri).hostname
        port = urlparse(uri).port
        if (ip, port, guid) in self._shortlist:
            self._shortlist.remove((ip, port, guid))

        self._log.info('Removed')



        # try:
        # del self._peers[uri]
        #     msg = {
        #         'type': 'peer_remove',
        #         'uri': uri
        #     }
        #     self.trigger_callbacks(msg['type'], msg)
        #
        # except KeyError:
        #     self._log.info("Peer %s was already removed", uri)


    def send(self, data, send_to=None, callback=lambda msg: None):

        self._log.info("Outgoing Data: %s %s" % (data, send_to))

        # Directed message
        if send_to is not None:
            peer = self._dht._routingTable.getContact(send_to)
            #self._log.debug('%s %s %s' % (peer._guid, peer._address, peer._pub))
            peer.send(data, callback=callback)
            return

        else:
            # FindKey and then send

            for peer in self._dht._activePeers:
                try:
                    data['senderGUID'] = self._guid
                    if peer._pub:
                        peer.send(data, callback)
                    else:
                        serialized = json.dumps(data)
                        peer.send_raw(serialized, callback)
                except:
                    self._log.info("Error sending over peer!")
                    traceback.print_exc()

    def broadcast_goodbye(self):
        self._log.info("Broadcast goodbye")
        msg = goodbye({'uri': self._uri})
        self.send(msg)

    def _on_message(self, msg):

        # here goes the application callbacks
        # we get a "clean" msg which is a dict holding whatever
        self._log.info("[On Message] Data received: %s" % msg)

        # if not self._routingTable.getContact(msg['senderGUID']):
        # Add to contacts if doesn't exist yet
        #self._addCryptoPeer(msg['uri'], msg['senderGUID'], msg['pubkey'])
        if msg['type'] != 'ok':
            self.trigger_callbacks(msg['type'], msg)


    def _on_raw_message(self, serialized):
        self._log.info("connected " + str(len(serialized)))
        try:
            msg = json.loads(serialized[0])
        except:
            self._log.info("incorrect msg! " + serialized)
            return

        msg_type = msg.get('type')
        if msg_type == 'hello_request' and msg.get('uri'):
            self._init_peer(msg)
        else:
            self._on_message(msg)

    def valid_peer_uri(self, uri):
        try:
            [self_protocol, self_addr, self_port] = \
                network_util.uri_parts(self._uri)
            [other_protocol, other_addr, other_port] = \
                network_util.uri_parts(uri)
        except RuntimeError:
            return False

        if not network_util.is_valid_protocol(other_protocol) \
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
