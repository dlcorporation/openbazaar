import sys
import json
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

    def __init__(self):
    
    	# TODO: Move debug settings to configuration location
        settings = dict(debug=True)
        
              
    
        self.transport = CryptoTransportLayer(12345)
        self.transport.join_network()
        #self.protocol_handler = ProtocolHandler(self.transport)
        self.market = Market(self.transport)        
        
        handlers = [
            (r"/", MainHandler),
            (r"/main", MainHandler),
            (r"/html/(.*)", tornado.web.StaticFileHandler, {'path': './html'}),
            (r"/ws", WebSocketHandler, dict(transport=self.transport, node=self.market))
        ]
        
        tornado.web.Application.__init__(self, handlers, **settings)

# Run this if executed directly
if __name__ == "__main__":
    application = MarketApplication()
    error = True
    port = 8888
    while error and port < 8988:
        try:
            application.listen(port)
            error = False
        except:
            port += 1
    print " - Started user app at http://%s:%s" % (sys.argv[2], port)
    tornado.ioloop.IOLoop.instance().start()

