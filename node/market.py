from protocol import shout, proto_page, query_page
from reputation import Reputation
from orders import Orders
import protocol
import sys
import json
import lookup
from pymongo import MongoClient
import logging
import pyelliptic
import pycountry
from ecdsa import SigningKey,SECP256k1
import random
from obelisk import bitcoin
import base64


class Market(object):

    def __init__(self, transport):

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info("Loading Market")

        self._myself = transport._myself
        self._peers = transport._activePeers #transport._peers
        self._transport = transport
        self.query_ident = None

        self.reputation = Reputation(self._transport)
        self.orders = Orders(self._transport)
        self.order_entries = self.orders._orders

        self.nicks = {}
        self.pages = {}

        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar

        self.settings = self._transport.settings

        welcome = True

        if self.settings:
            if  'welcome' in self.settings.keys() and self.settings['welcome']:
                welcome = False

        # Register callbacks for incoming events
        transport.add_callback('query_myorders', self.on_query_myorders)
        transport.add_callback('peer', self.on_peer)
        transport.add_callback('query_page', self.on_query_page)
        transport.add_callback('page', self.on_page)
        transport.add_callback('negotiate_pubkey', self.on_negotiate_pubkey)
        transport.add_callback('proto_response_pubkey', self.on_response_pubkey)

        self.load_page(welcome)


    def lookup(self, msg):

        if self.query_ident is None:
            self._log.info("Initializing identity query")
            self.query_ident = lookup.QueryIdent()

        nickname = str(msg["text"])
        key = self.query_ident.lookup(nickname)
        if key is None:
            self._log.info("Key not found for this nickname")
            return ("Key not found for this nickname", None)

        self._log.info("Found key: %s " % key.encode("hex"))
        if nickname in self._transport.nick_mapping:
            self._log.info("Already have a cached mapping, just adding key there.")
            response = {'nickname': nickname,
                        'pubkey': self._transport.nick_mapping[nickname][1].encode('hex'),
                        'signature': self._transport.nick_mapping[nickname][0].encode('hex'),
                        'type': 'response_pubkey',
                        'signature': 'unknown'}
            self._transport.nick_mapping[nickname][0] = key
            return (None, response)

        self._transport.nick_mapping[nickname] = [key, None]

        self._transport.send(protocol.negotiate_pubkey(nickname, key))


    def load_page(self, welcome):

        nickname = self.settings['nickname'] if self.settings.has_key("nickname") else ""
        storeDescription = self.settings['storeDescription'] if self.settings.has_key("storeDescription") else ""

        tagline = "%s: %s" % (nickname, storeDescription)
        self.mypage = tagline
        self.nickname = nickname
        self.signature = self._transport._myself.sign(tagline)

        if welcome:
            self._db.settings.update({}, {"$set":{"welcome":"noshow"}})
        else:
            self.welcome = False


    def save_product(self, msg):
        self._log.info("Product to save %s" % msg)
        self._log.info(self._transport)

        product_id = msg['id'] if msg.has_key("id") else ""

        if product_id == "":
          product_id = random.randint(0,1000000)

        if not msg.has_key("productPrice") or not msg['productPrice'] > 0:
          msg['productPrice'] = 0

        if not msg.has_key("productQuantity") or not msg['productQuantity'] > 0:
          msg['productQuantity'] = 1

        self._db.products.update({'id':product_id}, {'$set':msg}, True)


    def remove_product(self, msg):
        self._log.info("Product to remove %s" % msg)
        self._db.products.remove({'id':msg['productID']})


    def get_products(self):
        self._log.info(self._transport._market_id)
        products = self._db.products.find()
        my_products = []

        for product in products:
          my_products.append({ "productTitle":product['productTitle'] if product.has_key("productTitle") else "",
                        "id":product['id'] if product.has_key("id") else "",
                        "productDescription":product['productDescription'] if product.has_key("productDescription") else "",
                        "productPrice":product['productPrice'] if product.has_key("productPrice") else "",
                        "productShippingPrice":product['productShippingPrice'] if product.has_key("productShippingPrice") else "",
                        "productTags":product['productTags'] if product.has_key("productTags") else "",
                        "productImageData":product['productImageData'] if product.has_key("productImageData") else "",
                        "productQuantity":product['productQuantity'] if product.has_key("productQuantity") else "",
                         })

        return { "products": my_products }


    # SETTINGS

    def save_settings(self, msg):
        self._log.info("Settings to save %s" % msg)
        self._log.info(self._transport)
        self._db.settings.update({'id':'%s'%self._transport._market_id}, {'$set':msg}, True)

    def get_settings(self):
        self._log.info(self._transport._market_id)
        settings = self._db.settings.find_one({'id':'%s'%self._transport._market_id})

        if settings:
            return { "bitmessage": settings['bitmessage'] if settings.has_key("bitmessage") else "",
                "email": settings['email'] if settings.has_key("email") else "",
                "PGPPubKey": settings['PGPPubKey'] if settings.has_key("PGPPubKey") else "",
                "pubkey": settings['pubkey'] if settings.has_key("pubkey") else "",
                "nickname": settings['nickname'] if settings.has_key("nickname") else "",
                "secret": settings['secret'] if settings.has_key("secret") else "",
                "welcome": settings['welcome'] if settings.has_key("welcome") else "",
                "escrowAddresses": settings['escrowAddresses'] if settings.has_key("escrowAddresses") else "",
                "storeDescription": settings['storeDescription'] if settings.has_key("storeDescription") else "",
                "city": settings['city'] if settings.has_key("city") else "",
                "stateRegion": settings['stateRegion'] if settings.has_key("stateRegion") else "",
                "street1": settings['street1'] if settings.has_key("street1") else "",
                "street2": settings['street2'] if settings.has_key("street2") else "",
                "countryCode": settings['countryCode'] if settings.has_key("countryCode") else "",
                "zip": settings['zip'] if settings.has_key("zip") else "",
                "arbiterDescription": settings['arbiterDescription'] if settings.has_key("arbiterDescription") else "",
                "arbiter": settings['arbiter'] if settings.has_key("arbiter") else "",
                }


    # PAGE QUERYING

    def query_page(self, findGUID):
        self._log.info('Querying page: %s' % findGUID)
        msg = query_page(findGUID)
        msg['uri'] = self._transport._uri
        msg['guid'] = self._transport.guid
        msg['pubkey'] = self._transport.pubkey
        print msg
        self._transport.send(msg)

    def on_page(self, page):

        self._log.info("Page returned: " + str(page))

        #pubkey = page.get('pubkey')
        guid = page.get('guid')
        page = page.get('text')

        if guid and page:
            self._log.info(page)
            self.pages[guid] = page

    # Return your page info if someone requests it on the network
    def on_query_page(self, peer):
        self._log.info("Someone is querying for your page")
        self.settings = self.get_settings()
        self._log.info(base64.b64encode(self.settings['storeDescription'].encode('ascii')))
        self._transport.send(proto_page(self._transport._uri,
                                        self._transport.pubkey,
                                        self._transport.guid,
                                        self.settings['storeDescription'],
                                        self.signature,
                                        self.settings['nickname']))

    def on_query_myorders(self, peer):
        self._log.info("Someone is querying for your page")


    def on_peer(self, peer):
        pass

    def on_negotiate_pubkey(self, ident_pubkey):
        self._log.info("Someone is asking for your real pubKey")
        assert "nickname" in ident_pubkey
        assert "ident_pubkey" in ident_pubkey
        nickname = ident_pubkey['nickname']
        ident_pubkey = ident_pubkey['ident_pubkey'].decode("hex")
        self._transport.respond_pubkey_if_mine(nickname, ident_pubkey)

    def on_response_pubkey(self, response):
        self._log.info("got a pubkey!")
        assert "pubkey" in response
        assert "nickname" in response
        assert "signature" in response
        pubkey = response["pubkey"].decode("hex")
        signature = response["signature"].decode("hex")
        nickname = response["nickname"]
        # Cache mapping for later.
        if nickname not in self._transport.nick_mapping:
            self._transport.nick_mapping[nickname] = [None, pubkey]
        # Verify signature here...
        # Add to our dict.
        self._transport.nick_mapping[nickname][1] = pubkey
        self._log.info("[market] mappings: ###############")
        for k, v in self._transport.nick_mapping.iteritems():
            self._log.info("'%s' -> '%s' (%s)" % (
                k, v[1].encode("hex") if v[1] is not None else v[1],
                v[0].encode("hex") if v[0] is not None else v[0]))
        self._log.info("##################################")
