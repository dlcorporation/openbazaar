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


class PeerConnection(object):
    def __init__(self, transport, address):
        # timeout in seconds
        self._timeout = 10
        self._transport = transport
        self._address = address
        self._nickname = ""
        self._responses_received = {}
        self._log = logging.getLogger(
            '[%s] %s' % (self._transport._market_id, self.__class__.__name__)
        )
        self._ctx = zmq.Context()

    def create_socket(self):
        self._log.info('Creating Socket')
        socket = self._ctx.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)
        # self._socket.setsockopt(zmq.SOCKS_PROXY, "127.0.0.1:9051");
        return socket

    def cleanup_context(self):
        self._ctx.destroy()

    def cleanup_socket(self):
        self._socket.close(0)

    def send(self, data, callback):
        self.send_raw(json.dumps(data), callback)

    def send_raw(self, serialized, callback=lambda msg: None):

        compressed_data = zlib.compress(serialized, 9)

        try:
            s = self.create_socket()
            s.connect(self._address)

            stream = zmqstream.ZMQStream(s, io_loop=ioloop.IOLoop.current())
            stream.send(compressed_data)

            def cb(stream, msg):
                response = json.loads(msg[0])
                self._log.debug('[send_raw] %s' % pformat(response))

                # Update active peer info

                if 'senderNick' in response and\
                   response['senderNick'] != self._nickname:
                    self._nickname = response['senderNick']

                if callback is not None:
                    self._log.debug('%s' % msg)
                    callback(msg)
                stream.close()

            stream.on_recv_stream(cb)
        except Exception as e:
            self._log.error(e)
            # shouldn't we raise the exception here???? I think not doing this could cause buggy behavior on top


# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, market_id, my_ip, my_port, my_guid, nickname=None):

        self._peers = {}
        self._callbacks = defaultdict(list)
        self._timeouts = []
        self._port = my_port
        self._ip = my_ip
        self._guid = my_guid
        self._market_id = market_id
        self._nickname = nickname
        self._uri = 'tcp://[%s]:%s' % (self._ip, self._port)

        self._log = logging.getLogger(
            '[%s] %s' % (market_id, self.__class__.__name__)
        )

    def add_callbacks(self, callbacks):
        for section, callback in callbacks:
            self.add_callback(section, callback)

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
        return hello_request({'uri': self._uri})

    def listen(self, pubkey):
        self._log.info("Listening at: %s:%s" % (self._ip, self._port))
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REP)

        if network_util.is_loopback_addr(self._ip):
            try:
                # we are in local test mode so bind that socket on the
                # specified IP
                self.socket.bind(self._uri)
            except Exception as e:
                error_message = "\n\nTransportLayer.listen() error!!!: "
                error_message += "Could not bind socket to " + self._uri
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
            self.socket.ipv6 = True
            self.socket.bind('tcp://[*]:%s' % self._port)

        self.stream = zmqstream.ZMQStream(
            self.socket, io_loop=ioloop.IOLoop.current()
        )

        def handle_recv(message):
            for msg in message:
                self._on_raw_message(msg)
            self.stream.send(
                json.dumps({
                    'type': 'ok',
                    'senderGUID': self._guid,
                    'pubkey': pubkey,
                    'senderNick': self._nickname
                })
            )

        self.stream.on_recv(handle_recv)

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
        # msg = {
        # 'type': 'peer_remove',
        # 'uri': uri
        #     }
        #     self.trigger_callbacks(msg['type'], msg)
        #
        # except KeyError:
        #     self._log.info("Peer %s was already removed", uri)

    def send(self, data, send_to=None, callback=lambda msg: None):

        self._log.info("Outgoing Data: %s %s" % (data, send_to))
        data['senderNick'] = self._nickname

        # Directed message
        if send_to is not None:
            peer = self._dht._routingTable.getContact(send_to)
            # self._log.debug(
            #     '%s %s %s' % (peer._guid, peer._address, peer._pub)
            # )
            peer.send(data, callback=callback)
            return

        else:
            # FindKey and then send

            for peer in self._dht._activePeers:
                try:
                    data['senderGUID'] = self._guid
                    data['pubkey'] = self.pubkey
                    # if peer._pub:
                    #    peer.send(data, callback)
                    # else:
                    print 'test %s' % peer

                    def cb(msg):
                        print msg

                    peer.send(data, cb)

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
        # self._addCryptoPeer(msg['uri'], msg['senderGUID'], msg['pubkey'])
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
