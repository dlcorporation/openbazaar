from behave import *
from test_util import *
import logging


@given('there is a node')
def step_impl(context):
    create_nodes(context, 1)


@when('we connect')
def step_impl(context):
    context.response = ws_connect(0)


@then('it will introduce itself')
def step_impl(context):
    assert context.response['result']['type'] == u'myself'


def create_nodes(context, num_nodes):
    app = []
    for i in range(num_nodes):
        app.append(MarketApplication(ip_address(i),
                                    12345,
                                    i, db_path=get_db_path(i),
                                    dev_mode=True))
        app[i].listen(node_to_ws_port(i))
        set_store_description(i)
    context.app = app


def create_connected_nodes(context, num_nodes):
    create_nodes(context, num_nodes)
    for i in range(num_nodes - 1):
        ws_send(i, 'connect', {'uri': node_uri(i + 1)})


@given('{num_nodes} connected nodes')
def step_impl(context, num_nodes):
    create_connected_nodes(context, int(num_nodes))


@given('{num_nodes} nodes')
def step_impl(context, num_nodes):
    create_nodes(context, int(num_nodes))


@when('node {i} connects to node {j}')
def step_impl(context, i, j):
    ws_send(int(i), 'connect', {'uri': node_uri(int(j))})


@then('node {i} is connected to node {j}')
def step_impl(context, i, j):
    i = int(i)
    j = int(j)

    response = ws_receive_myself(i)['result']
    assert(response['type'] == 'myself')
    assert(node_uri(j) in map(lambda x: x['uri'], response['peers']))


@then('node {i} can query page of node {j}')
def step_impl(context, i, j):
    guid_j = ws_connect(int(j))[u'result']['settings']['guid']

    response = ws_send(int(i), 'query_page', {'findGUID': guid_j})[u'result']
    logging.getLogger().info('response %s' % response)

    assert response['type'] == u'page'
    assert response['text'] == storeDescription(j)
