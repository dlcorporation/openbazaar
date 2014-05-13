from behave import *
from node.tornadoloop import start_node
from threading import Thread
from test_util import *
import time
from multiprocessing import Process

@given('there is a node')
def step_impl(context):
    context.proc = Process(target=start_node,
                    args=('ppl/default',
                          '127.0.0.1',
                          12345,
                          None,
                          'test1.log'))
    context.proc.start()
    time.sleep(0.1)


@when('we connect')
def step_impl(context):
    context.response = ws_connect(8888)


@then('it will introduce itself')
def step_impl(context):
    assert context.response['result']['type'] == u'myself'
    context.proc.terminate()
    time.sleep(0.1)


@given('there are two nodes')
def step_impl(context):
    context.proc = []
    context.proc.append(Process(target=start_node,
           args=('ppl/default', '127.0.0.1', 12345, None, 'test1.log')))
    time.sleep(0.1)
    context.proc.append(Process(target=start_node,
           args=('ppl/default', '127.0.0.2', 12345, None, 'test1.log')))
    context.proc[0].start()
    context.proc[1].start()
    time.sleep(0.1)


@when('a node connects to another')
def step_impl(context):
    response1 = ws_connect(8888)
    response2 = ws_connect(8889)
    context.pubkeys = []
    context.pubkeys.append(response1[u'result'][u'pubkey'])
    context.pubkeys.append(response2[u'result'][u'pubkey'])
    print context.pubkeys
    ws_send(8888, 'connect', {'uri': 'tcp://127.0.0.2:12345'})
    time.sleep(0.5)


@then('they will have each other as peers')
def step_impl(context):
    response1 = ws_send(8888, 'peers')
    response1 = response1[u'result']
    response2 = ws_send(8889, 'peers')[u'result']
    print 'resp1', response1
    print 'resp2', response2
    assert response1['type'] == u'peers'
    assert response1['type'] == u'peers'
    assert response1['peers'][0]['pubkey'] == context.pubkeys[1]
    assert response1['peers'][0]['uri'] == u'tcp://127.0.0.2:12345'
    assert response2['peers'][0]['pubkey'] == context.pubkeys[0]
    assert response2['peers'][0]['uri'] == u'tcp://127.0.0.1:12345'
    context.proc[0].terminate()
    context.proc[1].terminate()
