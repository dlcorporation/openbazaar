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
from protocol import goodbye
import network_util
from urlparse import urlparse
import sys


class PeerConnection(object):
    def __init__(self, transport, address):
        # timeout in seconds
        self._timeout = 10
        self._transport = transport
        self._address = address
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

        def cb(msg):
            print 'callback'
            self.on_message(msg)
            if callback is not None:
                callback(msg)

        self._stream.on_recv(cb)


    def on_message(self, msg, callback=lambda msg: None):
        self._log.info("Message received: %s" % msg)
        callback()


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

    def listen(self, pubkey):
        #t = Thread(target=self._listen, args=(pubkey,))
        #t.setDaemon(True)
        #t.start()
        self._listen(pubkey)

    def _listen(self, pubkey):
        self._log.info("Listening at: %s:%s" % (self._ip, self._port))
        ctx = zmq.Context()
        socket = ctx.socket(zmq.REP)

        if network_util.is_loopback_addr(self._ip):
            # we are in local test mode so bind that socket on the
            # specified IP
            socket.bind(self._uri)
        else:
            socket.bind('tcp://*:%s' % self._port)

        #while True:

        stream = zmqstream.ZMQStream(socket, io_loop=ioloop.IOLoop.current())
        print 'stream: %s' % stream

        def handle_recv(message):
            for msg in message:
                print msg
                self.on_raw_message(msg)



            self._log.info('Sending back OK')
            #self._socket.send(json.dumps({'type': 'ok', 'senderGUID': self._guid, 'pubkey': pubkey}), flags=zmq.NOBLOCK)
            stream.send(json.dumps({'type': 'ok', 'senderGUID': self._guid, 'pubkey': pubkey}))

        stream.on_recv(handle_recv)

            # t = Thread(target=self.handle_raw_message, args=(message,))
            # t.setDaemon(True)
            # t.start()



    def handle_raw_message(self, message):
        self.on_raw_message(message)

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
        # del self._peers[uri]
        #     msg = {
        #         'type': 'peer_remove',
        #         'uri': uri
        #     }
        #     self.trigger_callbacks(msg['type'], msg)
        #
        # except KeyError:
        #     self._log.info("Peer %s was already removed", uri)


    def send(self, data, send_to=None):

        self._log.info("Outgoing Data: %s" % data)

        # Directed message
        if send_to is not None:

            peer = self._dht._routingTable.getContact(send_to)

            new_peer = self._dht._transport.get_crypto_peer(peer._guid, peer._address, peer._pub)

            new_peer.send(data)
            # for peer in self._dht._activePeers:
            #
            #     if peer._guid == send_to:
            #         self._log.info('Found a matching peer: %s' % peer._guid)
            #
            #
            #         peer.send(data)
            #
            #         self._log.debug('Sent message: %s ' % data)

            return

        else:
            # FindKey and then send

            for peer in self._dht._activePeers:
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
        self._log.info("[On Message] Data received: %s" % msg)

        # if not self._routingTable.getContact(msg['senderGUID']):
        # Add to contacts if doesn't exist yet
        #self._addCryptoPeer(msg['uri'], msg['senderGUID'], msg['pubkey'])
        if msg['type'] != 'ok':
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
