from multisig import Multisig
import threading
import json
import random
import logging
import subprocess
import protocol
import pycountry
import gnupg
import os
import obelisk
import pybitcointools
from pybitcointools import *
import arithmetic

import tornado.websocket
from zmq.eventloop import ioloop
from twisted.internet import reactor
import trust
from backuptool import BackupTool

ioloop.install()


class ProtocolHandler:
    def __init__(self, transport, market, handler, db, loop_instance):
        self._market = market
        self._transport = transport
        self._handler = handler
        self._db = db

        # register on transport events to forward..
        self._transport.add_callbacks([
            ('peer', self.on_node_peer),
            ('peer_remove', self.on_node_remove_peer),
            ('node_page', self.on_node_page),
            ('listing_results', self.on_listing_results),
            ('listing_result', self.on_listing_result),
            ('release_funds_tx', self.on_release_funds_tx),
            ('all', self.on_node_message)
        ])

        # handlers from events coming from websocket, we shouldnt need this
        self._handlers = {
            "load_page": self.client_load_page,
            "connect": self.client_connect,
            "peers": self.client_peers,
            "query_page": self.client_query_page,
            "review": self.client_review,
            "order": self.client_order,
            "search": self.client_query_network_for_products,
            "shout": self.client_shout,
            "get_notaries": self.client_get_notaries,
            "add_trusted_notary": self.client_add_trusted_notary,
            "remove_trusted_notary": self.client_remove_trusted_notary,
            "query_store_products": self.client_query_store_products,
            "check_order_count": self.client_check_order_count,
            "query_orders": self.client_query_orders,
            "query_contracts": self.client_query_contracts,
            "query_messages": self.client_query_messages,
            "send_message": self.client_send_message,
            "update_settings": self.client_update_settings,
            "query_order": self.client_query_order,
            "pay_order": self.client_pay_order,
            "ship_order": self.client_ship_order,
            "release_payment": self.client_release_payment,
            "remove_contract": self.client_remove_contract,
            "generate_secret": self.client_generate_secret,
            "welcome_dismissed": self.client_welcome_dismissed,
            "republish_contracts": self.client_republish_contracts,
            "import_raw_contract": self.client_import_raw_contract,
            "create_contract": self.client_create_contract,
            "clear_dht_data": self.client_clear_dht_data,
            "clear_peers_data": self.client_clear_peers_data,
            "read_log": self.client_read_log,
            "create_backup": self.client_create_backup,
        }

        self._timeouts = []

        #unused for now, wipe it if you want later.
        self.loop = loop_instance

        self._log = logging.getLogger(
            '[%s] %s' % (self._transport._market_id, self.__class__.__name__)
        )

    def send_opening(self):
        peers = self.get_peers()

        countryCodes = []
        for country in pycountry.countries:
            countryCodes.append({"code": country.alpha2, "name": country.name})

        settings = self._market.get_settings()
        # globalTrust = trust.getTrust(self._transport.guid)

        # print(trust.get(self._transport.guid))

        message = {
            'type': 'myself',
            'pubkey': settings.get('pubkey'),
            'peers': peers,
            'settings': settings,
            'guid': self._transport.guid,
            'sin': self._transport.sin,
            'uri': self._transport._uri,
            'countryCodes': countryCodes,
            # 'globalTrust': globalTrust
        }

        # print('Sending opening')
        self.send_to_client(None, message)

        burnAddr = trust.burnaddr_from_guid(self._transport.guid)
        # def found_unspent(amount_in_satoshis):

        def found_unspent(amount):
            # print("found_unspent")
            self.send_to_client(None, {
                'type': 'burn_info_available',
                'amount': amount,
                'addr': burnAddr
            })

        # print("getting unspent")

        trust.get_unspent(burnAddr, found_unspent)

    def client_read_log(self, socket_handler, msg):
        self._market.p = subprocess.Popen(
            ["tail", "-f", "logs/development.log", "logs/production.log"],
            stdout=subprocess.PIPE)

        self.stream = tornado.iostream.PipeIOStream(
            self._market.p.stdout.fileno()
        )
        self.stream.read_until("\n", self.line_from_nettail)

    def line_from_nettail(self, data):
        self.send_to_client(None, {"type": "log_output", "line": data})
        self.stream.read_until("\n", self.line_from_nettail)

    def on_listing_results(self, msg):
        self._log.debug('Found results %s' % msg)
        self.send_to_client(None, {
            "type": "store_contracts",
            "products": msg['contracts']
        })

    def on_listing_result(self, msg):
        self._log.debug('Found result %s' % msg)
        self.send_to_client(None, {
            "type": "store_contract",
            "contract": msg
        })

    def client_load_page(self, socket_handler, msg):
        self.send_to_client(None, {"type":"load_page"})

    def client_add_trusted_notary(self, socket_handler, msg):
        self._log.info('Adding trusted notary %s' % msg)
        self._market.add_trusted_notary(msg.get('guid'), msg.get('nickname'))
        #self.send_to_client(None, {"type":"load_page"})

    def client_remove_trusted_notary(self, socket_handler, msg):
        self._log.info('Removing trusted notary %s' % msg)
        self._market.remove_trusted_notary(msg.get('guid'))

    def client_get_notaries(self, socket_handler, msg):
        self._log.debug('Retrieving notaries')
        notaries = self._market.get_notaries()
        self._log.debug('Getting notaries %s' % notaries)
        self.send_to_client(None, {
            "type": "settings_notaries",
            "notaries": notaries
        })

    def client_clear_dht_data(self, socket_handler, msg):
        self._log.debug('Clearing DHT Data')
        self._db.deleteEntries("datastore")

    def client_clear_peers_data(self, socket_handler, msg):
        self._log.debug('Clearing Peers Data')
        self._db.deleteEntries("peers")

    # Requests coming from the client
    def client_connect(self, socket_handler, msg):
        self._log.info("Connection command: ", msg)
        self._transport.connect(msg['uri'], lambda x: None)
        self.send_ok()

    def client_peers(self, socket_handler, msg):
        self._log.info("Peers command")
        self.send_to_client(None, {"type": "peers", "peers": self.get_peers()})

    def client_welcome_dismissed(self, socket_handler, msg):
        self._market.disable_welcome_screen()

    def client_check_order_count(self, socket_handler, msg):
        self._log.debug('Checking order count')
        self.send_to_client(None, {
            "type": "order_count",
            "count": self._db.numEntries(
                "orders",
                "market_id = '%s' and state = '%s'" %
                (self._transport._market_id, "Waiting for Payment")
            )
        })

    def refresh_peers(self):
        self._log.info("Peers command")
        self.send_to_client(None, {"type": "peers", "peers": self.get_peers()})

    def client_query_page(self, socket_handler, msg):
        findGUID = msg['findGUID']

        query_id = random.randint(0, 1000000)
        self._timeouts.append(query_id)

        def cb(msg, query_id):
            self._log.info('Received a query page response: %s' % query_id)

            # try:
            #     self._timeouts.remove(query_id)
            # except ValueError:
            #     self._log.error('Cannot find that query id')
            # if not success:
            #     self.send_to_client(None, {
            #         "type": "peers",
            #         "peers": self.get_peers()
            #     })

        self._market.query_page(
            findGUID,
            lambda msg, query_id=query_id: cb(msg, query_id)
        )

        def unreachable_market(query_id):
            self._log.info('Cannot reach market, try port forwarding')
            if query_id in self._timeouts:
                self._log.info('Unreachable Market: %s' % msg)

                for peer in self._transport._dht._activePeers:
                    if peer._guid == findGUID:
                        self._transport._dht._activePeers.remove(peer)

                self.refresh_peers()

        # self.loop.add_timeout(
        #     time.time() + .5,
        #     lambda query_id=query_id: unreachable_market(query_id)
        # )

    def client_query_orders(self, socket_handler=None, msg=None):

        self._log.info("Querying for Orders %s " % msg)

        if 'page' in msg:
            page = msg['page']
        else:
            page = 0

        if msg is not None and 'merchant' in msg:
            if msg['merchant'] == 1:
                orders = self._market.orders.get_orders(page, True)
            else:
                orders = self._market.orders.get_orders(page, False)
        else:
            orders = self._market.orders.get_orders(page)

        self.send_to_client(None, {
            "type": "myorders",
            "page": page,
            "total": orders['total'],
            "orders": orders['orders']
        })

    def client_query_contracts(self, socket_handler, msg):

        self._log.info("Querying for Contracts")

        page = msg['page'] if 'page' in msg else 0
        contracts = self._market.get_contracts(page)

        self.send_to_client(None, {
            "type": "contracts",
            "contracts": contracts
        })

    def client_query_messages(self, socket_handler, msg):

        self._log.info("Querying for Messages")

        # Query bitmessage for messages
        messages = self._market.get_messages()

        self.send_to_client(None, {"type": "messages", "messages": messages})

    def client_send_message(self, socket_handler, msg):

        self._log.info("Sending message")

        # Send message with market's bitmessage
        self._market.send_message(msg)

    def client_republish_contracts(self, socket_handler, msg):

        self._log.info("Republishing contracts")
        self._market.republish_contracts()

    def client_import_raw_contract(self, socket_handler, contract):
        self._log.info(
            "Importing New Contract "\
            "(NOT IMPLEMENTED! TODO: Market.import_contract(contract)"
        )
        #self._market.import_contract(contract)

    # Get a single order's info
    def client_query_order(self, socket_handler, msg):
        order = self._market.orders.get_order(msg['orderId'])
        self.send_to_client(None, {"type": "orderinfo", "order": order})

    def client_update_settings(self, socket_handler, msg):
        self._log.info("Updating settings: %s" % msg)
        self.send_to_client(None, {"type": "settings", "values": msg})
        if msg['settings'].get('btc_pubkey'):
            del msg['settings']['btc_pubkey']
        self._market.save_settings(msg['settings'])

    def client_create_contract(self, socket_handler, contract):
        self._log.info("New Contract: %s" % contract)
        self._market.save_contract(contract)

    def client_remove_contract(self, socket_handler, msg):
        self._log.info("Remove contract: %s" % msg)
        self._market.remove_contract(msg)

    def client_pay_order(self, socket_handler, msg):

        self._log.info("Marking Order as Paid: %s" % msg)
        order = self._market.orders.get_order(msg['orderId'])

        order['shipping_address'] = self._market.shipping_address()

        # Send to exchange partner
        self._market.orders.pay_order(order, msg['orderId'])

    def client_ship_order(self, socket_handler, msg):

        self._log.info("Shipping order out: %s" % msg)

        order = self._market.orders.get_order(msg['orderId'])

        # Send to exchange partner
        self._market.orders.ship_order(
            order, msg['orderId'], msg['paymentAddress']
        )

    def client_release_payment(self, socket_handler, msg):
        self._log.info('Releasing payment to Merchant %s' % msg)

        order = self._market.orders.get_order(msg['orderId'])
        contract = order['signed_contract_body']

        # Find Seller Data in Contract
        offer_data = ''.join(contract.split('\n')[8:])
        index_of_seller_signature = offer_data.find(
            '- - -----BEGIN PGP SIGNATURE-----', 0, len(offer_data)
        )
        offer_data_json = offer_data[0:index_of_seller_signature]
        offer_data_json = json.loads(offer_data_json)
        self._log.info('Offer Data: %s' % offer_data_json)

        # Find Buyer Data in Contract
        bid_data_index = offer_data.find(
            '"Buyer"', index_of_seller_signature, len(offer_data)
        )
        end_of_bid_index = offer_data.find(
            '- -----BEGIN PGP SIGNATURE', bid_data_index, len(offer_data)
        )
        bid_data_json = "{"
        bid_data_json += offer_data[bid_data_index:end_of_bid_index]
        bid_data_json = json.loads(bid_data_json)

        # Find Notary Data in Contract
        notary_data_index = offer_data.find(
            '"Notary"', end_of_bid_index, len(offer_data)
        )
        end_of_notary_index = offer_data.find(
            '-----BEGIN PGP SIGNATURE', notary_data_index, len(offer_data)
        )
        notary_data_json = "{"
        notary_data_json += offer_data[notary_data_index:end_of_notary_index]
        notary_data_json = json.loads(notary_data_json)
        self._log.info('Notary Data: %s' % notary_data_json)

        try:
            client = obelisk.ObeliskOfLightClient(
                'tcp://obelisk2.airbitz.co:9091'
            )

            seller = offer_data_json['Seller']
            buyer = bid_data_json['Buyer']
            notary = notary_data_json['Notary']

            pubkeys = [
                seller['seller_BTC_uncompressed_pubkey'],
                buyer['buyer_BTC_uncompressed_pubkey'],
                notary['notary_BTC_uncompressed_pubkey']
            ]

            script = mk_multisig_script(pubkeys, 2, 3)
            multi_address = scriptaddr(script)

            def cb(ec, history, order):

                # Debug
                #self._log.info('%s %s' % (ec, history))

                settings = self._market.get_settings()
                private_key = settings.get('privkey')

                if ec is not None:
                    self._log.error("Error fetching history: %s" % ec)
                    # TODO: Send error message to GUI
                    return

                # Create unsigned transaction
                unspent = [row[:4] for row in history if row[4] is None]

                # Send all unspent outputs (everything in the address) minus the fee
                total_amount = 0
                inputs = []
                for row in unspent:
                    assert len(row) == 4
                    inputs.append(str(row[0].encode('hex'))+":"+str(row[1]))
                    value = row[3]
                    total_amount += value



                # Constrain fee so we don't get negative amount to send
                fee = min(total_amount, 10000)
                send_amount = total_amount - fee

                payment_output = order['payment_address']
                print payment_output
                print 'PAYMENT OUTPUT',"16uniUFpbhrAxAWMZ9qEkcT9Wf34ETB4Tt:%s" % send_amount
                print 'inputs', inputs
                tx = mktx(inputs, [str(payment_output)+":"+str(send_amount)])
                print 'TRANSACTION: %s' % tx

                signatures = []
                for x in range(0,len(inputs)):
                    ms = multisign(tx, x, script, private_key)
                    print 'buyer sig', ms
                    signatures.append(ms)

                print signatures




                self._market.release_funds_to_merchant(buyer['buyer_order_id'], tx, script, signatures, order.get('merchant'))




            def get_history():
                client.fetch_history(multi_address, lambda ec, history, order=order: cb(ec, history, order))



            reactor.callFromThread(get_history)

        except Exception, e:
            self._log.error('%s' % e)

    def on_release_funds_tx(self, msg):
        self._log.info('Receiving signed tx from buyer')

        buyer_order_id = str(msg['senderGUID'])+'-'+str(msg['buyer_order_id'])
        order = self._market.orders.get_order(buyer_order_id, by_buyer_id=True)
        contract = order['signed_contract_body']

        # Find Seller Data in Contract
        offer_data = ''.join(contract.split('\n')[8:])
        index_of_seller_signature = offer_data.find(
            '- - -----BEGIN PGP SIGNATURE-----', 0, len(offer_data)
        )
        offer_data_json = offer_data[0:index_of_seller_signature]
        offer_data_json = json.loads(offer_data_json)
        self._log.info('Offer Data: %s' % offer_data_json)

        # Find Buyer Data in Contract
        bid_data_index = offer_data.find(
            '"Buyer"', index_of_seller_signature, len(offer_data)
        )
        end_of_bid_index = offer_data.find(
            '- -----BEGIN PGP SIGNATURE', bid_data_index, len(offer_data)
        )
        bid_data_json = "{"
        bid_data_json += offer_data[bid_data_index:end_of_bid_index]
        bid_data_json = json.loads(bid_data_json)

        # Find Notary Data in Contract
        notary_data_index = offer_data.find(
            '"Notary"', end_of_bid_index, len(offer_data)
        )
        end_of_notary_index = offer_data.find(
            '-----BEGIN PGP SIGNATURE', notary_data_index, len(offer_data)
        )
        notary_data_json = "{"
        notary_data_json += offer_data[notary_data_index:end_of_notary_index]
        notary_data_json = json.loads(notary_data_json)
        self._log.info('Notary Data: %s' % notary_data_json)

        try:
            client = obelisk.ObeliskOfLightClient(
                'tcp://obelisk2.airbitz.co:9091'
            )

            seller = offer_data_json['Seller']
            buyer = bid_data_json['Buyer']
            notary = notary_data_json['Notary']

            pubkeys = [
                seller['seller_BTC_uncompressed_pubkey'],
                buyer['buyer_BTC_uncompressed_pubkey'],
                notary['notary_BTC_uncompressed_pubkey']
            ]

            script = msg['script']
            tx = msg['tx']
            multi_addr = scriptaddr(script)

            def cb(ec, history, order):

               # Debug
                #self._log.info('%s %s' % (ec, history))

                if ec is not None:
                    self._log.error("Error fetching history: %s" % ec)
                    # TODO: Send error message to GUI
                    return

                unspent = [row[:4] for row in history if row[4] is None]

                # Send all unspent outputs (everything in the address) minus the fee
                inputs = []
                for row in unspent:
                    assert len(row) == 4
                    inputs.append(str(row[0].encode('hex'))+":"+str(row[1]))

                seller_signatures = []
                print 'private key ', self._transport.settings['privkey']
                for x in range(0,len(inputs)):
                    ms = multisign(tx, x, script, self._transport.settings['privkey'])
                    print 'seller sig', ms
                    seller_signatures.append(ms)

                tx2 = pybitcointools.apply_multisignatures(tx, 0, script, seller_signatures[0], msg['signatures'][0])

                print 'FINAL SCRIPT: %s' % tx2
                print 'Sent', pybitcointools.eligius_pushtx(tx2)

            def get_history():
                client.fetch_history(multi_addr, lambda ec, history, order=order: cb(ec, history, order))

            reactor.callFromThread(get_history)

        except Exception, e:
            self._log.error('%s' % e)


    def client_generate_secret(self, socket_handler, msg):
        self._transport._generate_new_keypair()
        self.send_opening()

    def client_order(self, socket_handler, msg):
        self._market.orders.on_order(msg)

    def client_review(self, socket_handler, msg):
        pubkey = msg['pubkey'].decode('hex')
        text = msg['text']
        rating = msg['rating']
        self._market.reputation.create_review(pubkey, text, rating)

    # Search for markets ATM
    # TODO: multi-faceted search support
    def client_search(self, socket_handler, msg):

        self._log.info("[Search] %s" % msg)
        self._transport._dht.iterativeFindValue(
            msg['key'], callback=self.on_node_search_value
        )
        # self._log.info('Result: %s' % result)

        #response = self._market.lookup(msg)
        #if response:
        #    self._log.info(response)
        #self.send_to_client(*response)

    def client_query_network_for_products(self, socket_handler, msg):

        self._log.info("Querying for Contracts %s" % msg)

        self._transport._dht.find_listings_by_keyword(
            self._transport,
            msg['key'].upper(),
            callback=self.on_find_products
        )

    def client_query_store_products(self, socket_handler, msg):
        self._log.info("Searching network for contracts")

        self._transport._dht.find_listings(
            self._transport,
            msg['key'],
            callback=self.on_find_products_by_store
        )

    def client_create_backup(self, socket_handler, msg):
        """Currently hardcoded for testing: need to find out Installation path.
        Talk to team about right location for backup files
        they might have to be somewhere outside the installation path
        as some OSes might not allow the modification of the installation folder
        e.g. MacOS won't allow for changes if the .app has been signed.
        and all files created by the app, have to be outside, usually at
        ~/Library/Application Support/OpenBazaar/backups ??
        """
        def on_backup_done(backupPath):
            self._log.info('Backup sucessfully created at ' + backupPath)
            self.send_to_client(None,
                                {'type': 'create_backup_result',
                                 'result': 'success',
                                 'detail': backupPath})

        def on_backup_error(error):
            self._log.info('Backup error:' + str(error.strerror))
            self.send_to_client(None,
                                {'type': 'create_backup_result',
                                 'result': 'failure',
                                 'detail': error.strerror})

        #TODO: Make backup path configurable on server settings before run.sh
        OB_PATH = os.path.realpath(os.path.abspath(__file__))[:os.path.realpath(os.path.abspath(__file__)).find('/node')]
        BACKUP_PATH = OB_PATH + os.sep + "html" + os.sep + 'backups'
        BackupTool.backup(OB_PATH,
                          BACKUP_PATH,
                          on_backup_done,
                          on_backup_error)

    def on_find_products_by_store(self, results):

        self._log.info('Found Contracts: %s' % type(results))
        self._log.info(results)

        if len(results) > 0 and type(results[0]) == str:
            results = json.loads(results[0])

        self._log.info(results)

        if 'type' not in results:
            return
        else:
            self._log.debug('Results: %s ' % results['contracts'])

        if len(results) > 0 and 'data' in results:

            data = results['data']
            contracts = data['contracts']
            signature = results['signature']
            self._log.info('Signature: %s' % signature)

            # TODO: Validate signature of listings matches data
            # self._transport._myself.

            # Go get listing metadata and then send it to the GUI
            for contract in contracts:
                self._transport._dht.iterativeFindValue(
                    contract,
                    callback=lambda msg, key=contract: self.on_node_search_value(
                        msg, key
                    )
                )

                # self.send_to_client(None, {
                #     "type": "store_products",
                #     "products": listings
                # })

    def on_find_products(self, results):

        self._log.info('Found Contracts: %s' % type(results))
        self._log.info(results)

        if len(results):
            if 'listings' in results:
            # data = results['data']
            # contracts = data['contracts']
            # signature = results['signature']
            # self._log.info('Signature: %s' % signature)

            # TODO: Validate signature of listings matches data
            # self._transport._myself.

            # Go get listing metadata and then send it to the GUI
                for contract in results['listings']:
                    self._transport._dht.iterativeFindValue(
                        contract,
                        callback=lambda msg, key=contract: self.on_global_search_value(
                            msg, key
                        )
                    )

                # self.send_to_client(None, {
                #     "type": "store_products",
                #     "products": listings
                # })

    def client_shout(self, socket_handler, msg):
        msg['uri'] = self._transport._uri
        msg['pubkey'] = self._transport.pubkey
        msg['senderGUID'] = self._transport.guid
        msg['senderNick'] = self._transport._nickname
        self._transport.send(protocol.shout(msg))

    def on_node_search_value(self, results, key):

        if results:

            self._log.debug('Listing Data: %s %s' % (results, key))

            # Fix newline issue
            # self._log.info(results_data)

            # Import gpg pubkey
            gpg = gnupg.GPG()

            # Retrieve JSON from the contract
            # 1) Remove PGP Header
            contract_data = ''.join(results.split('\n')[3:])
            index_of_signature = contract_data.find(
                '-----BEGIN PGP SIGNATURE-----', 0, len(contract_data)
            )
            contract_data_json = contract_data[0:index_of_signature]

            try:
                contract_data_json = json.loads(contract_data_json)
                seller = contract_data_json.get('Seller')
                seller_pubkey = seller.get('seller_PGP')

                gpg.import_keys(seller_pubkey)

                v = gpg.verify(results)
                if v:

                    self.send_to_client(None, {
                        "type": "new_listing",
                        "data": contract_data_json,
                        "key": key,
                        "rawContract": results
                    })
                else:
                    self._log.error('Could not verify signature of contract.')
            except:
                self._log.debug('Error getting JSON contract')
        else:
            self._log.info('No results')

    def on_global_search_value(self, results, key):

        if results:

            self._log.debug('Listing Data: %s %s' % (results, key))

            # Fix newline issue
            # self._log.info(results_data)

            # Import gpg pubkey
            gpg = gnupg.GPG()

            # Retrieve JSON from the contract
            # 1) Remove PGP Header
            contract_data = ''.join(results.split('\n')[3:])
            index_of_signature = contract_data.find(
                '-----BEGIN PGP SIGNATURE-----', 0, len(contract_data)
            )
            contract_data_json = contract_data[0:index_of_signature]

            try:
                contract_data_json = json.loads(contract_data_json)
                seller_pubkey = contract_data_json.get(
                    'Seller'
                ).get(
                    'seller_PGP'
                )

                gpg.import_keys(seller_pubkey)

                v = gpg.verify(results)
                if v:

                    seller = contract_data_json.get('Seller')
                    contract_guid = seller.get('seller_GUID')
                    self._log.info('my guid %s' % self._transport._nickname)
                    if contract_guid == self._transport._guid:
                        nickname = self._transport._nickname
                    else:
                        routing_table = self._transport._dht._routingTable
                        peer = routing_table.getContact(contract_guid)
                        nickname = peer._nickname if peer is not None else ""

                    self.send_to_client(None, {
                        "type": "global_search_result",
                        "data": contract_data_json,
                        "key": key,
                        "rawContract": results,
                        "nickname": nickname
                    })
                else:
                    self._log.error('Could not verify signature of contract.')
            except:
                self._log.debug('Error getting JSON contract')
        else:
            self._log.info('No results')

    def on_node_search_results(self, results):
        if len(results) > 1:
            self.send_to_client(None, {
                "type": "peers",
                "peers": self.get_peers()
            })
        else:
            # Add peer to list of markets
            self.on_node_peer(results[0])

            # Load page for the store
            self._market.query_page(results[0]._guid)

    # messages coming from "the market"
    def on_node_peer(self, peer):
        self._log.info("Add peer: %s" % peer)

        response = {'type': 'peer',
                    'pubkey': peer._pub
                    if peer._pub
                    else 'unknown',
                    'guid': peer._guid
                    if peer._guid
                    else '',
                    'uri': peer._address}
        self.send_to_client(None, response)

    def on_node_remove_peer(self, msg):
        self.send_to_client(None, msg)

    def on_node_page(self, page):
        self.send_to_client(None, page)

    def on_node_message(self, *args):
        first = args[0]
        if isinstance(first, dict):
            self.send_to_client(None, first)
        else:
            self._log.info("can't format")

    # send a message
    def send_to_client(self, error, result):
        assert error is None or type(error) == str
        response = {
            "id": random.randint(0, 1000000),
            "result": result
        }
        if error:
            response["error"] = error
        self._handler.queue_response(response)

    def send_ok(self):
        self.send_to_client(None, {"type": "ok"})

    # handler a request
    def handle_request(self, socket_handler, request):
        command = request["command"]
        self._log.info('(I) ws.ProtocolHandler.handle_request of: ' + command)
        if command not in self._handlers:
            return False
        params = request["params"]
        # Create callback handler to write response to the socket.
        self._log.debug('found a handler!')
        self._handlers[command](socket_handler, params)
        return True

    def get_peers(self):
        peers = []

        for peer in self._transport._dht._activePeers:

            self._log.debug('get peer %s' % peer)

            if hasattr(peer, '_address'):
                peer_item = {'uri': peer._address}
                if peer._pub:
                    peer_item['pubkey'] = peer._pub.encode('hex')
                else:
                    peer_item['pubkey'] = 'unknown'

                peer_item['guid'] = peer._guid
                if peer._guid:
                    peer_item['sin'] = obelisk.EncodeBase58Check(
                        '\x0F\x02%s' + peer._guid.decode('hex')
                    )
                peer_item['nick'] = peer._nickname
                self._log.info('Peer Nick %s ' % peer)
                peers.append(peer_item)

        return peers


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    # Set of WebsocketHandler
    listeners = set()
    # Protects listeners
    listen_lock = threading.Lock()

    def initialize(self, transport, market, db):
        self._loop = tornado.ioloop.IOLoop.instance()
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info("Initialize websockethandler")
        self._app_handler = ProtocolHandler(
            transport, market, self, db, self._loop
        )
        self.market = market
        self._transport = transport

    def open(self):
        self._log.info('Websocket open')
        self._app_handler.send_opening()
        with WebSocketHandler.listen_lock:
            self.listeners.add(self)
        self._connected = True

    def on_close(self):
        self._log.info("Websocket closed")
        disconnect_msg = {
            'command': 'disconnect_client',
            'id': 0,
            'params': []
        }
        self._connected = False
        self._app_handler.handle_request(self, disconnect_msg)
        with WebSocketHandler.listen_lock:
            try:
                self.listeners.remove(self)
            except:
                self._log.error('Cannot remove socket listener')

    @staticmethod
    def _check_request(request):
        return "command" in request and "id" in request and \
               "params" in request and type(request["params"]) == dict
        # request.has_key("params") and type(request["params"]) == list

    def on_message(self, message):
        # self._log.info('[On Message]: %s' % message)
        try:
            request = json.loads(message)
        except:
            logging.error("Error decoding message: %s", message, exc_info=True)

        # Check request is correctly formed.
        if not self._check_request(request):
            logging.error("Malformed request: %s", request, exc_info=True)
            return
        if self._app_handler.handle_request(self, request):
            return

    def _send_response(self, response):
        if self.ws_connection:
            # self._log.info('Response: %s' % response)

            self.write_message(json.dumps(response))
            #try:
            #    self.write_message(json.dumps(response))
            #except tornado.websocket.WebSocketClosedError:
            #    logging.warning("Dropping response to closed socket: %s",
            #       response, exc_info=True)

    def queue_response(self, response):
        def send_response(*args):
            self._send_response(response)

        try:
            # calling write_message or the socket is not thread safe
            self._loop.current().add_callback(send_response)
        except:
            logging.error("Error adding callback", exc_info=True)
