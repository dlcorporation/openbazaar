"""
This module manages all market related activities
"""
from StringIO import StringIO
import ast
from base64 import b64decode, b64encode
import hashlib
import json
import logging
import random
import string
import traceback

from PIL import Image, ImageOps
import gnupg
import tornado
from zmq.eventloop import ioloop

import constants
from data_uri import DataURI
from orders import Orders
from protocol import proto_page, query_page
from crypto2crypto import CryptoTransportLayer
from pybitcointools import *

import trust

ioloop.install()


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
        self._dht = transport.get_dht()
        self._market_id = transport.get_market_id()
        # self._myself = transport.get_myself()
        self._peers = self._dht.getActivePeers()
        self._db = db
        self.orders = Orders(transport, self._market_id, db)
        self.pages = {}
        self.mypage = None
        self.signature = None
        self._nickname = ""
        self._log = logging.getLogger('[%s] %s' % (self._market_id,
                                                   self.__class__.__name__))
        self.settings = self._transport.settings

        self.gpg = gnupg.GPG()

        # Register callbacks for incoming events
        self._transport.add_callbacks([('query_myorders', self.on_query_myorders),
                                       ('peer', self.on_peer),
                                       ('query_page', self.on_query_page),
                                       ('query_listings', self.on_query_listings),
                                       ('page', self.on_page),
                                       ('negotiate_pubkey', self.on_negotiate_pubkey),
                                       ('proto_response_pubkey', self.on_response_pubkey)])

        self.load_page()

        # Periodically refresh buckets
        loop = tornado.ioloop.IOLoop.instance()
        refreshCB = tornado.ioloop.PeriodicCallback(self._dht._refreshNode,
                                                    constants.refreshTimeout,
                                                    io_loop=loop)
        refreshCB.start()

    def load_page(self):
        nickname = self.settings['nickname'] \
            if 'nickname' in self.settings else ""
        # store_description = self.settings['storeDescription'] if 'storeDescription' self.settings else ""
        self._nickname = nickname

    def disable_welcome_screen(self):
        self._db.updateEntries("settings",
                               {'market_id': self._transport._market_id},
                               {"welcome": "disable"})

    def private_key(self):
        return self.settings['secret']

    def on_listing_results(self, results):
        self._log.debug('Listings %s' % results)

    def process_contract_image(self, image):
        uri = DataURI(image)
        imageData = uri.data
        # mime_type = uri.mimetype
        charset = uri.charset

        image = Image.open(StringIO(imageData))
        croppedImage = ImageOps.fit(image, (200, 200), centering=(0.5, 0.5))
        data = StringIO()
        croppedImage.save(data, format='PNG')
        new_uri = DataURI.make('image/png',
                               charset=charset,
                               base64=True,
                               data=data.getvalue())
        data.close()

        return new_uri

    def get_contract_id(self):
        return random.randint(0, 1000000)

    def linebreak_signing_data(self, data):
        json_string = json.dumps(data, indent=0)
        seg_len = 52
        out_text = string.join(map(lambda x: json_string[x:x + seg_len],
                                   range(0, len(json_string), seg_len)), "\n")
        return out_text

    def generate_contract_key(self, signed_contract):
        contract_hash = hashlib.sha1(str(signed_contract)).hexdigest()
        hash_value = hashlib.new('ripemd160')
        hash_value.update(contract_hash)
        return hash_value.hexdigest()

    def save_contract_to_db(self, contract_id, body, signed_body, key):
        self._db.insertEntry("contracts", {"id": contract_id,
                                           "market_id": self._transport._market_id,
                                           "contract_body": json.dumps(body),
                                           "signed_contract_body": str(signed_body),
                                           "state": "seed",
                                           "key": key})

    def update_keywords_on_network(self, key, keywords):

        for keyword in keywords:
            keyword = keyword.upper()
            hash_value = hashlib.new('ripemd160')
            keyword_key = 'keyword-%s' % keyword
            hash_value.update(keyword_key.encode('utf-8'))
            keyword_key = hash_value.hexdigest()

            self._transport._dht.iterativeStore(self._transport,
                                                keyword_key,
                                                json.dumps({'keyword_index_add': key}),
                                                self._transport._guid)

    def save_contract(self, msg):
        contract_id = self.get_contract_id()

        # Refresh market settings
        self.settings = self.get_settings()

        msg['Seller']['seller_PGP'] = self.gpg.export_keys(self.settings['PGPPubkeyFingerprint'])
        msg['Seller']['seller_BTC_uncompressed_pubkey'] = self.settings['btc_pubkey']
        msg['Seller']['seller_GUID'] = self.settings['guid']

        # Process and crop thumbs for images
        if 'item_images' in msg['Contract']:
            if 'image1' in msg['Contract']['item_images']:
                img = msg['Contract']['item_images']['image1']
                new_uri = self.process_contract_image(img)
                msg['Contract']['item_images'] = new_uri

        # Line break the signing data
        out_text = self.linebreak_signing_data(msg)

        # Sign the contract
        signed_data = self.gpg.sign(out_text,
                                    passphrase='P@ssw0rd',
                                    keyid=self.settings.get('PGPPubkeyFingerprint'))

        # Save contract to DHT
        contract_key = self.generate_contract_key(signed_data)

        # Store contract in database
        self.save_contract_to_db(contract_id, msg, signed_data, contract_key)

        # Store listing
        self._transport._dht.iterativeStore(self._transport,
                                            contract_key,
                                            str(signed_data),
                                            self._transport._guid)
        self.update_listings_index()

        # If keywords are present
        keywords = msg['Contract']['item_keywords']
        self.update_keywords_on_network(contract_key, keywords)

    def shipping_address(self):
        settings = self.get_settings()
        shipping_address = {"recipient_name": settings.get('recipient_name'),
                            "street1": settings.get('street1'),
                            "street2": settings.get('street2'),
                            "city": settings.get('city'),
                            "stateRegion": settings.get('stateRegion'),
                            "stateProvinceRegion": settings.get('stateProvinceRegion'),
                            "zip": settings.get('zip'),
                            "country": settings.get('country'),
                            "countryCode": settings.get('countryCode')}
        return shipping_address

    def add_trusted_notary(self, guid, nickname=""):
        self._log.debug('%s %s' % (guid, nickname))
        notaries = self.settings.get('notaries')
        if notaries == "" or notaries == []:
            notaries = []
        else:
            notaries = json.loads(notaries)

        for notary in notaries:
            self._log.info(notary)
            if notary.get('guid') == guid:
                if notary.get('nickname') != nickname:
                    notary['nickname'] = nickname
                    notary['idx'] = notary
                    self.settings['notaries'] = notaries
                return

        notaries.append({"guid": guid, "nickname": nickname})
        self.settings['notaries'] = json.dumps(notaries)

        if 'btc_pubkey' in self.settings:
            del self.settings['btc_pubkey']

        self._db.updateEntries("settings",
                               {'market_id': self._transport._market_id},
                               self.settings)

    def remove_trusted_notary(self, guid):

        notaries = self.settings.get('notaries')
        notaries = ast.literal_eval(notaries)

        for idx, notary in enumerate(notaries):

            if notary.get('guid') == guid:
                del notaries[idx]

        self.settings['notaries'] = json.dumps(notaries)

        self._db.updateEntries("settings",
                               {'market_id': self._transport._market_id},
                               self.settings)

    def republish_contracts(self):
        listings = self._db.selectEntries("contracts")
        for listing in listings:
            self._transport._dht.iterativeStore(self._transport,
                                                listing['key'],
                                                listing.get('signed_contract_body'),
                                                self._transport._guid)
        self.update_listings_index()

    def get_notaries(self, online_only=False):
        self._log.debug('Getting notaries')
        notaries = []
        settings = self.get_settings()

        # Untested code
        if online_only:
            notaries = {}
            for n in settings['notaries']:
                peer = self._dht._routingTable.getContact(n.guid)
            if peer is not None and peer.check_port():
                notaries.append(n)
            return notaries
        # End of untested code

        return settings['notaries']

    @staticmethod
    def valid_guid(guid):
        return len(guid) == 40 and int(guid, 16)

    def republish_listing(self, msg):

        listing_id = msg.get('productID')
        listing = self._db.selectEntries("products", "id = '%s'" % listing_id)
        if listing:
            listing = listing[0]
        else:
            return

        listing_key = listing['key']

        self._transport._dht.iterativeStore(self._transport,
                                            listing_key,
                                            listing.get('signed_contract_body'),
                                            self._transport._guid)
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
        #     self._transport._dht.iterativeStore(self._transport, keyword_key, json.dumps({'keyword_index_add': contract_key}), self._transport._guid)

    def update_listings_index(self):

        # Store to marketplace listing index
        contract_index_key = hashlib.sha1('contracts-%s' %
                                          self._transport._guid).hexdigest()
        hashvalue = hashlib.new('ripemd160')
        hashvalue.update(contract_index_key)
        contract_index_key = hashvalue.hexdigest()

        # Calculate index of contracts
        contract_ids = self._db.selectEntries("contracts",
                                              "market_id = '%s'" %
                                              self._transport._market_id)
        my_contracts = []
        for contract_id in contract_ids:
            my_contracts.append(contract_id['key'])

        self._log.debug('My Contracts: %s' % my_contracts)

        # Sign listing index for validation and tamper resistance
        data_string = str({'guid': self._transport._guid,
                           'contracts': my_contracts})
        signature = CryptoTransportLayer.makeCryptor(self._transport.settings['secret']).sign(data_string).encode('hex')

        value = {'signature': signature,
                 'data': {'guid': self._transport._guid,
                          'contracts': my_contracts}}

        # Pass off to thread to keep GUI snappy
        self._transport._dht.iterativeStore(self._transport,
                                            contract_index_key,
                                            value, self._transport._guid)

    def remove_contract(self, msg):
        self._log.info("Removing contract: %s" % msg)

        # Remove from DHT keyword indices
        self.remove_from_keyword_indexes(msg['contract_id'])

        self._db.deleteEntries("contracts", {"id": msg["contract_id"]})
        self.update_listings_index()

    def remove_from_keyword_indexes(self, contract_id):
        contract = self._db.selectEntries("contracts", "id = '%s'" % contract_id)[0]
        contract_key = contract['key']

        contract = json.loads(contract['contract_body'])
        contract_keywords = contract['Contract']['item_keywords']

        for keyword in contract_keywords:
            # Remove keyword from index
            hash_value = hashlib.new('ripemd160')
            keyword_key = 'keyword-%s' % keyword
            hash_value.update(keyword_key.encode('utf-8'))
            keyword_key = hash_value.hexdigest()

            self._transport._dht.iterativeStore(self._transport,
                                                keyword_key,
                                                json.dumps({'keyword_index_remove': contract_key}),
                                                self._transport._guid)

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
                                                                 settings['bitmessage'],
                                                                 subject, body)
            self._log.info("Send message result: {}".format(result))
            return {}
        except Exception as e:
            self._log.error("Failed to send message: %s" % e)
            self._log.error(traceback.format_exc())
            return {}

    def get_contracts(self, page=0):
        self._log.info('Getting contracts for market: %s' % self._transport._market_id)
        contracts = self._db.selectEntries("contracts", "market_id = '%s'" % self._transport._market_id,
                                           limit=10,
                                           limit_offset=(page * 10))
        my_contracts = []
        for contract in contracts:
            try:
                contract_body = json.loads(u"%s" % contract['contract_body'])
                item_price = contract_body.get('Contract').get('item_price') if contract_body.get('Contract').get('item_price') > 0 else 0
                shipping_price = contract_body.get('Contract').get('item_delivery').get('shipping_price') if contract_body.get('Contract').get('item_delivery').get('shipping_price') > 0 else 0
                my_contracts.append({"key": contract['key'] if 'key' in contract else "",
                                     "id": contract['id'] if 'id' in contract else "",
                                     "item_images": contract_body.get('Contract').get('item_images'),
                                     "signed_contract_body": contract['signed_contract_body'] if 'signed_contract_body' in contract else "",
                                     "contract_body": contract_body,
                                     "unit_price": item_price,
                                     "shipping_price": shipping_price,
                                     "item_title": contract_body.get('Contract').get('item_title'),
                                     "item_desc": contract_body.get('Contract').get('item_desc'),
                                     "item_condition": contract_body.get('Contract').get('item_condition'),
                                     "item_quantity_available": contract_body.get('Contract').get('item_quantity'),
                                     })
            except:
                self._log.error('Problem loading the contract body JSON')

        return {"contracts": my_contracts, "page": page,
                "total_contracts": self._db.numEntries("contracts")}

    # SETTINGS
    def save_settings(self, msg):
        self._log.debug("Settings to save %s" % msg)

        # Check for any updates to arbiter or notary status to push to the DHT
        if 'notary' in msg:
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

        if 'burnAmount' in msg:
            del msg['burnAmount']
        if 'burnAddr' in msg:
            del msg['burnAddr']

        # Update local settings
        self._db.updateEntries("settings", {'market_id': self._transport._market_id}, msg)

    def get_settings(self):

        self._log.info('Getting settings info for Market %s' % self._transport._market_id)
        settings = self._db.getOrCreate("settings", "market_id = '%s'" % self._transport._market_id, {"market_id": self._transport._market_id})

        if settings['arbiter'] == 1:
            settings['arbiter'] = True
        if settings['notary'] == 1:
            settings['notary'] = True

        settings['notaries'] = ast.literal_eval(settings['notaries']) if settings['notaries'] != "" else []
        settings['trustedArbiters'] = ast.literal_eval(settings['trustedArbiters']) if settings['trustedArbiters'] != "" else []
        settings['privkey'] = settings['privkey'] if 'secret' in settings else ""
        settings['btc_pubkey'] = privkey_to_pubkey(settings.get('privkey'))
        settings['secret'] = settings['secret'] if 'secret' in settings else ""

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
        guid = page.get('senderGUID')

        # TODO: allow async calling in different thread
        def reputation_pledge_retrieved(amount):
            self._log.debug('Received reputation pledge amount %s for guid %s' % (amount, guid))
            SATOSHIS_IN_BITCOIN = 100000000
            bitcoins = float(amount) / SATOSHIS_IN_BITCOIN
            bitcoins = round(bitcoins, 4)
            page['reputation_pledge'] = bitcoins

        trust.get_global(guid, reputation_pledge_retrieved)
        sin = page.get('sin')
        page = page.get('text')

        self._log.info("Received store info from node: %s" % page)

        if sin and page:
            self.pages[sin] = page

    # Return your page info if someone requests it on the network
    def on_query_page(self, peer):
        self._log.info("Someone is querying for your page")
        settings = self.get_settings()
        # self._log.info(base64.b64encode(self.settings['storeDescription']))

        new_peer = self._transport.get_crypto_peer(peer['senderGUID'],
                                                   peer['uri'],
                                                   pubkey=peer['pubkey'],
                                                   nickname=peer['senderNick'])
        new_peer.start_handshake()

        new_peer.send(proto_page(self._transport._uri,
                                 self._transport.pubkey,
                                 self._transport.guid,
                                 settings['storeDescription'],
                                 self.signature,
                                 settings['nickname'],
                                 settings['PGPPubKey'] if 'PGPPubKey' in settings else '',
                                 settings['email'] if 'email' in settings else '',
                                 settings['bitmessage'] if 'bitmessage' in settings else '',
                                 settings['arbiter'] if 'arbiter' in settings else '',
                                 settings['notary'] if 'notary' in settings else '',
                                 settings['arbiterDescription'] if 'arbiterDescription' in settings else '',
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
        # signature = response["signature"].decode("hex")
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

    def release_funds_to_merchant(self, buyer_order_id, tx, script, signatures, guid):
        self._log.debug('Release funds to merchant: %s %s %s %s' % (buyer_order_id, tx, signatures, guid))
        self._transport.send({'type': 'release_funds_tx',
                              'tx': tx,
                              'script': script,
                              'buyer_order_id': buyer_order_id,
                              'signatures': signatures}, guid)
        self._log.debug('TX sent to merchant')
