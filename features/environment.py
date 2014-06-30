from zmq.eventloop import ioloop


def before_all(context):
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini".
    context.config.setup_logging()


def before_scenario(context, scenario):
    cur = ioloop.IOLoop.current()
    ioloop.IOLoop.clear_current()
    cur.close(all_fds=True)
    newloop = ioloop.IOLoop()
    newloop.make_current()