import sys
import json
from collections import defaultdict

import pyelliptic as ec

from zmq.eventloop import ioloop, zmqstream
import zmq
from multiprocessing import Process
from threading import Thread
ioloop.install()
import traceback
import network_util

# Default port
DEFAULT_PORT=12345

# Get some command line pars
SEED_URI = False

if len(sys.argv) > 2:
    MY_IP = sys.argv[2]
else:
    MY_IP = "127.0.0.1"
if len(sys.argv) > 3:
    SEED_URI = sys.argv[3] # like tcp://127.0.0.1:12345
# else:
    # print "You provided no SEED_URI. You should call like [market myip seeduri]"

# Connection to one peer
class PeerConnection(object):
    def __init__(self, address):
        # timeout in seconds
        self._timeout = 10
        self._address = address

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
        Process(target=self._send_raw, args=(serialized,)).start()

    def _send_raw(self, serialized):
        self.create_socket()

        self._socket.send(serialized)

        poller = zmq.Poller()
        poller.register(self._socket, zmq.POLLIN)
        if poller.poll(self._timeout * 1000):
            msg = self._socket.recv()
            self.on_message(msg)
        else:
            print "Peer " + self._address + " timed out."

        self.cleanup_socket()

    def on_message(self, msg):
        print "message received!", msg

    def closed(self, *args):
        print " - peer disconnected"

# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, port=DEFAULT_PORT):
        self._peers = {}
        self._callbacks = defaultdict(list)
        self._id = MY_IP[-1] # hack for logging
        self._port = port
        self._uri = 'tcp://%s:%s' % (MY_IP, self._port)

    def add_callback(self, section, callback):
        self._callbacks[section].append(callback)

    def trigger_callbacks(self, section, *data):
        for cb in self._callbacks[section]:
            cb(*data)
        if not section == 'all':
            for cb in self._callbacks['all']:
                cb(*data)

    def get_profile(self):
        return {'type': 'hello_request', 'uri': 'tcp://%s:12345' % MY_IP}

    def join_network(self):
        self.listen()
        
        if SEED_URI:
            self.init_peer({'uri': SEED_URI})

    def listen(self):
        Thread(target=self._listen).start()

    def _listen(self):
        self.log("init server %s %s" % (MY_IP, self._port))
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REP)

        if MY_IP.startswith("127.0.0."): 
            # we are in local test mode so bind that socket on the 
            # specified IP
            self._socket.bind(self._uri)
        else: 
            self._socket.bind('tcp://*:%s' % self._port)

        while True:
            message = self._socket.recv()
            self.on_raw_message(message)
            self._socket.send(json.dumps({'type': "ok"}))

    def closed(self, *args):
        print "client left"

    def _init_peer(self, msg):
        uri = msg['uri']
        
        if not uri in self._peers:
            self._peers[uri] = PeerConnection(uri)            

    def log(self, msg, pointer='-'):
        print " %s [%s] %s" % (pointer, self._id, msg)
        sys.stdout.flush()

    def send(self, data, send_to=None):

        #self.log("Data sent to p2p: %s" % data);

        # directed message        
        if send_to:
            for peer in self._peers.values():
                if peer._pub == send_to:                    
                    if peer.send(data):
                        print 'Success'
                    else:
                        print 'Failed'                         
                    return
            print "Peer not found!", send_to, self._myself.get_pubkey()
            return
            
        # broadcast
        for peer in self._peers.values():
            try:
                if peer._pub:
                    peer.send(data)
                else:
                    serialized = json.dumps(data)
                    peer.send_raw(serialized)
            except:
                print "Error sending over peer!"
                traceback.print_exc()

    def on_message(self, msg):
        # here goes the application callbacks
        # we get a "clean" msg which is a dict holding whatever
        self.log("Data received: %s" % msg)
        self.trigger_callbacks(msg.get('type'), msg)

    def on_raw_message(self, serialized):
        self.log("connected " +str(len(serialized)))
        try:
            msg = json.loads(serialized[0])
        except:
            self.log("incorrect msg! " + serialized)
            return

        msg_type = msg.get('type')
        if msg_type == 'hello_request' and msg.get('uri'):
            self.init_peer(msg)
        else:
            self.on_message(msg)

    def valid_peer_uri(self, uri):
        try:
            [self_protocol, self_addr, self_port] = network_util.uri_parts(self._uri)
            [other_protocol, other_addr, other_port] = network_util.uri_parts(uri)
        except RuntimeError:
            return False

        if not network_util.is_valid_protocol(other_protocol)  \
                or not network_util.is_valid_port(other_port):
            return False

        if network_util.is_private_ip_address(self_addr):
            if not network_util.is_private_ip_address(other_addr):
                self.log(('Warning: trying to connect to external '
                        'network with a private ip address.')) 
        else:
            if network_util.is_private_ip_address(other_addr):
                return False

        return True
