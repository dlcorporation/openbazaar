from zmq.eventloop import ioloop
from distutils.util import strtobool as _bool
import os

BEHAVE_DEBUG_ON_ERROR = _bool(os.environ.get("BEHAVE_DEBUG_ON_ERROR", "no"))

def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        # -- ENTER DEBUGGER: Zoom in on failure location.
        # NOTE: Use IPython debugger, same for pdb (basic python debugger).
        import pdb
        pdb.post_mortem(step.exc_traceback)

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