import sys
import json
import argparse
import tornado.ioloop
import tornado.web
from zmq.eventloop import ioloop, zmqstream
import zmq
ioloop.install()
from crypto2crypto import CryptoTransportLayer
from market import Market
from ws import WebSocketHandler, ProtocolHandler
import pymongo

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/html/index.html")

class MarketApplication(tornado.web.Application):

    def __init__(self, store_file, my_market_ip, my_market_port, seed_uri):
    
        self.transport = CryptoTransportLayer(my_market_ip, my_market_port, store_file)
        self.transport.join_network(seed_uri)
        self.market = Market(self.transport)        
        
        handlers = [
            (r"/", MainHandler),
            (r"/main", MainHandler),
            (r"/html/(.*)", tornado.web.StaticFileHandler, {'path': './html'}),
            (r"/ws", WebSocketHandler, dict(transport=self.transport, node=self.market))
        ]
        
    	# TODO: Move debug settings to configuration location
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

# Run this if executed directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("store_file", help="You need to specify a user crypto file in `ppl/` folder")
    parser.add_argument("my_market_ip")
    parser.add_argument("-p", "--my_market_port", type=int, default=12345)
    parser.add_argument("-s", "--seed_uri")
    parser.add_argument("-l", "--log_file", default='node.log')
    args = parser.parse_args()

    application = MarketApplication(args.store_file, args.my_market_ip, \
                                    args.my_market_port, args.seed_uri)
    error = True
    port = 8888
    while error and port < 8988:
        try:
            application.listen(port)
            error = False
        except:
            port += 1
    print " - Started user app at http://%s:%s" % (args.my_market_ip, port)
    tornado.ioloop.IOLoop.instance().start()
