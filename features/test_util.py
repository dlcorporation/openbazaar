import json
import time

from tornado.ioloop import IOLoop
from tornado import gen
from tornado.websocket import websocket_connect

from node.db_store import Obdb


def ip_address(i):
    return '127.0.0.%s' % str(i + 1)


def nickname(i):
    return ''


def get_db_path(i):
    return 'db/ob-test-%s.db' % i


def node_uri(node_index):
    return 'tcp://127.0.0.%s:12345' % str(node_index + 1)


def set_store_description(i):
    ws_send(i, 'update_settings',
            {'settings':
             {'storeDescription': storeDescription(i),
              'nickname': nickname(i)}})


def storeDescription(i):
    return 'store %s' % i


def remove_peers_from_db(i):
    Obdb(get_db_path(i)).deleteEntries('peers')


def node_to_ws_port(node_index):
    return node_index + 8888


def ws_connect(node_index):
    port = str(node_to_ws_port(node_index))

    @gen.coroutine
    def client():
        client = yield websocket_connect('ws://localhost:%s/ws' % port)
        message = yield client.read_message()
        raise gen.Return(json.loads(message))

    return IOLoop.current().run_sync(client)


def ws_send_raw(port, string):
    @gen.coroutine
    def client():
        client = yield websocket_connect('ws://localhost:%s/ws' % port)
        # skip myself message
        message = yield client.read_message()
        client.write_message(json.dumps(string))
        message = yield client.read_message()
        raise gen.Return(json.loads(message))

    return IOLoop.current().run_sync(client)


def ws_send(node_index, command, params=None):
    if params is None:
        params = {}
    port = node_to_ws_port(node_index)
    cmd = {'command': command,
           'id': 1,
           'params': params}
    ret = ws_send_raw(port, cmd)
    time.sleep(0.1)
    return ret


def ws_receive_myself(node_index):
    port = node_to_ws_port(node_index)

    @gen.coroutine
    def client():
        client = yield websocket_connect('ws://localhost:%s/ws' % port)
        message = yield client.read_message()
        raise gen.Return(json.loads(message))

    return IOLoop.current().run_sync(client)
