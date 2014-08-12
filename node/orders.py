import random
import logging
import time

from protocol import order
from pyelliptic import ECC

from multisig import Multisig
from db_store import Obdb
import gnupg
import hashlib
import string
import json
import datetime
import qrcode
import StringIO
import ast


class Orders(object):
    def __init__(self, transport, market_id, db):

        self._transport = transport
        self._priv = transport._myself
        self._market_id = market_id

        self._gpg = gnupg.GPG()
        self._db = db
        self._orders = self.get_orders()
        self.orders = self._orders

        self._transport.add_callback('order', self.on_order)

        self._log = logging.getLogger('[%s] %s' % (self._market_id, self.__class__.__name__))

    def get_order(self, orderId):

        _order = self._db.selectEntries("orders", {"order_id": orderId})[0]


        if _order['state'] in ('Need to Pay', 'Notarized', 'Waiting for Payment'):
            offer_data = ''.join(_order['signed_contract_body'].split('\n')[8:])
            index_of_seller_signature = offer_data.find('-----BEGIN PGP SIGNATURE-----', 0, len(offer_data))
            offer_data_json = offer_data[0:index_of_seller_signature-4]
            offer_data_json = json.loads(str(offer_data_json))
            if _order.has_key("shipping_price"):
                shipping_price = _order['shipping_price'] if _order['shipping_price'] != '' else 0
            else:
                shipping_price = 0
            total_price = (float(shipping_price) + float(_order['item_price'])) if _order.has_key("item_price") else _order['item_price']
        elif _order['state'] in ('Paid'):
            offer_data = ''.join(_order['signed_contract_body'].split('\n')[8:])
            index_of_seller_signature = offer_data.find('-----BEGIN PGP SIGNATURE-----', 0, len(offer_data))
            offer_data_json = offer_data[0:index_of_seller_signature-4]
            offer_data_json = json.loads(str(offer_data_json))
            if _order.has_key("shipping_price"):
                shipping_price = _order['shipping_price'] if _order['shipping_price'] != '' else 0
            else:
                shipping_price = 0
            total_price = (float(shipping_price) + float(_order['item_price'])) if _order.has_key("item_price") else _order['item_price']
        else:
            offer_data = ''.join(_order['signed_contract_body'].split('\n')[8:])
            index_of_seller_signature = offer_data.find('-----BEGIN PGP SIGNATURE-----', 0, len(offer_data))
            offer_data_json = '{"Seller": {'+offer_data[0:index_of_seller_signature-2]
            self._log.info(offer_data_json)
            total_price = ""
            offer_data_json = json.loads(str(offer_data_json))

        qr = qrcode.make("bitcoin:"+_order['address']+"?amount"+str(total_price)+"&message="+offer_data_json['Contract']['item_title'])
        output = StringIO.StringIO()
        qr.save(output, "PNG")
        qr = output.getvalue().encode("base64")
        output.close()


        notary = self._transport._guid if _order['state'] == 'Notarized' else ""

        # Get order prototype object before storing
        order = {"id": _order['id'],
                 "state": _order['state'],
                 "address": _order['address'] if _order.has_key("address") else "",
                 "buyer": _order['buyer'] if _order.has_key("buyer") else "",
                 "merchant": _order['merchant'] if _order.has_key("merchant") else "",
                 "item_price": _order['item_price'] if _order.has_key("item_price") else "",
                 "shipping_price": _order['shipping_price'] if _order.has_key("shipping_price") else "",
                 "total_price": total_price,
                 "notary": notary,
                 "item_image": offer_data_json['Contract']['item_images'] if offer_data_json['Contract']['item_images'] != {} else "img/no-photo.png",
                 "qrcode": 'data:image/png;base64,'+qr,
                 "item_title": offer_data_json['Contract']['item_title'],
                 "signed_contract_body": _order['signed_contract_body'] if _order.has_key("signed_contract_body") else "",
                 "note_for_merchant":  _order['note_for_merchant'] if _order.has_key("note_for_merchant") else "",
                 "updated": _order['updated'] if _order.has_key("updated") else ""}
        # orders.append(_order)

        return order

    def get_orders(self, page=0):
        orders = self._db.selectEntries("orders", {'market_id': self._market_id}, order_field="updated", order="DESC", limit=10, limit_offset=page*10)


        return {"total": self._db.numEntries("orders", {'market_id': self._market_id}), "orders":orders}


    # Create a new order
    def create_order(self, seller, text):
        self._log.info('CREATING ORDER')
        order_id = random.randint(0, 1000000)
        buyer = self._transport._myself.get_pubkey()
        new_order = order(order_id, buyer, seller, 'new', text, self._escrows)

        # Add a timestamp
        new_order['created'] = time.time()

        self._transport.send(new_order, seller)

        self._db.insertEntry("orders", new_order)


    def accept_order(self, new_order):

        # TODO: Need to have a check for the vendor to agree to the order

        new_order['state'] = 'accepted'
        seller = new_order['seller'].decode('hex')
        buyer = new_order['buyer'].decode('hex')

        new_order['escrows'] = [new_order.get('escrows')[0]]
        escrow = new_order['escrows'][0].decode('hex')

        # Create 2 of 3 multisig address
        self._multisig = Multisig(None, 2, [buyer, seller, escrow])

        new_order['address'] = self._multisig.address

        if self._db.numEntries("order",{"order_id": new_order['id']}) > 0:
            self._db.updateEntries("orders", {"order_id": new_order['id']}, {new_order})
        else:
            self._db.insertEntry("orders", new_order)

        self._transport.send(new_order, new_order['buyer'].decode('hex'))

    def pay_order(self, new_order, order_id):  # action
        new_order['state'] = 'Paid'

        self._log.debug(new_order)

        del new_order['qrcode']
        del new_order['item_image']
        del new_order['total_price']
        del new_order['item_title']

        self._db.updateEntries("orders", {"order_id": order_id}, new_order)

        new_order['type'] = 'order'

        self._transport.send(new_order, new_order['merchant'])


    def offer_json_from_seed_contract(self, seed_contract):
        self._log.debug('Seed Contract: %s' % seed_contract)
        contract_data = ''.join(seed_contract.split('\n')[6:])
        index_of_signature = contract_data.find('- -----BEGIN PGP SIGNATURE-----', 0, len(contract_data))
        contract_data_json = contract_data[0:index_of_signature]
        self._log.debug('json %s' % contract_data_json)
        return json.loads(contract_data_json)

    def send_order(self, order_id, contract, notary):  # action

        self._log.info('Verify Contract and Store in Orders Table')
        self._log.debug('%s' % contract)
        contract_data_json = self.offer_json_from_seed_contract(contract)

        try:
            self._log.debug('%s' % contract_data_json)
            seller_pgp = contract_data_json['Seller']['seller_PGP']
            self._gpg.import_keys(seller_pgp)
            v = self._gpg.verify(contract)

            if v:
                self._log.info('Verified Contract')

                try:
                    self._db.insertEntry("orders", {"order_id": order_id,
                                                    "state": "Sent",
                                                    "signed_contract_body": contract,
                                                    "market_id": self._market_id,
                                                   "updated": time.time(),
                                                   "merchant": contract_data_json['Seller']['seller_GUID'],
                                                   "buyer": self._transport._guid})
                except Exception, e:
                    self._log.error('Cannot update DB %s ' % e)

                order_to_notary = {}
                order_to_notary['type'] = 'order'
                order_to_notary['rawContract'] = contract
                order_to_notary['state'] = 'bid'

                # Send order to notary for approval
                self._transport.send(order_to_notary, notary)

            else:
                self._log.error('Could not verify signature of contract.')

        except Exception, e2:
            self._log.error(e2)


    def receive_order(self, new_order):  # action
        new_order['state'] = 'received'

        order_id = random.randint(0, 1000000)
        while self._db.numEntries("orders",{'id': order_id}) > 0:
            order_id = random.randint(0, 1000000)

        new_order['order_id'] = order_id
        self._db.insertEntry("orders",  new_order)
        self._transport.send(new_order, new_order['seller'].decode('hex'))

    def new_order(self, msg):

        self._log.debug('New Order: %s' % msg)

        # Save order locally in database
        order_id = random.randint(0, 1000000)
        while self._db.numEntries("orders",{'id': order_id}) > 0:
            order_id = random.randint(0, 1000000)

        buyer = {}
        buyer['Buyer'] = {}
        buyer['Buyer']['buyer_GUID'] = self._transport._guid
        buyer['Buyer']['buyer_BTC_uncompressed_pubkey'] = msg['btc_pubkey']
        buyer['Buyer']['buyer_pgp'] = self._transport.settings['PGPPubKey']
        buyer['Buyer']['buyer_deliveryaddr'] = "123 Sesame Street"
        buyer['Buyer']['note_for_seller'] = msg['message']
        buyer['Buyer']['buyer_order_id'] = order_id

        self._log.debug('Buyer: %s' % buyer)

        # Add to contract and sign
        seed_contract = msg.get('rawContract')

        gpg = self._gpg

        # Prepare contract body
        json_string = json.dumps(buyer, indent=0)
        seg_len = 52
        out_text = string.join(map(lambda x: json_string[x:x + seg_len],
                                   range(0, len(json_string), seg_len)), "\n")

        # Append new data to contract
        out_text = "%s\n%s" % (seed_contract, out_text)

        signed_data = gpg.sign(out_text, passphrase='P@ssw0rd',
                               keyid=self._transport.settings.get('PGPPubkeyFingerprint'))

        self._log.debug('Double-signed Contract: %s' % signed_data)

        # Hash the contract for storage
        contract_key = hashlib.sha1(str(signed_data)).hexdigest()
        hash_value = hashlib.new('ripemd160')
        hash_value.update(contract_key)
        contract_key = hash_value.hexdigest()

        self._db.updateEntries("orders", {'order_id': order_id}, {'market_id': self._transport._market_id,
                     'contract_key': contract_key,
                     'signed_contract_body': str(signed_data),
                     'state': 'new',
                     'updated': time.time(),
                     'note_for_merchant': msg['message']})

        # Send order to seller
        self.send_order(order_id, str(signed_data), msg['notary'])

    def get_seed_contract_from_doublesigned(self, contract):
        start_index = contract.find('- -----BEGIN PGP SIGNED MESSAGE-----', 0, len(contract))
        end_index = contract.find('- -----END PGP SIGNATURE-----', start_index, len(contract))
        contract = contract[start_index:end_index+29]
        return contract

    def get_json_from_doublesigned_contract(self, contract):
        start_index = contract.find("{", 0, len(contract))
        end_index = contract.find('- -----BEGIN PGP SIGNATURE-----', 0, len(contract))
        self._log.info(contract[start_index:end_index])
        return json.loads("".join(contract[start_index:end_index].split('\n')))


    def handle_bid_order(self, bid):

        self._log.info('Bid Order: %s' % bid)

        # Generate unique id for this bid
        order_id = random.randint(0, 1000000)
        while self._db.numEntries("contracts",{'id': order_id}) > 0:
            order_id = random.randint(0, 1000000)

        # Add to contract and sign
        contract = bid.get('rawContract')

        # Check signature and verify of seller and bidder contract
        seed_contract = self.get_seed_contract_from_doublesigned(contract)
        seed_contract_json = self.get_json_from_doublesigned_contract(seed_contract)
        #seed_contract = seed_contract.replace('- -----','-----')

        #self._log.debug('seed contract %s' % seed_contract)
        self._log.debug('seed contract json %s' % seed_contract_json)

        contract_stripped = "".join(contract.split('\n'))

        self._log.info(contract_stripped)
        bidder_pgp_start_index = contract_stripped.find("buyer_pgp", 0, len(contract_stripped))
        bidder_pgp_end_index = contract_stripped.find("buyer_GUID", 0, len(contract_stripped))
        bidder_pgp = contract_stripped[bidder_pgp_start_index+13:bidder_pgp_end_index]
        self._log.info(bidder_pgp)

        self._gpg.import_keys(bidder_pgp)
        v = self._gpg.verify(contract)
        if v:
            self._log.info('Sellers contract verified')

        notary = {}
        notary['Notary'] = {'notary_GUID': self._transport._guid,
                            'notary_BTC_uncompressed_pubkey': self._transport.settings['pubkey'],
                            'notary_pgp': self._transport.settings['PGPPubKey'],
                            'notary_fee': "1%",
                            'notary_order_id': order_id
                            }

        self._log.debug('Notary: %s' % notary)

        gpg = self._gpg

        # Prepare contract body
        json_string = json.dumps(notary, indent=0)
        seg_len = 52
        out_text = string.join(map(lambda x: json_string[x:x + seg_len],
                                   range(0, len(json_string), seg_len)), "\n")

        # Append new data to contract
        out_text = "%s\n%s" % (contract, out_text)

        signed_data = gpg.sign(out_text, passphrase='P@ssw0rd',
                               keyid=self._transport.settings.get('PGPPubkeyFingerprint'))

        self._log.debug('Double-signed Contract: %s' % signed_data)

        # Hash the contract for storage
        contract_key = hashlib.sha1(str(signed_data)).hexdigest()
        hash_value = hashlib.new('ripemd160')
        hash_value.update(contract_key)
        contract_key = hash_value.hexdigest()

        self._log.info('Order ID: %s' % order_id)

        # Push buy order to DHT and node if available
        # self._transport._dht.iterativeStore(self._transport, contract_key, str(signed_data), self._transport._guid)
        #self.update_listings_index()

        # Find Seller Data in Contract
        offer_data = ''.join(contract.split('\n')[8:])
        index_of_seller_signature = offer_data.find('- -----BEGIN PGP SIGNATURE-----', 0, len(offer_data))
        offer_data_json = "{\"Seller\": {"+ offer_data[0:index_of_seller_signature]
        self._log.info('Offer Data: %s' % offer_data_json)
        offer_data_json = json.loads(str(offer_data_json))

        # Find Buyer Data in Contract
        bid_data_index = offer_data.find('"Buyer"', index_of_seller_signature, len(offer_data))
        end_of_bid_index = offer_data.find('-----BEGIN PGP SIGNATURE', bid_data_index, len(offer_data))
        bid_data_json = "{" + offer_data[bid_data_index:end_of_bid_index]
        bid_data_json = json.loads(bid_data_json)
        self._log.info('Bid Data: %s' % bid_data_json)

        multisig = Multisig(None, 2, [offer_data_json['Seller']['seller_BTC_uncompressed_pubkey'].decode('hex'),
                                      bid_data_json['Buyer']['buyer_BTC_uncompressed_pubkey'].decode('hex'),
                                      self._transport.settings['pubkey'].decode('hex')])
        multisig_address = multisig.address


        self._db.insertEntry("orders", {'market_id': self._transport._market_id,
                     'contract_key': contract_key,
                     'signed_contract_body': str(signed_data),
                     'state': 'Notarized',
                     'order_id': order_id,
                     'merchant': offer_data_json['Seller']['seller_GUID'],
                     'buyer': bid_data_json['Buyer']['buyer_GUID'],
                     'address': multisig_address,
                     'item_price': offer_data_json['Contract']['item_price'],
                     'shipping_price': offer_data_json['Contract']['item_delivery']['shipping_price'] if offer_data_json['Contract']['item_delivery'].has_key('shipping_price') else "",
                     'note_for_merchant': bid_data_json['Buyer']['note_for_seller'],
                     "updated": time.time()})

        # Send order to seller and buyer
        self._log.info('Sending notarized contract to buyer and seller %s' % bid)

        notarized_order = {"type": "order",
                           "state": "Notarized",
                           "rawContract": str(signed_data)}

        self._log.info('SELLER %s' % offer_data_json['Seller']['seller_GUID'])

        self._transport.send(notarized_order, offer_data_json['Seller']['seller_GUID'])
        self._transport.send(notarized_order, bid_data_json['Buyer']['buyer_GUID'])

    def generate_order_id(self):
        order_id = random.randint(0, 1000000)
        while self._db.contracts.find({'id': order_id}).count() > 0:
            order_id = random.randint(0, 1000000)
        return order_id

    def handle_paid_order(self, msg):
        self._log.info('Entering Paid Order handling')
        self._log.debug('Paid Order %s' % msg)

        offer_data = ''.join(msg['signed_contract_body'].split('\n')[8:])
        index_of_seller_signature = offer_data.find('- - -----BEGIN PGP SIGNATURE-----', 0, len(offer_data))
        offer_data_json = offer_data[0:index_of_seller_signature]
        self._log.info('Offer Data: %s' % offer_data_json)
        offer_data_json = json.loads(str(offer_data_json))

        bid_data_index = offer_data.find('"Buyer"', index_of_seller_signature, len(offer_data))
        end_of_bid_index = offer_data.find('- -----BEGIN PGP SIGNATURE', bid_data_index, len(offer_data))
        bid_data_json = "{" + offer_data[bid_data_index:end_of_bid_index]
        bid_data_json = json.loads(bid_data_json)
        self._log.info('Bid Data: %s' % bid_data_json)

        buyer_order_id = bid_data_json['Buyer']['buyer_GUID']+'-'+str(bid_data_json['Buyer']['buyer_order_id'])

        self._db.updateEntries("orders", {'buyer_order_id': buyer_order_id}, {'state':'Buyer Paid',
                     "updated": time.time()})


    def handle_notarized_order(self, msg):
        self._log.info(msg['rawContract'])

        contract = msg['rawContract']

        # Find Seller Data in Contract
        offer_data = ''.join(contract.split('\n')[8:])
        index_of_seller_signature = offer_data.find('- - -----BEGIN PGP SIGNATURE-----', 0, len(offer_data))
        offer_data_json = offer_data[0:index_of_seller_signature]
        self._log.info('Offer Data: %s' % offer_data_json)
        offer_data_json = json.loads(str(offer_data_json))

        # Find Buyer Data in Contract
        bid_data_index = offer_data.find('"Buyer"', index_of_seller_signature, len(offer_data))
        end_of_bid_index = offer_data.find('- -----BEGIN PGP SIGNATURE', bid_data_index, len(offer_data))
        bid_data_json = "{" + offer_data[bid_data_index:end_of_bid_index]
        bid_data_json = json.loads(bid_data_json)
        self._log.info('Bid Data: %s' % bid_data_json)

         # Find Notary Data in Contract
        notary_data_index = offer_data.find('"Notary"', end_of_bid_index, len(offer_data))
        end_of_notary_index = offer_data.find('-----BEGIN PGP SIGNATURE', notary_data_index, len(offer_data))
        notary_data_json = "{" + offer_data[notary_data_index:end_of_notary_index]
        notary_data_json = json.loads(notary_data_json)
        self._log.info('Notary Data: %s' % notary_data_json)

        # Generate multi-sig address
        multisig = Multisig(None, 2, [offer_data_json['Seller']['seller_BTC_uncompressed_pubkey'].decode('hex'),
                                      bid_data_json['Buyer']['buyer_BTC_uncompressed_pubkey'].decode('hex'),
                                      notary_data_json['Notary']['notary_BTC_uncompressed_pubkey'].decode('hex')])
        multisig_address = multisig.address

        seller_GUID = offer_data_json['Seller']['seller_GUID']

        order_id = bid_data_json['Buyer']['buyer_order_id']

        contract_key = hashlib.sha1(str(contract)).hexdigest()
        hash_value = hashlib.new('ripemd160')
        hash_value.update(contract_key)
        contract_key = hash_value.hexdigest()

        if seller_GUID == self._transport._guid:
            self._log.info('I am the seller!')
            state = 'Waiting for Payment'

            merchant_order_id = random.randint(0, 1000000)
            while self._db.numEntries("orders",{'id': order_id}) > 0:
                merchant_order_id = random.randint(0, 1000000)

            buyer_id = str(bid_data_json['Buyer']['buyer_GUID'])+'-'+str(bid_data_json['Buyer']['buyer_order_id'])

            self._db.insertEntry("orders", {'market_id': self._transport._market_id,
                     'contract_key': contract_key,
                     'order_id': merchant_order_id,
                     'signed_contract_body': str(contract),
                     'state': state,
                     'buyer_order_id': buyer_id,
                     'merchant': offer_data_json['Seller']['seller_GUID'],
                     'buyer': bid_data_json['Buyer']['buyer_GUID'],
                     'notary': notary_data_json['Notary']['notary_GUID'],
                     'address': multisig_address,
                     'item_price': offer_data_json['Contract']['item_price'],
                     'shipping_price': offer_data_json['Contract']['item_delivery']['shipping_price'] if offer_data_json['Contract']['item_delivery'].has_key('shipping_price') else "",
                     'note_for_merchant': bid_data_json['Buyer']['note_for_seller'],
                     "updated": time.time()})

        else:
            self._log.info('I am the buyer')
            state = 'Need to Pay'

            self._db.updateEntries("orders", {'order_id': order_id}, {'market_id': self._transport._market_id,
                     'contract_key': contract_key,
                     'signed_contract_body': str(contract),
                     'state': state,
                     'merchant': offer_data_json['Seller']['seller_GUID'],
                     'buyer': bid_data_json['Buyer']['buyer_GUID'],
                     'notary': notary_data_json['Notary']['notary_GUID'],
                     'address': multisig_address,
                     'item_price': offer_data_json['Contract']['item_price'],
                     'shipping_price': offer_data_json['Contract']['item_delivery']['shipping_price'] if offer_data_json['Contract']['item_delivery'].has_key('shipping_price') else "",
                     'note_for_merchant': bid_data_json['Buyer']['note_for_seller'],
                     "updated": time.time()})



    # Order callbacks
    def on_order(self, msg):

        self._log.debug('ORDER %s' % msg)

        state = msg.get('state')

        if state == 'new':
            self.new_order(msg)

        if state == 'bid':
            self.handle_bid_order(msg)

        if state == 'Notarized':
            self._log.info('You received a notarized contract')
            self.handle_notarized_order(msg)

        if state == 'Paid':
            self._log.info('You received a payment notification')
            self.handle_paid_order(msg)

            #
            #
            # state = msg.get('state')
            #
            # buyer = msg.get('buyer').decode('hex')
            # seller = msg.get('seller').decode('hex')
            # myself = self._transport._myself.get_pubkey()
            #
            # if not buyer or not seller or not state:
            # self._log.info("Malformed order")
            #     return
            #
            # if not state == 'new' and not msg.get('id'):
            #     self._log.info("Order with no id")
            #     return
            #
            # # Check order state
            # if state == 'new':
            #     if myself == buyer:
            #         self.create_order(seller, msg.get('text', 'no comments'))
            #     elif myself == seller:
            #         self._log.info(msg)
            #         self.accept_order(msg)
            #     else:
            #         self._log.info("Not a party to this order")
            #
            # elif state == 'cancelled':
            #     if myself == seller or myself == buyer:
            #         self._log.info('Order cancelled')
            #     else:
            #         self._log.info("Order not for us")
            #
            # elif state == 'accepted':
            #     if myself == seller:
            #         self._log.info("Bad subjects [%s]" % state)
            #     elif myself == buyer:
            #         # wait for confirmation
            #         self._db.orders.update({"id": msg['id']}, {"$set": msg}, True)
            #         pass
            #     else:
            #         self._log.info("Order not for us")
            # elif state == 'paid':
            #     if myself == seller:
            #         # wait for  confirmation
            #         pass
            #     elif myself == buyer:
            #         self.pay_order(msg)
            #     else:
            #         self._log.info("Order not for us")
            # elif state == 'sent':
            #     if myself == seller:
            #         self.send_order(msg)
            #     elif myself == buyer:
            #         # wait for confirmation
            #         pass
            #     else:
            #         self._log.info("Order not for us")
            # elif state == 'received':
            #     if myself == seller:
            #         pass
            #         # ok
            #     elif myself == buyer:
            #         self.receive_order(msg)
            #     else:
            #         self._log.info("Order not for us")
            #
            # # Store order
            # if msg.get('id'):
            #     if self.orders.find({id: msg['id']}):
            #         self.orders.update({'id': msg['id']}, {"$set": {'state': msg['state']}}, True)
            #     else:
            #         self.orders.update({'id': msg['id']}, {"$set": {msg}}, True)
