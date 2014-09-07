from collections import defaultdict
from pprint import pformat
from protocol import goodbye, hello_request
from urlparse import urlparse
from zmq.eventloop import ioloop, zmqstream
ioloop.install()  # Gubatron: is this necessary here again, saw it in ws.py?

import json
import logging
import network_util
import traceback
import zlib
import zmq
import socket
import errno


class PeerConnection(object):
    def __init__(self, transport, address):
        # timeout in seconds
        self.timeout = 10
        self.transport = transport
        self.address = address
        self.nickname = ""
        self.responses_received = {}
        self.log = logging.getLogger(
            '[%s] %s' % (self.transport.market_id, self.__class__.__name__)
        )
        self.ctx = zmq.Context()

    def create_zmq_socket(self):
        self.log.info('Creating Socket')
        socket = self.ctx.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)
        # self._socket.setsockopt(zmq.SOCKS_PROXY, "127.0.0.1:9051");
        return socket

    def cleanup_context(self):
        self.ctx.destroy()

    def cleanup_socket(self):
        self._socket.close(0)

    def send(self, data, callback):
        self.send_raw(json.dumps(data), callback)

    def send_raw(self, serialized, callback=lambda msg: None):

        compressed_data = zlib.compress(serialized, 9)

        try:
            s = self.create_zmq_socket()
            try:
                s.connect(self.address)
            except zmq.ZMQError as e:
                if e.errno != errno.EINVAL:
                    raise
                s.ipv6 = True
                s.connect(self.address)

            stream = zmqstream.ZMQStream(s, io_loop=ioloop.IOLoop.current())
            stream.send(compressed_data)

            def cb(stream, msg):
                response = json.loads(msg[0])
                self.log.debug('[send_raw] %s' % pformat(response))

                # Update active peer info

                if 'senderNick' in response and\
                   response['senderNick'] != self.nickname:
                    self.nickname = response['senderNick']

                if callback is not None:
                    self.log.debug('%s' % msg)
                    callback(msg)
                stream.close()

            stream.on_recv_stream(cb)
        except Exception as e:
            self.log.error(e)
            # shouldn't we raise the exception here???? I think not doing this could cause buggy behavior on top
            raise


# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, market_id, my_ip, my_port, my_guid, nickname=None):

        self.peers = {}
        self.callbacks = defaultdict(list)
        self.timeouts = []
        self.port = my_port
        self.ip = my_ip
        self.guid = my_guid
        self.market_id = market_id
        self.nickname = nickname

        try:
            socket.inet_pton(socket.AF_INET6, my_ip)
            my_uri = 'tcp://[%s]:%s' % (self.ip, self.port)
        except socket.error:
            my_uri = 'tcp://%s:%s' % (self.ip, self.port)
        self.uri = my_uri

        self.log = logging.getLogger(
            '[%s] %s' % (market_id, self.__class__.__name__)
        )

    def add_callbacks(self, callbacks):
        for section, callback in callbacks:
            self.callbacks[section] = []
            self.add_callback(section, callback)

    def add_callback(self, section, callback):
        if callback not in self.callbacks[section]:
            self.callbacks[section].append(callback)

    def trigger_callbacks(self, section, *data):
        # Run all callbacks in specified section
        for cb in self.callbacks[section]:
            cb(*data)

        # Run all callbacks registered under the 'all' section. Don't duplicate
        # calls if the specified section was 'all'.
        if not section == 'all':
            for cb in self.callbacks['all']:
                cb(*data)

    def get_profile(self):
        return hello_request({'uri': self.uri})

    def listen(self, pubkey):
        self.log.info("Listening at: %s:%s" % (self.ip, self.port))
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REP)

        if network_util.is_loopback_addr(self.ip):
            try:
                # we are in local test mode so bind that socket on the
                # specified IP
                self.socket.bind(self.uri)
            except Exception as e:
                error_message = "\n\nTransportLayer.listen() error!!!: "
                error_message += "Could not bind socket to " + self.uri
                error_message += " (" + str(e) + ")"
                import platform
                if platform.system() == 'Darwin':
                    error_message += "\n\nPerhaps you have not added a "\
                                     "loopback alias yet.\n"
                    error_message += "Try this on your terminal and restart "\
                                     "OpenBazaar in development mode again:\n"
                    error_message += "\n\t$ sudo ifconfig lo0 alias 127.0.0.2"
                    error_message += "\n\n"
                raise Exception(error_message)

        else:
            try:
                self.socket.ipv6 = True
                self.socket.bind('tcp://[*]:%s' % self.port)
            except AttributeError:
                self.socket.bind('tcp://*:%s' % self.port)

        self.stream = zmqstream.ZMQStream(
            self.socket, io_loop=ioloop.IOLoop.current()
        )

        def handle_recv(message):
            for msg in message:
                self._on_raw_message(msg)
            self.stream.send(
                json.dumps({
                    'type': 'ok',
                    'senderGUID': self.guid,
                    'pubkey': pubkey,
                    'senderNick': self.nickname
                })
            )

        self.stream.on_recv(handle_recv)

    def closed(self, *args):
        self.log.info("client left")

    def _init_peer(self, msg):
        uri = msg['uri']

        if uri not in self.peers:
            self.peers[uri] = PeerConnection(self, uri)

    def remove_peer(self, uri, guid):
        self.log.info("Removing peer %s", uri)
        ip = urlparse(uri).hostname
        port = urlparse(uri).port
        if (ip, port, guid) in self.shortlist:
            self.shortlist.remove((ip, port, guid))

        self.log.info('Removed')

        # try:
        # del self.peers[uri]
        # msg = {
        # 'type': 'peer_remove',
        # 'uri': uri
        #     }
        #     self.trigger_callbacks(msg['type'], msg)
        #
        # except KeyError:
        #     self.log.info("Peer %s was already removed", uri)

    def send(self, data, send_to=None, callback=lambda msg: None):

        self.log.info("Outgoing Data: %s %s" % (data, send_to))
        data['senderNick'] = self.nickname

        # Directed message
        if send_to is not None:
            peer = self.dht.routingTable.getContact(send_to)
            # self.log.debug(
            #     '%s %s %s' % (peer.guid, peer.address, peer._pub)
            # )
            peer.send(data, callback=callback)
            return

        else:
            # FindKey and then send

            for peer in self.dht.activePeers:
                try:
                    data['senderGUID'] = self.guid
                    data['pubkey'] = self.pubkey
                    # if peer._pub:
                    #    peer.send(data, callback)
                    # else:
                    print 'test %s' % peer

                    def cb(msg):
                        print msg

                    peer.send(data, cb)

                except:
                    self.log.info("Error sending over peer!")
                    traceback.print_exc()

    def broadcast_goodbye(self):
        self.log.info("Broadcast goodbye")
        msg = goodbye({'uri': self.uri})
        self.send(msg)

    def _on_message(self, msg):

        # here goes the application callbacks
        # we get a "clean" msg which is a dict holding whatever
        self.log.info("[On Message] Data received: %s" % msg)

        # if not self.routingTable.getContact(msg['senderGUID']):
        # Add to contacts if doesn't exist yet
        # self._addCryptoPeer(msg['uri'], msg['senderGUID'], msg['pubkey'])
        if msg['type'] != 'ok':
            self.trigger_callbacks(msg['type'], msg)

    def _on_raw_message(self, serialized):
        self.log.info("connected " + str(len(serialized)))
        try:
            msg = json.loads(serialized[0])
        except:
            self.log.info("incorrect msg! " + serialized)
            return

        msg_type = msg.get('type')
        if msg_type == 'hello_request' and msg.get('uri'):
            self._init_peer(msg)
        else:
            self._on_message(msg)

    def valid_peer_uri(self, uri):
        try:
            [self_protocol, self_addr, self_port] = \
                network_util.uri_parts(self.uri)
            [other_protocol, other_addr, other_port] = \
                network_util.uri_parts(uri)
        except RuntimeError:
            return False

        if not network_util.is_valid_protocol(other_protocol) \
                or not network_util.is_valid_port(other_port):
            return False

        if network_util.is_private_ip_address(self_addr):
            if not network_util.is_private_ip_address(other_addr):
                self.log.warning(('Trying to connect to external '
                                   'network with a private ip address.'))
        else:
            if network_util.is_private_ip_address(other_addr):
                return False

        return True
