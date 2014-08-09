from behave import *
from zmq.eventloop import ioloop
from node.crypto2crypto import *
from tornado.testing import *
from node.db_store import Obdb

port = 12345
db = Obdb()


def create_layers(context, num_layers):
    layers = []
    for i in range(num_layers):
        layers.append(CryptoTransportLayer('127.0.0.%s' % str(i+1), port, i))
    context.layers = layers


@given('{num_layers} layers')
def step_impl(context, num_layers):
    create_layers(context, int(num_layers))


@when('layer {i} connects to layer {j}')
def step_impl(context, i, j):
    i = context.layers[int(i)]
    j = context.layers[int(j)]

    j.join_network()

    def cb(msg):
        ioloop.IOLoop.current().stop()

    i.join_network([urlparse(j._uri).hostname], callback=cb)
    ioloop.IOLoop.current().start()


@then('layer {i} is aware of layer {j}')
def step_impl(context, i, j):
    i = int(i)
    j = int(j)
    iLayer = context.layers[i]
    jLayer = context.layers[j]


    assert(db.numEntries("peers", {"guid": jLayer._guid, "market_id": i}) > 0)
    assert(('127.0.0.%s' % (j+1), port, jLayer.guid, jLayer._nickname) in iLayer._dht._knownNodes)
    assert(jLayer._guid in map(lambda x: x._guid, iLayer._dht._activePeers))
    # i is not in jLayer._knownNodes
    assert(iLayer._guid in map(lambda x: x._guid, jLayer._dht._activePeers))