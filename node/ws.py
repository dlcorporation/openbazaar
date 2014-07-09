import threading
import json
import ast
import random
import logging

import tornado.websocket
import tornado.ioloop

import protocol
import pycountry
import gnupg
import pprint


class ProtocolHandler:
    def __init__(self, transport, market, handler):
        self._market = market
        self._transport = transport
        self._handler = handler

        # register on transport events to forward..
        self._transport.add_callback('peer', self.on_node_peer)
        self._transport.add_callback('peer_remove', self.on_node_remove_peer)
        self._transport.add_callback('node_page', self.on_node_page)
        self._transport.add_callback('all', self.on_node_message)

        # handlers from events coming from websocket, we shouldnt need this
        self._handlers = {
            "connect":          self.client_connect,
            "peers":          self.client_peers,
            "query_page":          self.client_query_page,
            "review":          self.client_review,
            "order":          self.client_order,
            "search":          self.client_query_store_products,
            "shout":          self.client_shout,
            "query_store_products":	  self.client_query_store_products,
            "query_orders":	  self.client_query_orders,
            "query_contracts":	  self.client_query_contracts,
            "query_messages":	  self.client_query_messages,
            "send_message":	  self.client_send_message,
            "update_settings":	self.client_update_settings,
            "query_order":	self.client_query_order,
            "pay_order":	self.client_pay_order,
            "ship_order":	self.client_ship_order,
            "save_product":	self.client_save_product,
            "remove_contract":	self.client_remove_contract,
            "generate_secret":	self.client_generate_secret,
            "republish_listing":	  self.client_republish_listing,
            "import_raw_contract":	  self.client_import_raw_contract,
            "create_contract":	  self.client_create_contract,
        }

        self._log = logging.getLogger('[%s] %s' % (self._transport._market_id, self.__class__.__name__))

    def send_opening(self):
        peers = self.get_peers()

        countryCodes = []
        for country in pycountry.countries:
          countryCodes.append({"code":country.alpha2, "name":country.name})

        settings = self._market.get_settings()

        message = {
            'type': 'myself',
            'pubkey': self._transport._myself.get_pubkey().encode('hex'),
            'peers': peers,
            'settings': settings,
            'guid': self._transport.guid,
            'countryCodes': countryCodes,
            'reputation': []#self._transport.reputation.get_my_reputation()
        }

        self.send_to_client(None, message)

    # Requests coming from the client
    def client_connect(self, socket_handler, msg):
        self._log.info("Connection command: ", msg)
        self._transport.init_peer(msg)
        self.send_ok()

    def client_peers(self, socket_handler, msg):
        self._log.info("Peers command")
        self.send_to_client(None, {"type": "peers", "peers": self.get_peers()})

    def refresh_peers(self):
        self._log.info("Peers command")
        self.send_to_client(None, {"type": "peers", "peers": self.get_peers()})

    def client_query_page(self, socket_handler, msg):
        self._log.info("Message: %s" % msg)
        findGUID = msg['findGUID']

        def cb(success):
            if not success:
                self.send_to_client(None, {"type": "peers", "peers": self.get_peers()})

        self._market.query_page(findGUID, cb)
        #self._market.reputation.query_reputation(guid)


    def client_query_orders(self, socket_handler, msg):

        self._log.info("Querying for Orders")

        # Query mongo for orders
        orders = self._market.orders.get_orders()

        self.send_to_client(None, { "type": "myorders", "orders": orders } )

    def client_query_contracts(self, socket_handler, msg):

        self._log.info("Querying for Contracts")

        # Query mongo for products
        contracts = self._market.get_contracts()

        self.send_to_client(None, { "type": "contracts", "contracts": contracts } )

    def client_query_messages(self, socket_handler, msg):

        self._log.info("Querying for Messages")

        # Query bitmessage for messages
        messages = self._market.get_messages()

        self.send_to_client(None, { "type": "messages", "messages": messages } )

    def client_send_message(self, socket_handler, msg):

        self._log.info("Sending message")

        # Send message with market's bitmessage
        self._market.send_message(msg)

    def client_republish_listing(self, socket_handler, msg):

        self._log.info("Republishing product listing")

        # Query mongo for products
        products = self._market.republish_listing(msg)

    def client_import_raw_contract(self, socket_handler, contract):

        self._log.info("Importing New Contract")
        self._market.import_contract(contract)

    # Get a single order's info
    def client_query_order(self, socket_handler, msg):

        # Query mongo for order
        order = self._market.orders.get_order(msg['orderId'])

        self.send_to_client(None, { "type": "orderinfo", "order": order } )


    def client_update_settings(self, socket_handler, msg):
        self._log.info("Updating settings: %s" % msg)

        self.send_to_client(None, { "type": "settings", "values": msg })

        # Update settings in mongo
        self._market.save_settings(msg['settings'])

    def client_save_product(self, socket_handler, msg):
        #self._log.info("Save product: %s" % msg)

        # Update settings in mongo
        self._market.save_product(msg)

    def client_create_contract(self, socket_handler, contract):
        self._log.info("New Contract: %s" % contract)

        # Update settings in mongo
        self._market.save_contract(contract)

    def client_remove_contract(self, socket_handler, msg):
        self._log.info("Remove contract: %s" % msg)

        # Update settings in mongo
        self._market.remove_contract(msg)

    def client_pay_order(self, socket_handler, msg):

        self._log.info("Marking Order as Paid: %s" % msg)

        # Update order in mongo
        order = self._market.orders.get_order(msg['orderId'])

        # Send to exchange partner
        self._market.orders.pay_order(order)

    def client_ship_order(self, socket_handler, msg):

        self._log.info("Shipping order out: %s" % msg)

        # Update order in mongo
        order = self._market.orders.get_order(msg['orderId'])

        # Send to exchange partner
        self._market.orders.send_order(order)

    def client_generate_secret(self, socket_handler, msg):

      new_secret = self._transport._generate_new_keypair()
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

        self._log.info("[Search] %s"% msg)
        self._transport._dht.iterativeFindValue(msg['key'], callback=self.on_node_search_value)
        #self._log.info('Result: %s' % result)

        #response = self._market.lookup(msg)
        #if response:
        #    self._log.info(response)
            #self.send_to_client(*response)


    def client_query_store_products(self, socket_handler, msg):

        self._log.info("Querying for Store Contracts")

        # Query mongo for products
        self._transport._dht.find_listings(self._transport, msg['key'], callback=self.on_find_products)

    def on_find_products(self, results):

      self._log.info('Found Contracts: %s' % type(results))
      self._log.info(results)

      if len(results):
          data = results['data']
          contracts = data['contracts']
          signature = results['signature']
          self._log.info('Signature: %s' % signature)

          # TODO: Validate signature of listings matches data
          #self._transport._myself.

          # Go get listing metadata and then send it to the GUI
          for contract in contracts:
              self._transport._dht.iterativeFindValue(contract, callback=self.on_node_search_value)

      #self.send_to_client(None, { "type": "store_products", "products": listings } )

    def client_shout(self, socket_handler, msg):
        msg['uri'] = self._transport._uri
        msg['pubkey'] = self._transport.pubkey
        msg['senderGUID'] = self._transport.guid
        self._transport.send(protocol.shout(msg))

    def on_node_search_value(self, results):
        self._log.info('Listing Data: %s' % results)

        # Fix newline issue
        results_data = results.replace('\\n', '\n\r')
        #self._log.info(results_data)

        # Import gpg pubkey
        gpg = gnupg.GPG(gnupghome="gpg")

        # Retrieve JSON from the contract
        # 1) Remove PGP Header
        contract_data = ''.join(results.split('\n')[3:])
        index_of_signature = contract_data.find('-----BEGIN PGP SIGNATURE-----', 0, len(contract_data))
        contract_data_json = contract_data[0:index_of_signature]

        contract_data_json = json.loads(contract_data_json)
        seller_pubkey = contract_data_json.get('Seller').get('seller_PGP')

        gpg.import_keys(seller_pubkey)

        split_results = results.split('\n')
        self._log.debug('DATA: %s' % split_results[3])

        v = gpg.verify(results)
        if v:
            self.send_to_client(None, { "type": "new_listing", "data": contract_data_json })
        else:
            self._log.error('Could not verify signature of contract.')



    def on_node_search_results(self, results):
        if len(results) > 1:
          self.send_to_client(None, {"type": "peers", "peers": self.get_peers()})
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
        if command not in self._handlers:
            return False
        params = request["params"]
        # Create callback handler to write response to the socket.
        handler = self._handlers[command](socket_handler, params)
        return True

    def get_peers(self):
        peers = []

        for peer in self._transport._dht._activePeers:
            peer_item = {'uri': peer._address}
            if peer._pub:
                peer_item['pubkey'] = peer._pub.encode('hex')
            else:
                peer_item['pubkey'] = 'unknown'
            peer_item['guid'] = peer._guid
            peers.append(peer_item)

        return peers

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    # Set of WebsocketHandler
    listeners = set()
    # Protects listeners
    listen_lock = threading.Lock()

    def initialize(self, transport, market):
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info("Initialize websockethandler")
        self._app_handler = ProtocolHandler(transport, market, self)
        self.market = market
        self._transport = transport

    def open(self):
        self._log.info('Websocket open')
        self._app_handler.send_opening()
        with WebSocketHandler.listen_lock:
            self.listeners.add(self)
        self._connected = True

    def on_close(self):
        self._log.info("websocket closed")
        disconnect_msg = {'command': 'disconnect_client', 'id': 0, 'params': []}
        self._connected = False
        self._app_handler.handle_request(self, disconnect_msg)
        with WebSocketHandler.listen_lock:
            self.listeners.remove(self)

    @staticmethod
    def _check_request(request):
        return request.has_key("command") and request.has_key("id") and \
            request.has_key("params") and type(request["params"]) == dict
            #request.has_key("params") and type(request["params"]) == list

    def on_message(self, message):

        #self._log.info('[On Message]: %s' % message)

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
            #self._log.info('Response: %s' % response)

            
            self.write_message(json.dumps(response))
        #try:
        #    self.write_message(json.dumps(response))
        #except tornado.websocket.WebSocketClosedError:
        #    logging.warning("Dropping response to closed socket: %s",
        #       response, exc_info=True)

    def queue_response(self, response):
        ioloop = tornado.ioloop.IOLoop.instance()
        def send_response(*args):
            self._send_response(response)
        try:
            # calling write_message or the socket is not thread safe
            ioloop.add_callback(send_response)
        except:
            logging.error("Error adding callback", exc_info=True)
