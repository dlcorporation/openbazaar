from behave import *
from node.tornadoloop import start_node
from threading import Thread
from test_util import *
import time

@given('there is a node')
def step_impl(context):
    thread = Thread(target=start_node,
                    args=('ppl/default',
                          '127.0.0.1',
                          12345,
                          None,
                          'test1.log')).start()
    context.thread = thread
    time.sleep(0.1)


@when('we connect')
def step_impl(context):
    context.response = ws_connect(8888)


@then('it will introduce itself')
def step_impl(context):
    print repr(context.response['result']['type'])
    assert context.response['result']['type'] == u'mysel'
    context.thread.stop()


