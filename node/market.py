"""
This module manages all market related activities
"""
from PIL import Image, ImageOps
from StringIO import StringIO
from base64 import b64decode, b64encode
from data_uri import DataURI
from orders import Orders
from protocol import proto_page, query_page
from zmq.eventloop import ioloop
ioloop.install()
import ast
import constants
import datetime
import gnupg
import hashlib
import json
import logging
import lookup
import protocol
import random
import string
import tornado
import traceback

class Market(object):

    def __init__(self, transport, db):

        """This class manages the active market for the application

        Attributes:
          _transport (CryptoTransportLayer): Transport layer for messaging between nodes.
          _dht (DHT): For storage across the network.
          _market_id (int): Indicates which local market we're working with.

        """

        # Current
        self._transport = transport
        self._dht = transport.getDHT()
        self._market_id = transport.getMarketID()
        self._myself = transport.getMyself()
        self._peers = self._dht.getActivePeers()
        self._db = db
        self.orders = Orders(transport, self._market_id, db)

        # Legacy for now
        self.pages = {}
        self.welcome = False
        self.mypage = None
        self.signature = None
        self._nickname = ""

        self._log = logging.getLogger('[%s] %s' % (self._market_id, self.__class__.__name__))
        self.settings = self._transport.settings

        welcome = True

        if self.settings:
            if  'welcome' in self.settings.keys() and self.settings['welcome']:
                welcome = False

        # Register callbacks for incoming events
        self._transport.add_callback('query_myorders', self.on_query_myorders)
        self._transport.add_callback('peer', self.on_peer)
        self._transport.add_callback('query_page', self.on_query_page)
        self._transport.add_callback('query_listings', self.on_query_listings)
        self._transport.add_callback('page', self.on_page)

        self._transport.add_callback('negotiate_pubkey', self.on_negotiate_pubkey)
        self._transport.add_callback('proto_response_pubkey', self.on_response_pubkey)

        self.load_page(welcome)

        # Periodically refresh buckets
        loop = tornado.ioloop.IOLoop.instance()
        refreshCB = tornado.ioloop.PeriodicCallback(self._dht._refreshNode,
                                                    constants.refreshTimeout,
                                                    io_loop=loop)
        refreshCB.start()



    def load_page(self, welcome):

        nickname = self.settings['nickname'] if self.settings.has_key("nickname") else ""
        store_description = self.settings['storeDescription'] if self.settings.has_key("storeDescription") else ""

        self._nickname = nickname

        if welcome:
            self._db.updateEntries("settings", {'market_id': self._transport._market_id}, {"welcome":"noshow"})
        else:
            self.welcome = False

    def private_key(self):
        return self.settings['privkey']

    def on_listing_results(self, results):
        self._log.debug('Listings %s' % results)

    def save_contract(self, msg):

        contract_id = random.randint(0, 1000000)

        # Initialize default values if not set
        # if not msg.has_key("unit_price") or not msg['unit_price'] > 0:
        #     msg['unit_price'] = 0
        # if not msg.has_key("shipping_price") or not msg['shipping_price'] > 0:
        #     msg['shipping_price'] = 0
        # if not msg.has_key("item_quantity_available") or not msg['item_quantity_available'] > 0:
        #     msg['item_quantity_available'] = 1

        # Load gpg
        gpg = gnupg.GPG()

        # Insert PGP Key
        self.settings = self._db.selectEntries("settings", "market_id = '%s'" % self._market_id)[0]

        self._log.debug('Settings %s' % self._transport.settings)
        msg['Seller']['seller_PGP'] = gpg.export_keys(self._transport.settings['PGPPubkeyFingerprint'], secret="P@ssw0rd")
        msg['Seller']['seller_BTC_uncompressed_pubkey'] = self._transport.settings['pubkey']
        msg['Seller']['seller_GUID'] = self._transport._guid

        # Process and crop thumbs for images
        if msg['Contract'].has_key('item_images'):
            if msg['Contract']['item_images'].has_key('image1'):

                img = msg['Contract']['item_images']['image1']

                uri = DataURI(img)
                imageData = uri.data
                mime_type = uri.mimetype
                charset = uri.charset

                image = Image.open(StringIO(imageData))
                croppedImage = ImageOps.fit(image, (200, 200), centering=(0.5, 0.5))
                data = StringIO()
                croppedImage.save(data, format='PNG')

                new_uri = DataURI.make('image/png', charset=charset, base64=True, data=data.getvalue())

                data.close()

                msg['Contract']['item_images'] = new_uri

        # TODO: replace default passphrase
        json_string = json.dumps(msg, indent=0)
        seg_len = 52
        out_text = string.join(map(lambda x : json_string[x:x+seg_len],
           range(0, len(json_string), seg_len)), "\n")
        signed_data = gpg.sign(out_text, passphrase='P@ssw0rd', keyid=self.settings.get('PGPPubkeyFingerprint'))

        # Save contract to DHT
        contract_key = hashlib.sha1(str(signed_data)).hexdigest()

        hash_value = hashlib.new('ripemd160')
        hash_value.update(contract_key)
        contract_key = hash_value.hexdigest()

        self._db.insertEntry("contracts", {"id": contract_id, "market_id": self._transport._market_id, "contract_body": json.dumps(msg), "signed_contract_body": str(signed_data), "state": "seed", "key": contract_key})

        self._log.debug('New Contract Key: %s' % contract_key)

        # Store listing
        self._transport._dht.iterativeStore(self._transport, contract_key, str(signed_data), self._transport._guid)

        self.update_listings_index()

        # If keywords store them in the keyword index
        keywords = msg['Contract']['item_keywords']
        self._log.info('Keywords: %s' % keywords)
        for keyword in keywords:

            hash_value = hashlib.new('ripemd160')
            hash_value.update('keyword-%s' % keyword)
            keyword_key = hash_value.hexdigest()

            self._transport._dht.iterativeStore(self._transport, keyword_key, json.dumps({'keyword_index_add':contract_key}), self._transport._guid)

    def republish_contracts(self):
        #listings = self._db.contracts.find()
        listings = self._db.selectEntries("contracts")
        for listing in listings:
            self._transport._dht.iterativeStore(self._transport, listing['key'], listing.get('signed_contract_body'), self._transport._guid)
        self.update_listings_index()

    def get_notaries(self):
        self._log.debug('Getting notaries')

        notaries = []
        self.settings = self.get_settings()
        notary_guids = self.settings['notaries']
        for guid in notary_guids:
            self._log.debug(guid)

            peer = self._dht._routingTable.getContact(guid)
            if peer and hasattr(peer, '_nickname'):
                nickname = peer._nickname
            else:
                nickname = ""

            notaries.append({"guid":guid, "nickname": nickname})
        self._log.debug(notaries)
        return notaries

    def republish_listing(self, msg):

        listing_id = msg.get('productID')
        listing = self._db.selectEntries("products", {"id": listing_id})
        if listing:
            listing = listing[0]
        else:
            return

        listing_key = listing['key']

        self._transport._dht.iterativeStore(self._transport, listing_key, listing.get('signed_contract_body'), self._transport._guid)
        self.update_listings_index()

        # If keywords store them in the keyword index
        # keywords = msg['Contract']['item_keywords']
        # self._log.info('Keywords: %s' % keywords)
        # for keyword in keywords:
        #
        #     hash_value = hashlib.new('ripemd160')
        #     hash_value.update('keyword-%s' % keyword)
        #     keyword_key = hash_value.hexdigest()
        #
        #     self._transport._dht.iterativeStore(self._transport, keyword_key, json.dumps({'keyword_index_add':contract_key}), self._transport._guid)



    def update_listings_index(self):

        # Store to marketplace listing index
        contract_index_key = hashlib.sha1('contracts-%s' % self._transport._guid).hexdigest()
        hashvalue = hashlib.new('ripemd160')
        hashvalue.update(contract_index_key)
        contract_index_key = hashvalue.hexdigest()

        # Calculate index of contracts
        contract_ids = self._db.selectEntries("contracts", "market_id = '%s'" % self._transport._market_id)
        my_contracts = []
        for contract_id in contract_ids:
            my_contracts.append(contract_id['key'])

        self._log.debug('My Contracts: %s' % my_contracts)

        # Sign listing index for validation and tamper resistance
        data_string = str({'guid':self._transport._guid, 'contracts': my_contracts})
        signature = self._myself.sign(data_string).encode('hex')

        value = {'signature': signature, 'data': {'guid':self._transport._guid, 'contracts': my_contracts}}

        # Pass off to thread to keep GUI snappy
        self._transport._dht.iterativeStore(self._transport, contract_index_key, value, self._transport._guid)


    def remove_contract(self, msg):
        self._log.info("Removing contract: %s" % msg)

        # Remove from DHT keyword indices
        self.remove_from_keyword_indexes(msg['contract_id'])


        self._db.deleteEntries("contracts", {"id": msg["contract_id"]})
        self.update_listings_index()

    def remove_from_keyword_indexes(self, contract_id):

        contract = self._db.selectEntries("contracts", {"id": contract_id})[0]
        contract_key = contract['key']

        contract = json.loads(contract['contract_body'])
        contract_keywords = contract['Contract']['item_keywords']

        for keyword in contract_keywords:

            # Remove keyword from index

            hash_value = hashlib.new('ripemd160')
            hash_value.update('keyword-%s' % keyword)
            keyword_key = hash_value.hexdigest()

            self._transport._dht.iterativeStore(self._transport, keyword_key, json.dumps({'keyword_index_remove':contract_key}), self._transport._guid)

    def get_messages(self):
        self._log.info("Listing messages for market: %s" % self._transport._market_id)
        settings = self.get_settings()
        try:
            # Request all messages for our address
            inboxmsgs = json.loads(self._transport._bitmessage_api.getInboxMessagesByReceiver(
                settings['bitmessage']))
            for m in inboxmsgs['inboxMessages']:
                # Base64 decode subject and content
                m['subject'] = b64decode(m['subject'])
                m['message'] = b64decode(m['message'])
                # TODO: Augment with market, if available

            return {"messages": inboxmsgs}
        except Exception as e:
            self._log.error("Failed to get inbox messages: {}".format(e))
            self._log.error(traceback.format_exc())
            return {}

    def send_message(self, msg):
        self._log.info("Sending message for market: %s" % self._transport._market_id)
        settings = self.get_settings()
        try:
            # Base64 decode subject and content
            self._log.info("Encoding message: {}".format(msg))
            subject = b64encode(msg['subject'])
            body = b64encode(msg['body'])
            result = self._transport._bitmessage_api.sendMessage(msg['to'],
                settings['bitmessage'], subject, body)
            self._log.info("Send message result: {}".format(result))
            return {}
        except Exception as e:
            self._log.error("Failed to send message: %s" % e)
            self._log.error(traceback.format_exc())
            return {}

    def get_contracts(self, page=0):
        self._log.info('Getting contracts for market: %s' % self._transport._market_id)
        contracts = self._db.selectEntries("contracts", "market_id = '%s'" % self._transport._market_id, limit=10, limit_offset=(page*10))
        my_contracts = []

        for contract in contracts:

            try:
                contract_body = json.loads(u"%s" % contract['contract_body'])

                item_price = contract_body.get('Contract').get('item_price') if contract_body.get('Contract').get('item_price') > 0 else 0

                my_contracts.append({"key":contract['key'] if contract.has_key("key") else "",
                                "id":contract['id'] if contract.has_key("id") else "",
                                "item_images":contract_body.get('Contract').get('item_images'),
                                "signed_contract_body": contract['signed_contract_body'] if contract.has_key("signed_contract_body") else "",
                                "contract_body": contract_body,
                                "unit_price":item_price,
                                "item_title":contract_body.get('Contract').get('item_title'),
                                "item_desc":contract_body.get('Contract').get('item_desc'),
                                "item_condition":contract_body.get('Contract').get('item_condition'),
                                "item_quantity_available":contract_body.get('Contract').get('item_quantity'),
                               })
            except:
                self._log.error('Problem loading the contract body JSON')

        return {"contracts": my_contracts, "page": page, "total_contracts":self._db.numEntries("contracts")}

    # SETTINGS

    def save_settings(self, msg):
        self._log.debug("Settings to save %s" % msg)

        # Check for any updates to arbiter or notary status to push to the DHT
        if msg.has_key('notary'):

            # Generate notary index key
            hash_value = hashlib.new('ripemd160')
            hash_value.update('notary-index')
            key = hash_value.hexdigest()

            if msg['notary'] is True:
                self._log.info('Letting the network know you are now a notary')
                data = json.dumps({'notary_index_add': self._transport._guid})
                self._transport._dht.iterativeStore(self._transport, key, data, self._transport._guid)
            else:
                self._log.info('Letting the network know you are not a notary')
                data = json.dumps({'notary_index_remove': self._transport._guid})
                self._transport._dht.iterativeStore(self._transport, key, data, self._transport._guid)

        # Update nickname
        self._transport._nickname = msg['nickname']

        # Update local settings
        self._db.updateEntries("settings", {'market_id': self._transport._market_id}, msg)

    def get_settings(self):

        self._log.info('Getting settings info for Market %s' % self._transport._market_id)
        settings = self._db.getOrCreate("settings", "market_id = '%s'" % self._transport._market_id, {"market_id":self._transport._market_id})

        if settings['arbiter'] == 1:
          settings['arbiter'] = True
        if settings['notary'] == 1:
          settings['notary'] = True

        settings['notaries'] = ast.literal_eval(settings['notaries']) if settings['notaries'] != "" else []
        settings['trustedArbiters'] = ast.literal_eval(settings['trustedArbiters']) if settings['trustedArbiters'] != "" else []

        settings['privkey'] = settings['secret'][8:] if settings.has_key("secret") else ""

        self._log.info('SETTINGS: %s' % settings)

        if settings:
            return settings
        else:
            return {}


    # PAGE QUERYING
    def query_page(self, find_guid, callback=lambda msg: None):

        self._log.info('Searching network for node: %s' % find_guid)
        msg = query_page(find_guid)
        msg['uri'] = self._transport._uri
        msg['senderGUID'] = self._transport.guid
        msg['sin'] = self._transport.sin
        msg['pubkey'] = self._transport.pubkey

        self._transport.send(msg, find_guid, callback)


    def on_page(self, page):

        #pubkey = page.get('pubkey')
        guid = page.get('senderGUID')
        sin = page.get('sin')
        page = page.get('text')

        self._log.info("Received store info from node: %s" % sin)

        if sin and page:
            self.pages[sin] = page


    # Return your page info if someone requests it on the network
    def on_query_page(self, peer):
        self._log.info("Someone is querying for your page")
        settings = self.get_settings()
        #self._log.info(base64.b64encode(self.settings['storeDescription']))

        new_peer = self._transport.get_crypto_peer(peer['senderGUID'], peer['uri'], pubkey=peer['pubkey'], nickname=peer['senderNick'])

        new_peer.send(proto_page(self._transport._uri,
                                        self._transport.pubkey,
                                        self._transport.guid,
                                        settings['storeDescription'],
                                        self.signature,
                                        settings['nickname'],
                                        settings['PGPPubKey'] if settings.has_key('PGPPubKey') else '',
                                        settings['email'] if settings.has_key('email') else '',
                                        settings['bitmessage'] if settings.has_key('bitmessage') else '',
                                        settings['arbiter'] if settings.has_key('arbiter') else '',
                                        settings['notary'] if settings.has_key('notary') else '',
                                        settings['arbiterDescription'] if settings.has_key('arbiterDescription') else '',
                                        self._transport.sin)
                                        )

    def on_query_myorders(self, peer):
        self._log.info("Someone is querying for your page: %s" % peer)

    def on_query_listings(self, peer, page=0):
        self._log.info("Someone is querying your listings: %s" % peer)
        contracts = self.get_contracts(page)

        for contract in contracts['contracts']:
            contract = contract
            contract['type'] = "listing_result"
            self._transport.send(contract, peer['senderGUID'])


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
        #signature = response["signature"].decode("hex")
        nickname = response["nickname"]
        # Cache mapping for later.
        if nickname not in self._transport.nick_mapping:
            self._transport.nick_mapping[nickname] = [None, pubkey]
        # Verify signature here...
        # Add to our dict.
        self._transport.nick_mapping[nickname][1] = pubkey
        self._log.info("[market] mappings: ###############")
        for key, value in self._transport.nick_mapping.iteritems():
            self._log.info("'%s' -> '%s' (%s)" % (
                key, value[1].encode("hex") if value[1] is not None else value[1],
                value[0].encode("hex") if value[0] is not None else value[0]))
        self._log.info("##################################")




    def lookup(self, msg):

        if self.query_ident is None:
            self._log.info("Initializing identity query")
            self.query_ident = lookup.QueryIdent()

        nickname = str(msg["text"])
        key = self.query_ident.lookup(nickname)
        if key is None:
            self._log.info("Key not found for this nickname")
            return "Key not found for this nickname", None

        self._log.info("Found key: %s " % key.encode("hex"))
        if nickname in self._transport.nick_mapping:
            self._log.info("Already have a cached mapping, just adding key there.")
            response = {'nickname': nickname,
                        'pubkey': self._transport.nick_mapping[nickname][1].encode('hex'),
                        'signature': self._transport.nick_mapping[nickname][0].encode('hex'),
                        'type': 'response_pubkey',
                       }
            self._transport.nick_mapping[nickname][0] = key
            return None, response

        self._transport.nick_mapping[nickname] = [key, None]

        self._transport.send(protocol.negotiate_pubkey(nickname, key))
