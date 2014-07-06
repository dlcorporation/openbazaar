import sys, os, argparse

import tornado.ioloop
import tornado.web
import tornado.ioloop
from zmq.eventloop import ioloop

ioloop.install()
from crypto2crypto import CryptoTransportLayer
from market import Market
from ws import WebSocketHandler
import logging
import signal


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/html/index.html")


class MarketApplication(tornado.web.Application):

    def __init__(self, market_ip, market_port, seed_uri, market_id, 
                    bm_user=None, bm_pass=None, bm_port=None):

        self.transport = CryptoTransportLayer(market_ip,
                                               market_port,
                                               market_id,
                                               bm_user,
                                               bm_pass,
                                               bm_port)

        self.transport.join_network(seed_uri)

        self.market = Market(self.transport)

        handlers = [
            (r"/", MainHandler),
            (r"/main", MainHandler),
            (r"/html/(.*)", tornado.web.StaticFileHandler, {'path': './html'}),
            (r"/ws", WebSocketHandler,
                dict(transport=self.transport, market=self.market))
        ]

        # TODO: Move debug settings to configuration location
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

    def get_transport(self):
        return self.dht._transport


def start_node(my_market_ip, my_market_port, seed_uri, log_file, market_id, bm_user=None, bm_pass=None, bm_port=None):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s -  \
                                %(levelname)s - %(message)s',
                        filename=log_file)
    locallogger = logging.getLogger('[%s] %s' % (market_id, 'root'))
    application = MarketApplication(my_market_ip,
                                    my_market_port,
                                    seed_uri,
                                    market_id,
                                    bm_user,
                                    bm_pass,
                                    bm_port)


    error = True
    port = 8888
    while error and port < 8988:
        try:
            application.listen(port)
            error = False
        except:
            port += 1

    locallogger.info("Started user app at http://%s:%s" % (my_market_ip, port))

    # handle shutdown
    def shutdown(x, y):
        locallogger = logging.getLogger('[%s] %s' % (market_id, 'root'))
        locallogger.warning("Received TERMINATE, exiting...")
        #application.get_transport().broadcast_goodbye()
        sys.exit(0)
    try:
        signal.signal(signal.SIGTERM, shutdown)
    except ValueError:
        # not the main thread
        pass

    tornado.ioloop.IOLoop.instance().start()

# Run this if executed directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("my_market_ip")
    parser.add_argument("-p", "--my_market_port", type=int, default=12345)
    parser.add_argument("-s", "--seed_uri")
    parser.add_argument("-l", "--log_file", default='production.log')
    parser.add_argument("-u", "--market_id", default=1)
    parser.add_argument("--bmuser", default='username', help="Bitmessage instance user")
    parser.add_argument("--bmpass", default='password', help="Bitmessage instance pass")
    parser.add_argument("--bmport", default='8442', help="Bitmessage instance RPC port")
    args = parser.parse_args()
    start_node(args.my_market_ip,
               args.my_market_port, args.seed_uri, args.log_file, args.market_id,
               args.bmuser, args.bmpass, args.bmport)
