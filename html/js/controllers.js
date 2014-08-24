var obControllers = angular.module('obControllers', []);

/**
 * Orders controller.
 *
 * @desc This controller is the orders controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
obControllers
    .controller('Orders', ['$scope', '$interval', '$routeParams', '$location',
        function($scope, $interval, $routeParams, $location) {

            $scope.myOrders = []
            $scope.ordersPanel = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', false);

            /**
             * Open Websocket and then establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            var socket = new Connection(function(msg) {

                var handlers = {
                    'load_page': function(msg) { $scope.load_page(msg) },
                    'order': function(msg) { $scope.parse_order(msg) },
                    'order_count': function(msg) { $scope.parse_order_count(msg) },
                    'myorders': function(msg) { $scope.parse_myorders(msg) },
                    'orderinfo': function(msg) { $scope.parse_orderinfo(msg) },
                }

                if(handlers[msg.type]) {
                    handlers[msg.type](msg);
                }



            })

            $scope.load_page = function(msg) {
                console.log($scope.path)
                if($scope.path === "/orders/sales") {
                    $scope.queryMyOrder(1);
                } else {
                    $scope.queryMyOrder(0);

                }
            }

            $scope.queryMyOrder = function(merchant) {
                // Query for orders
                var query = {
                    'type': 'query_orders',
                    'merchant': merchant
                }
                $scope.merchant = merchant ? 1 : 0
                socket.send('query_orders', query)
                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            }

            /**
             * Parse order message from server for modal
             * @msg - Message from server
             */
            $scope.parse_order = function(msg) {

                if ($scope.myOrders.hasOwnProperty(msg.id)) {
                    console.log("Updating order!")
                    $scope.myOrders[msg.id].state = msg.state
                    $scope.myOrders[msg.id].tx = msg.tx
                    $scope.myOrders[msg.id].notary = msg.notary
                    $scope.myOrders[msg.id].item_price = msg.item_price
                    $scope.myOrders[msg.id].shipping_price = msg.shipping_price
                    //$scope.myOrders[msg.id].total_price = parseFloat(msg.item_price) + parseFloat(msg.shipping_price)
                    $scope.myOrders[msg.id].address = msg.address
                    $scope.myOrders[msg.id].buyer = msg.buyer
                    $scope.myOrders[msg.id].merchant = msg.merchant
                    $scope.myOrders[msg.id].note_for_merchant = msg.note_for_merchant
                    return;
                } else {
                    $scope.myOrders.push(msg);
                }
                if (!$scope.$$phase) {
                    console.log($scope.myOrders);
                    $scope.$apply();
                }
            }

            /**
             * Parse order message from server for modal
             * @msg - Message from server
             */
            $scope.parse_orderinfo = function(msg) {

                console.log("Order info retrieved");
                console.log(msg.order);

                $scope.modalOrder = msg.order;

                if (msg.order.state == 'Accepted') {
                    $scope.modalOrder.waitingForPayment = true;
                } else if (msg.order.state == 'Paid' || msg.order.state == 'Buyer Paid') {
                    console.log('order', msg.order, $scope.myself.guid)
                    if (msg.order.merchant == $scope.myself.guid) {
                        $scope.modalOrder.waitingForShipment = true;
                    } else {
                        $scope.modalOrder.waitingForSellerToShip = true;
                    }
                } else if (msg.order.state == 'Sent') {
                    $scope.modalOrder.flagForArbitration = true;
                } else {
                    $scope.modalOrder.waitingForPayment = false;
                }

                if (msg.order.state == 'Notarized') {
                    $scope.modalOrder.notary = $scope.myself.guid
                }

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            /**
             * Handles orders count message from the server
             * @msg - Message from server
             */
            $scope.parse_order_count = function(msg) {
                console.log(msg)
                $scope.orders_new = msg.count
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

        }
]);

/**
 * User controller.
 *
 * @desc This controller is the user controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
obControllers
    .controller('User', ['$scope', '$interval', '$routeParams', '$location',
        function($scope, $interval, $routeParams, $location) {

            $scope.page_loading = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', true);
            $scope.guid = $routeParams.userId;

            /**
             * Open Websocket and then establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            var socket = new Connection(function(msg) {

                var handlers = {
                    'load_page': function(msg) { $scope.load_page(msg) },
                    'store_contracts': function(msg) { $scope.parse_store_listings(msg) },
                    'store_contract': function(msg) { $scope.parse_store_contract(msg) },
                    'page': function(msg) { $scope.parse_page(msg) },
                    'store_products': function(msg) { $scope.parse_store_products(msg) },
                    'new_listing': function(msg) { $scope.parse_new_listing(msg) }
                }

                if(handlers[msg.type]) {
                    handlers[msg.type](msg);
                }

            })

            $scope.load_page = function(msg) {
                console.log($scope.path)

                switch($scope.path) {

                    case "/user/"+$scope.guid+"/products":
                        $scope.queryShop($scope.guid);
                        $scope.storeProductsPanel = true;
                        $scope.showStorePanel('storeProducts');
                        break;
                    case "/user/"+$scope.guid+"/services":
                        $scope.queryShop($scope.guid);
                        $scope.storeServicesPanel = true;
                        $scope.showStorePanel('storeServices');
                        break;
                    default:
                        $scope.queryShop($scope.guid)
                        $scope.showStorePanel('storeInfo');
                }


            }

            /**
             * Query the network for a merchant and then
             * show the page
             * @guid - GUID of page to load
             */
            $scope.queryShop = function(guid) {

                $scope.awaitingShop = guid;
                console.log('Querying for shop: ', guid);

                var query = {
                    'type': 'query_page',
                    'findGUID': guid
                }

                $scope.page = null
                socket.send('query_page', query)

            }

            $scope.parse_page = function(msg) {

                $scope.page_loading = null
                console.log('Received a page for: ', msg)
                console.log('Waiting for: ' + $scope.awaitingShop)

                if (msg.senderGUID != $scope.awaitingShop)
                    return
                if (!$scope.reviews.hasOwnProperty(msg.pubkey)) {
                    $scope.reviews[msg.pubkey] = []
                }

                console.log($scope.settings);
                $.each($scope.settings.notaries, function(idx, val) {
                    if (val.guid == msg.senderGUID) {
                       msg.isTrustedNotary = true;
                    }
                });

                if (!$scope.dashboard) {
                    $scope.currentReviews = $scope.reviews[msg.pubkey]
                    $scope.page = msg

                    // Write in store content into the HTML
                    var contentDiv = document.getElementById('page-content')
                    contentDiv.innerHTML = msg.text;

                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }
                }
            }

            // A listing has shown up from the network
            $scope.store_listings = [];
            $scope.parse_new_listing = function(msg) {
                console.log(msg.data);
                contract_data = msg.data;
                contract_data.key = msg.key;
                contract_data.rawContract = msg.rawContract;
                contract_data.nickname = msg.nickname;
                $scope.store_listings.push(contract_data)
                $scope.store_listings = jQuery.unique($scope.store_listings);
                $.each($scope.store_listings, function(index, contract) {
                    if (jQuery.isEmptyObject(contract.Contract.item_images)) {
                        console.log('empty object');
                        contract.Contract.item_images = "img/no-photo.png";
                    }
                });
                $('#listing-loader').hide();
                console.log('New Listing', $scope.store_listings)
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.parse_store_contract = function(msg) {

                contract = msg.contract
                console.log(contract)

                $scope.store_listings.push(contract)

                $scope.store_listings = jQuery.unique($scope.store_listings);
                $.each($scope.store_listings, function(index, contract) {
                    if (jQuery.isEmptyObject(contract.contract_body.Contract.item_images)) {
                        contract.contract_body.Contract.item_images = "img/no-photo.png";
                    }
                });


                $('#listing-loader').hide();
                console.log('New Listing', $scope.store_listings)
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.parse_store_listings = function(msg) {

                contracts = msg.products

                $scope.store_listings = []
                $.each(contracts, function(key, value) {
                    console.log('value', value)
                    $scope.store_listings.push(value.contract_body)
                });

                //$scope.store_listings = jQuery.unique($scope.store_listings);
                $.each($scope.store_listings, function(index, contract) {
                    if (jQuery.isEmptyObject(contract.Contract.item_images)) {
                        contract.Contract.item_images = "img/no-photo.png";
                    }
                });


                $('#listing-loader').hide();
                console.log('New Listing', $scope.store_listings)
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.store_products = {};
            $scope.parse_store_products = function(msg) {

                console.log(msg)
                $scope.store_products = msg.products;


                if (!$scope.$$phase) {
                    $scope.$apply();
                }
                // $scope.store_products.forEach(function(product) {
                //   console.log(product);
                //
                // })

            }
            $scope.parse_listing_results = function(msg) {
                $scope.store_products = msg.contracts;
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            function resetStorePanels() {
                $scope.storeInfoPanel = false;
                $scope.storeProductsPanel = false;
                $scope.storeReviewsPanel = false;
                $scope.storeOrderHistoryPanel = false;
                $scope.storeServicesPanel = false;
            }

            $scope.showStorePanel = function(panelName) {

                resetStorePanels();
                $scope.dashboard = false;

                switch (panelName) {
                    case 'storeInfo':
                        $scope.storeInfoPanel = true;
                        break;
                    case 'storeProducts':
                        $('#listing-loader').show();
                        $scope.store_listings = [];
                        $scope.queryStoreProducts($scope.guid);
                        $scope.getNotaries();
                        break;
                    case 'storeOrders':
                        //$scope.storeOrdersPanel = true;
                        break;
                    case 'storeReviews':
                        $scope.storeReviewsPanel = true;
                        break;
                    case 'storeServices':
                        $scope.storeServicesPanel = true;
                        break;

                }
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            // Query for product listings from this store
            $scope.queryStoreProducts = function(storeID) {

                console.log('Querying for contracts in store: ' + storeID);
                $scope.storeProductsPanel = true;
                var query = {
                    'type': 'query_store_products',
                    'key': storeID
                }
                socket.send('query_store_products', query);

            }

            $scope.addNotary = function(guid, nickname) {

                //if(notaryGUID.length != 40 || !notaryGUID.match(/^[0-9a-z]+$/)) {
                //    alert('Incorrect format for GUID');
                //    return;
                //}
                $scope.page.isTrustedNotary = true

                socket.send('add_trusted_notary', { 'type': 'add_trusted_notary',
                    'guid': guid,
                    'nickname': nickname
                    }
                );


            }

        }
]);

/**
 * Contracts controller.
 *
 * @desc This controller is the contracts controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
obControllers
    .controller('Contracts', ['$scope', '$interval', '$routeParams', '$location',
        function($scope, $interval, $routeParams, $location) {

            $scope.contractsPanel = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', false);


            /**
             * Open Websocket and then establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            var socket = new Connection(function(msg) {

                var handlers = {
                    'load_page': function(msg) { $scope.load_page(msg) },
                    'contracts': function(msg) { $scope.parse_contracts(msg) }
                }

                if(handlers[msg.type]) {
                    handlers[msg.type](msg);
                }

            })

            $scope.load_page = function(msg) {
                console.log($scope.path)
                    console.log('test')
                    $scope.sidebar = false;
                    $scope.queryContracts();

            }

            $scope.queryContracts = function() {
                var query = { 'type': 'query_contracts' }
                socket.send('query_contracts', query)
            }

            $scope.removeContract = function(contract_id) {
                socket.send("remove_contract", {
                    "contract_id": contract_id
                });
                socket.send("query_contracts", {})
            }

            $scope.republishContracts = function() {
                socket.send("republish_contracts", {});
                socket.send("query_contracts", {})
            }

            $scope.ProductModal = function($scope, $modal, $log) {

                $scope.contracts_page_changed = function() {
                    console.log($scope.contracts_current_page)
                    var query = {
                        'page': $scope.contracts_current_page - 1
                    }
                    console.log(query)
                    socket.send('query_contracts', query)

                }

                $scope.open = function(size, backdrop) {

                    backdrop = backdrop ? backdrop : true;

                    var modalInstance = $modal.open({
                        templateUrl: 'addContract.html',
                        controller: ProductModalInstance,
                        size: size,
                        backdrop: backdrop,
                        resolve: {
                            contract: function() {
                                return {
                                    "contract": $scope.contract
                                };
                            }
                        }
                    });

                    modalInstance.result.then(function(selectedItem) {
                        $scope.selected = selectedItem;
                    }, function() {
                        $log.info('Product modal dismissed at: ' + new Date());
                    });

                }


            };

            var ProductModalInstance = function($scope, $modalInstance, contract) {

                $scope.contract = contract;
                $scope.contract.productQuantity = 1;
                $scope.contract.productCondition = 'New';
                $scope.contracts_current_page = 0;

                $scope.createContract = function() {

                    console.log($scope.contract);

                    if (contract.contract) {

                        // Imported JSON format contract
                        jsonContract = $scope.contract.rawText;
                        console.log(jsonContract);

                        socket.send("import_raw_contract", {
                            'contract': jsonContract
                        });

                    } else {

                        contract = {};
                        contract.Contract_Metadata = {
                            "OBCv": "0.1-alpha",
                            "category": "physical_goods",
                            "subcategory": "fixed_price",
                            "contract_nonce": "01",
                            "expiration": "2014-01-01 00:00:00"
                        }
                        contract.Seller = {
                            "seller_GUID": "",
                            "seller_BTC_uncompressed_pubkey": "",
                            "seller_PGP": ""
                        }
                        contract.Contract = {
                            "item_title": $scope.contract.productTitle,
                            "item_keywords": [],
                            "currency": "XBT",
                            "item_price": $scope.contract.productPrice,
                            "item_condition": $scope.contract.productCondition,
                            "item_quantity": $scope.contract.productQuantity,
                            "item_desc": $scope.contract.productDescription,
                            "item_images": {},
                            "item_delivery": {
                                "countries": "",
                                "region": "",
                                "est_delivery": "",
                                "shipping_price": $scope.contract.productShippingPrice
                            }
                        }

                        keywords = ($scope.contract.productKeywords) ? $scope.contract.productKeywords.split(',') : []
                        $.each(keywords, function(i, el) {
                            if ($.inArray(el.trim(), contract.Contract.item_keywords) === -1 && el.trim() != '') contract.Contract.item_keywords.push(el.trim());
                        });

                        var imgUpload = document.getElementById('inputProductImage').files[0];

                        if (imgUpload) {

                            if (imgUpload.type != '' && $.inArray(imgUpload.type, ['image/jpeg', 'image/gif', 'image/png']) != -1) {

                                var r = new FileReader();
                                r.onloadend = function(e) {
                                    var data = e.target.result;

                                    contract.Contract.item_images.image1 = imgUpload.result;

                                    console.log(contract);
                                    socket.send("create_contract", contract);
                                    Notifier.success('Success', 'Contract saved successfully.');
                                    socket.send("query_contracts", {})


                                }
                                r.readAsArrayBuffer(imgUpload);


                            } else {

                                console.log(contract);
                                socket.send("create_contract", contract);
                                Notifier.success('Success', 'Contract saved successfully.');
                                socket.send("query_contracts", {})


                            }

                        } else {
                            console.log(contract);
                            socket.send("create_contract", contract);

                            socket.send("query_contracts", {})

                        }
                    }
                    $modalInstance.dismiss('cancel');
                }

                $scope.cancel = function() {
                    socket.send("query_contracts", {});
                    $modalInstance.dismiss('cancel');
                };

                $scope.toggleItemAdvanced = function() {
                    $scope.itemAdvancedDetails = ($scope.itemAdvancedDetails) ? 0 : 1;
                }
            };


        }
]);

/**
 * Search controller.
 *
 * @desc This controller is the search controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
obControllers
    .controller('Search', ['$scope', '$interval', '$routeParams', '$location',
        function($scope, $interval, $routeParams, $location) {

            $scope.searchPanel = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', false);

            /**
             * Open Websocket and then establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            var socket = new Connection(function(msg) {

                var handlers = {
                    'load_page': function(msg) { $scope.load_page(msg) }
                }

                if(handlers[msg.type]) {
                    handlers[msg.type](msg);
                }

            })

            $scope.load_page = function(msg) {
                console.log($scope.path)
                $('#dashboard-container').removeClass('col-sm-8').addClass('col-sm-12')

            }

            $scope.search = ""
            $scope.searchNetwork = function() {
                var query = {
                    'type': 'search',
                    'key': $scope.search
                };
                $scope.searching = $scope.search;
                $scope.search_results = [];
                $scope.awaitingShop = $scope.search;
                socket.send('search', query)
                $scope.search = ""
                $scope.showDashboardPanel('search');
            }
    }
]);

/**
 * Settings controller.
 *
 * @desc This controller is the settings controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
obControllers
    .controller('Settings', ['$scope', '$interval', '$routeParams', '$location',
        function($scope, $interval, $routeParams, $location) {

            $scope.settingsPanel = true;
            $scope.path = $location.path();
            $('#keys-form').siblings().hide();
            $scope.$emit('sidebar', false);



            /**
             * Open Websocket and then establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            var socket = new Connection(function(msg) {

                var handlers = {
                    'load_page': function(msg) { $scope.load_page(msg) },
                    'settings_notaries': function(msg) { $scope.parse_notaries(msg) }
                }

                if(handlers[msg.type]) {
                    handlers[msg.type](msg);
                }

            })

            $scope.load_page = function(msg) {
                console.log($scope.path)
                $('#dashboard-container').removeClass('col-sm-8').addClass('col-sm-12')

                switch($scope.path) {

                    case "/settings/keys":
                        $('#keys-form').show();
                        $('#keys-form').siblings().hide();
                        $('#settings-keys').addClass('active');
                        break;
                    case "/settings/communication":
                        $('#communication-form').show();
                        $('#communication-form').siblings().hide();
                        $('#settings-communication').addClass('active');
                        break;
                    case "/settings/arbiter":
                        $('#arbiter-form').show();
                        $('#arbiter-form').siblings().hide();
                        $('#settings-arbiter').addClass('active');
                        break;
                    case "/settings/notary":
                        $('#notary-form').show();
                        $('#notary-form').siblings().hide();
                        $('#settings-notary').addClass('active');
                        $scope.getNotaries()
                        break;
                    case "/settings/advanced":
                        $('#advanced-form').show();
                        $('#advanced-form').siblings().hide();
                        $('#settings-advanced').addClass('active');
                        break;
                    default:
                        $('#profile-form').show();
                        $('#profile-form').siblings().hide();
                        $('#settings-storeinfo').addClass('active');
                        break;
                }

            }


            $scope.addNotary = function(notary) {

                notaryGUID = (notary != '') ? notary : $scope.newNotary;
                $scope.newNotary = '';

                if(notaryGUID.length != 40 || !notaryGUID.match(/^[0-9a-z]+$/)) {
                    alert('Incorrect format for GUID');
                    return;
                }

                socket.send('add_trusted_notary', { 'type': 'add_trusted_notary',
                    'guid': notaryGUID,
                    'nickname': ''
                    }
                );

                Notifier.success('Success', 'Notary added successfully.');
                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            }

            $scope.removeNotary = function(notaryGUID) {

                $('#notary_'+notaryGUID).parent().hide();
                socket.send('remove_trusted_notary', { 'type': 'remove_trusted_notary',
                    'guid': notaryGUID
                    }
                );

                Notifier.success('Success', 'Notary removed successfully.');

                $scope.getNotaries();

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.getNotaries = function() {
                console.log('Getting notaries');
                socket.send('get_notaries', {});
            }

            $scope.generateNewSecret = function() {

                var query = {
                    'type': 'generate_secret'
                }
                console.log('Generating new secret key')
                socket.send('generate_secret', query)
                console.log($scope.myself.settings)

            }

            /**
             * Load notaries array into the GUI
             * @msg - Message from server
             */
            $scope.parse_notaries = function(msg) {
                $scope.trusted_notaries = msg.notaries
                console.log(msg.notaries)
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

        }
]);

/**
 * Market controller.
 *
 * @desc This controller is the main controller for the market.
 * It contains all of the single page application logic.
 * @param {!angular.Scope} $scope
 * @constructor
 */
obControllers
    .controller('Market', ['$scope', '$interval', '$routeParams', '$location',
        function($scope, $interval, $routeParams, $location) {

            $scope.newuser = true                   // Should show welcome screen?
            $scope.page = false                     // Market page has been loaded
            $scope.dashboard = true                 // Show dashboard
            $scope.myInfoPanel = true               // Show information panel
            $scope.shouts = [];                     // Shout messages
            $scope.newShout = ""
            $scope.searching = ""
            $scope.currentReviews = []
            $scope.myOrders = []
            $scope.myReviews = []

            $scope.peers = [];
            $scope.reviews = {};
            $scope.awaitingShop = null;
            $scope.page_loading = null;

            $scope.$emit('sidebar', true);

            /**
             * Open Websocket and then establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            var socket = new Connection(function(msg) {

                var handlers = {
                    'peer': function(msg) { $scope.add_peer(msg) },
                    'peers': function(msg) { $scope.update_peers(msg) },
                    'peer_remove': function(msg) { $scope.remove_peer(msg) },
                    'myself': function(msg) { $scope.parse_myself(msg) },
                    'shout': function(msg) { $scope.parse_shout(msg) },
                    'log_output': function(msg) { $scope.parse_log_output(msg) },
                    'messages': function(msg) { $scope.parse_messages(msg) },
                    'notaries': function(msg) { $scope.parse_notaries(msg) },
                    'global_search_result': function(msg) { $scope.parse_search_result(msg) },
                    'reputation': function(msg) { $scope.parse_reputation(msg) },
                    'proto_response_pubkey': function(msg) { $scope.parse_response_pubkey(msg) },
                }

                if(handlers[msg.type]) {
                    handlers[msg.type](msg);
                }



            })

            // Listen for Sidebar mods
            $scope.$on('sidebar', function(event, visible) {
                console.log(visible);
                $scope.sidebar = visible
            });

            refresh_peers = function() {
                socket.send('peers', {})
            }

            //$interval(refresh_peers,60000,0,true)

            /**
             * Create a shout and send it to all connected peers
             * Display it in the interface
             */
            $scope.createShout = function() {
                // launch a shout
                console.log($scope)
                var newShout = {
                    'type': 'shout',
                    'text': $scope.newShout,
                    'pubkey': $scope.myself.pubkey,
                    'senderGUID': $scope.myself.guid
                }
                socket.send('shout', newShout)
                $scope.shouts.push(newShout)
                $scope.newShout = '';
            }

            // Toggle the sidebar hidden/shown
            $scope.toggleSidebar = function() {
                $scope.sidebar = ($scope.sidebar) ? false : true;
            }

            // Hide the sidebar
            $scope.hideSidebar = function() {
                $scope.sidebar = false;
            }

            // Show the sidebar
            $scope.showSidebar = function() {
                $scope.sidebar = true;
            }




            /**
             * [LEGACY] Adds review to a page
             * @pubkey -
             * @review -
             */
            var add_review_to_page = function(pubkey, review) {
                var found = false;

                console.log("Add review");

                if (!$scope.reviews.hasOwnProperty(pubkey)) {
                    $scope.reviews[pubkey] = []
                }
                $scope.reviews[pubkey].forEach(function(_review) {
                    if (_review.sig == review.sig && _review.subject == review.subject && _review.pubkey == review.pubkey) {
                        console.log("Found a review for this market")
                        found = true
                    }
                });
                if (!found) {
                    // check if the review is about me
                    if ($scope.myself.pubkey == review.subject) {
                        console.log("Found review for myself")
                        $scope.myReviews.push(review)
                    }
                    $scope.reviews[pubkey].push(review)
                }
                $scope.$apply();
                console.log($scope.reviews);
            }



            /**
             * Send log line to GUI
             * @msg - Message from server
             */
            $scope.parse_log_output = function(msg) {
                console.log(msg)
                $scope.log_output += msg.line

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            }

            /**
             * Load notaries array into the GUI
             * @msg - Message from server
             */
            $scope.parse_notaries = function(msg) {
                $scope.trusted_notaries = msg.notaries
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }



            $scope.parse_welcome = function(msg) {

                console.log(msg)

            }

            $scope.getNumber = function(num) {
                return new Array(num);
            }

            $scope.orders_page_changed = function() {
                console.log($scope.orders_current_page)
                var query = {
                    'page': $scope.orders_current_page - 1,
                    'merchant': $scope.merchant
                }
                socket.send('query_orders', query)

            }

            $scope.parse_myorders = function(msg) {

                $scope.orders = msg['orders'];
                $scope.orders_total = msg['total'];
                $scope.orders_pages = msg['total'] % 10
                $scope.orders_current_page = msg['page'] + 1

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            }


            $scope.parse_contracts = function(msg) {

                console.log(msg);

                page = msg['page'];

                $scope.contracts = msg.contracts.contracts;

                $scope.total_contracts = msg.contracts.total_contracts;
                $scope.contracts_pages = $scope.total_contracts % 10
                console.log('contracts', $scope.total_contracts);
                $scope.contracts_current_page = (page > 0) ? page - 1 : 0;
                console.log($scope)

                for (var key in msg.contracts.contracts) {

                    var obj = msg.contracts.contracts[key];
                    for (var prop in obj) {
                        if (prop == 'item_images' && jQuery.isEmptyObject(msg.contracts.contracts[key].item_images)) {
                            msg.contracts.contracts[key].item_images = "img/no-photo.png";
                        }

                    }

                }

                $scope.contract2 = {};
                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            }

            $scope.message = {};
            $scope.parse_messages = function(msg) {
                if (msg != null &&
                    msg.messages != null &&
                    msg.messages.messages != null &&
                    msg.messages.messages.inboxMessages != null) {

                    $scope.messages = msg.messages.messages.inboxMessages;

                    $scope.message = {};
                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }
                }
            }

            $scope.parse_response_pubkey = function(msg) {
                var pubkey = msg.pubkey;
                var nickname = msg.nickname;
                $scope.peers.forEach(function(peer) {
                    if (peer.pubkey == pubkey) {
                        // this peer!!
                        peer.nickname = msg.nickname;
                        if ($scope.searching == msg.nickname) {
                            $scope.queryShop(peer)
                        }
                    }
                });
                if (!$scope.$$phase) {

                    $scope.$apply();
                }
            }

            // Peer information has arrived
            $scope.parse_reputation = function(msg) {

                console.log('Parsing reputation', msg.reviews)
                msg.reviews.forEach(function(review) {
                    add_review_to_page(review.subject, review);
                });
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.add_peer = function(msg) {

                console.log('Add peer: ', msg);

                /* get index if peer is already known */
                var index = [-1].concat($scope.peers).reduce(
                    function(previousValue, currentValue, index, array) {
                        return currentValue.uri == msg.uri ? index : previousValue;
                    });

                if (index == -1) {
                    /* it is a new peer */
                    $scope.peers.push(msg);
                } else {
                    $scope.peers[index] = msg;
                }
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.update_peers = function(msg) {

                console.log('Refresh peers: ', msg);

                $scope.peers = msg.peers;

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.remove_peer = function(msg) {

                console.log('Remove peer: ', msg);

                $scope.peers = $scope.peers.filter(function(element) {
                    return element.uri != msg.uri;
                });

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.review = {
                rating: 5,
                text: ""
            }
            $scope.addReview = function() {

                var query = {
                    'type': 'review',
                    'pubkey': $scope.page.pubkey,
                    'text': $scope.review.text,
                    'rating': parseInt($scope.review.rating)
                }
                socket.send('review', query)

                // store in appropriate format (its different than push format :P)
                add_review_to_page($scope.page.pubkey, {
                    type: 'review',
                    'pubkey': $scope.myself.pubkey,
                    'subject': $scope.page.pubkey,
                    'rating': query.rating,
                    text: query.text
                })

                $scope.review.rating = 5;
                $scope.review.text = '';
                $scope.showReviewForm = false;
            }

            // My information has arrived
            $scope.parse_myself = function(msg) {


                $scope.myself = msg;

                if (!$scope.$$phase) {
                    $scope.$apply();
                }


                // Settings
                $scope.settings = msg.settings
                console.log(msg.settings)

                //msg.reputation.forEach(function(review) {
                //   add_review_to_page($scope.myself.pubkey, review)
                //});

                msg.peers.forEach(function(peer) {
                    $scope.add_peer(peer)
                });


            }

            // A shout has arrived
            $scope.parse_shout = function(msg) {
                $scope.shouts.push(msg)
                console.log('Shout', $scope.shouts)
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }




            $scope.search_results = [];
            $scope.parse_search_result = function(msg) {
                console.log(msg);
                contract_data = msg.data;
                contract_data.key = msg.key;
                contract_data.rawContract = msg.rawContract;
                contract_data.nickname = msg.nickname;
                $scope.search_results.push(contract_data)
                $scope.search_results = jQuery.unique($scope.search_results);
                $.each($scope.search_results, function(index, contract) {
                    if (jQuery.isEmptyObject(contract.Contract.item_images)) {
                        console.log('empty object');
                        contract.Contract.item_images = "img/no-photo.png";
                    }
                });

                console.log('Search Results', $scope.search_results)

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }

            $scope.checkOrderCount = function() {
                socket.send('check_order_count', {});
            }



            $scope.settings = {
                email: '',
                PGPPubKey: '',
                bitmessage: '',
                pubkey: '',
                secret: '',
                nickname: '',
                welcome: '',
                trustedArbiters: {},
                trustedNotaries: {}
            }

            $scope.saveSettings = function(notify) {
                console.log($scope.settings)
                var query = {
                    'type': 'update_settings',
                    settings: $scope.settings
                }
                socket.send('update_settings', query);
                if (typeof notify === "undefined") {
                    Notifier.success('Success', 'Settings saved successfully.');
                }
            }


            // Create a new order and send to the network
            $scope.newOrder = {
                message: '',
                tx: '',
                listingKey: '',
                productTotal: ''
            }
            $scope.createOrder = function() {

                $scope.creatingOrder = false;

                var newOrder = {
                    'text': $scope.newOrder.message,
                    'state': 'new',
                    'buyer': $scope.myself.pubkey,
                    'seller': $scope.page.pubkey,
                    'listingKey': $scope.newOrder.pubkey
                }

                socket.send('order', newOrder);
                $scope.sentOrder = true;

                $scope.showDashboardPanel('orders');

                $('#pill-orders').addClass('active').siblings().removeClass('active').blur();
                $("#orderSuccessAlert").alert();
                window.setTimeout(function() {
                    $("#orderSuccessAlert").alert('close')
                }, 5000);

            }
            $scope.payOrder = function(order) {
                order.state = 'paid'
                order.tx = $scope.newOrder.tx;
                $scope.newOrder.tx = '';
                socket.send('order', order);
            }
            $scope.receiveOrder = function(order) {
                order.state = 'received'
                socket.send('order', order);
            }
            $scope.sendOrder = function(order) {
                order.state = 'Sent'
                socket.send('order', order);

                scope.queryMyOrder(0);

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            }

            $scope.cancelOrder = function(order) {
                order.state = 'cancelled'
                socket.send('order', order)
            }

            $scope.addArbiter = function(arbiter) {
                arbiterGUID = (arbiter != '') ? arbiter : $('#inputArbiterGUID').val();
                $('#inputArbiterGUID').val('');

                // TODO: Check for valid arbiter GUID
                //if(arbiterGUID.length != 38 || !arbiterGUID.match(/^[0-9a-zA-Z]+$/)) {
                //    alert('Incorrect format for GUID');
                //    return;
                //}

                if (!$scope.settings.trustedArbiters) {
                    $scope.settings.trustedArbiters = [];
                }
                $scope.settings.trustedArbiters.push(arbiterGUID);

                // Dedupe arbiter GUIDs
                var uniqueArbiters = [];
                $.each($scope.settings.trustedArbiters, function(i, el) {
                    if ($.inArray(el, uniqueArbiters) === -1) uniqueArbiters.push(el);
                });

                $scope.settings.trustedArbiters = uniqueArbiters;

                $scope.saveSettings(false);
                Notifier.success('Success', 'Arbiter added successfully.');
            }

            $scope.removeArbiter = function(arbiterGUID) {

                // Dedupe arbiter GUIDs
                var uniqueArbiters = $scope.settings.trustedArbiters;
                $.each($scope.settings.trustedArbiters, function(i, el) {
                    if (el == arbiterGUID) uniqueArbiters.splice(i, 1);
                });

                $scope.settings.trustedArbiters = uniqueArbiters;

                $scope.saveSettings(false);
                Notifier.success('Success', 'Arbiter removed successfully.');
            }

            $scope.compose_message = function(size, myself, address, subject) {
                $scope.$broadcast("compose_message", {
                    size: size,
                    myself: myself,
                    bm_address: address,
                    subject: subject
                });
            };

            $scope.clearDHTData = function() {
                socket.send('clear_dht_data', {});
                Notifier.success('Success', 'DHT cache cleared');
            }

            $scope.clearPeers = function() {
                socket.send('clear_peers_data', {});
                Notifier.success('Success', 'Peers table cleared');
            }



            function resetPanels() {
                $scope.messagesPanel = false;
                $scope.reviewsPanel = false;
                $scope.productCatalogPanel = false;
                $scope.settingsPanel = false;
                $scope.arbitrationPanel = false;
                $scope.ordersPanel = false;
                $scope.myInfoPanel = false;
                $scope.searchPanel = false;
            }

            $scope.showDashboardPanel = function(panelName) {

                resetPanels();

                if (panelName != 'myInfo') {
                    $scope.hideSidebar();
                    $('#dashboard-container').removeClass('col-sm-8').addClass('col-sm-12')
                } else {
                    $scope.showSidebar();
                    $('#dashboard-container').removeClass('col-sm-12').addClass('col-sm-8')
                }

                $scope.dashboard = true;
                $scope.page = false;

                switch (panelName) {
                    case 'messages':
                        $scope.queryMessages();
                        $scope.messagesPanel = true;
                        break;
                    case 'reviews':
                        $scope.reviewsPanel = true;
                        break;

                    case 'arbitration':
                        $scope.arbitrationPanel = true;
                        break;


                    case 'myInfo':
                        $scope.myInfoPanel = true;
                        break;

                }
            }




            $scope.getNotaries = function() {
                console.log('Getting notaries');
                socket.send('get_notaries', {});
            }


            $scope.go = function (url) {
              $location.path(url);
            }






            $scope.queryMessages = function() {
                // Query for messages
                var query = {
                    'type': 'query_messages'
                }
                console.log('querying messages')
                socket.send('query_messages', query)
                console.log($scope.myself.messages)

            }







            // Modal Code
            $scope.WelcomeModalCtrl = function($scope, $modal, $log, $rootScope) {

                // Listen for changes to settings and if welcome is empty then show the welcome modal
                $scope.$watch('settings', function () {
                    console.log('settings',$scope.settings)
                    if ($scope.settings.welcome == "enable") {
                        $scope.open('lg','static');
                    } else {
                        return;
                    }

                    /*Else process your data*/
                });

                $scope.open = function(size, backdrop, scope) {

                    backdrop = backdrop ? backdrop : true;

                    var modalInstance = $modal.open({
                        templateUrl: 'myModalContent.html',
                        controller: ModalInstanceCtrl,
                        size: size,
                        backdrop: backdrop,
                        resolve: {
                            settings: function() {
                                return $scope.settings;
                            }
                        }
                    });

                    modalInstance.result.then(function(selectedItem) {
                        $scope.selected = selectedItem;
                    }, function() {
                        $log.info('Modal dismissed at: ' + new Date());
                    });

                }

            };

            // Please note that $modalInstance represents a modal window (instance) dependency.
            // It is not the same as the $modal service used above.

            var ModalInstanceCtrl = function($scope, $modalInstance, settings) {

                $scope.settings = settings;
                // $scope.selected = {
                //   item: $scope.items[0]
                // };
                //

                $scope.welcome = settings.welcome;

                $scope.ok = function() {
                    socket.send('welcome_dismissed', {});
                    $modalInstance.dismiss('cancel');
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            };

            $scope.ViewOrderCtrl = function($scope, $modal, $log) {



                $scope.open = function(size, orderId, settings) {

                    // Send socket a request for order info
                    socket.send('query_order', {
                        orderId: orderId
                    })

                    var modalInstance = $modal.open({
                        templateUrl: 'viewOrder.html',
                        controller: ViewOrderInstanceCtrl,
                        size: size,
                        resolve: {
                            orderId: function() {
                                return orderId;
                            },
                            settings: function() {
                                return settings;
                            },
                            scope: function() {
                                return $scope
                            }
                        }
                    });

                    modalInstance.result.then(function() {

                    }, function() {
                        $log.info('Modal dismissed at: ' + new Date());
                    });
                };
            };


            var ViewOrderInstanceCtrl = function($scope, $modalInstance, orderId, scope, settings) {


                $scope.orderId = orderId;
                $scope.Market = scope;
                $scope.settings = settings;

                $scope.markOrderPaid = function(orderId) {

                    socket.send("pay_order", {
                        orderId: orderId
                    })

                    scope.modalOrder.state = 'Paid';

                    // Refresh orders in background
                    scope.queryMyOrder(0);

                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }

                }


                $scope.markOrderShipped = function(orderId) {

                    socket.send("ship_order", {
                        orderId: orderId,
                        paymentAddress: scope.modalOrder.paymentAddress
                    })

                    scope.modalOrder.state = 'Shipped';
                    scope.modalOrder.waitingForShipment = false;
                    scope.queryMyOrder(1);

                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }

                }

                $scope.markOrderReceived = function(orderId) {

                    socket.send("release_payment", {
                        orderId: orderId
                    })

                    scope.modalOrder.state = 'Completed';
                    scope.queryMyOrder(0);

                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }

                }

                $scope.ok = function() {
                    $modalInstance.close();
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            };





            $scope.BuyItemCtrl = function($scope, $modal, $log) {

                $scope.open = function(size, myself, merchantPubkey, productTitle, productPrice, productDescription, productImageData, key, rawContract,
                    notaries, arbiters, btc_pubkey, guid) {

                    // Send socket a request for order info
                    //socket.send('query_order', { orderId: orderId } )




                    modalInstance = $modal.open({
                        templateUrl: 'buyItem.html',
                        controller: $scope.BuyItemInstanceCtrl,
                        resolve: {
                            merchantPubkey: function() {
                                return merchantPubkey
                            },
                            myself: function() {
                                return myself
                            },
                            productTitle: function() {
                                return productTitle
                            },
                            productPrice: function() {
                                return productPrice
                            },
                            productDescription: function() {
                                return productDescription
                            },
                            productImageData: function() {
                                return productImageData
                            },
                            key: function() {
                                return key
                            },
                            btc_pubkey: function() {
                                return btc_pubkey
                            },
                            rawContract: function() {
                                return rawContract
                            },
                            notaries: function() {
                                return notaries
                            },
                            arbiters: function() {
                                return arbiters
                            },
                            guid: function() {
                                return guid
                            },
                            scope: function() {
                                return $scope
                            }
                        },
                        size: size
                    });

                    modalInstance.result.then(function() {

                        $scope.showDashboardPanel('orders_purchases');

                        $('#pill-orders').addClass('active').siblings().removeClass('active').blur();
                        $("#orderSuccessAlert").alert();
                        window.setTimeout(function() {
                            $("#orderSuccessAlert").alert('close')
                        }, 5000);

                    }, function() {
                        $log.info('Modal dismissed at: ' + new Date());

                    });
                };
            };


            $scope.BuyItemInstanceCtrl = function($scope, $modalInstance, myself, merchantPubkey, productTitle, productPrice, productDescription, productImageData, key,
                rawContract,
                notaries,
                arbiters,
                btc_pubkey,
                guid,
                scope) {


                console.log(productTitle, productPrice, productDescription, productImageData, rawContract, notaries, arbiters, btc_pubkey, guid);
                $scope.myself = myself;
                $scope.merchantPubkey = merchantPubkey;
                $scope.productTitle = productTitle;
                $scope.productPrice = productPrice;
                $scope.productDescription = productDescription;
                $scope.productImageData = productImageData;
                $scope.totalPrice = productPrice;
                $scope.productQuantity = 1;
                $scope.rawContract = rawContract;
                $scope.guid = guid;
                $scope.arbiters = arbiters;
                $scope.notaries = []

                jQuery.each(notaries, function(key, value) {
                    notary = value
                    console.log(value.guid + ' ' + guid)
                    if (value.guid != guid) {
                        $scope.notaries.push({
                            "guid": value.guid,
                            "nickname": value.nickname
                        })
                    }
                })
                console.log($scope.notaries)

                $scope.key = key;

                $scope.update = function(user) {
                    console.log('Updated');
                };


                $scope.ok = function() {
                    $modalInstance.close();
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };

                $scope.updateTotal = function() {
                    var newPrice = $('#itemQuantity').val() * $scope.productPrice;
                    newPrice = Math.round(newPrice * 100000) / 100000
                    $('#totalPrice').html(newPrice);
                }

                $scope.gotoStep2 = function() {
                    $scope.order.step2 = 1;
                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }
                }

                $scope.gotoStep1 = function() {
                    $scope.order.step2 = '';
                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }
                }

                $scope.order = {
                    message: '',
                    tx: '',
                    listingKey: key,
                    listingTotal: '',
                    productTotal: '',
                    productQuantity: 1,
                    rawContract: rawContract,
                    btc_pubkey: btc_pubkey
                }
                $scope.order.notary = ($scope.notaries.length > 0) ? $scope.notaries[0].guid : "";
                $scope.order.arbiter = $scope.arbiters[0];

                $scope.submitOrder = function() {

                    $scope.creatingOrder = false;
                    $scope.order.step2 = '';
                    $scope.order.step1 = '';
                    $scope.order.confirmation = true;

                    var newOrder = {
                        'message': $scope.order.message,
                        'state': 'new',
                        'buyer': $scope.myself.pubkey,
                        'seller': $scope.merchantPubkey,
                        'listingKey': $scope.key,
                        'orderTotal': $('#totalPrice').html(),
                        'rawContract': rawContract,
                        'notary': $scope.order.notary,
                        'btc_pubkey': $scope.order.btc_pubkey,
                        'arbiter': $scope.order.arbiter
                    }
                    console.log(newOrder);
                    socket.send('order', newOrder);
                    $scope.sentOrder = true;
                    scope.queryMyOrder(0);

                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }



                }

                $scope.closeConfirmation = function() {
                    $modalInstance.close();
                }



            };


            $scope.ComposeMessageCtrl = function($scope, $modal, $log) {


                $scope.$on("compose_message", function(event, args) {
                    $scope.bm_address = args.bm_address;
                    $scope.size = args.size;
                    $scope.subject = args.subject;
                    $scope.myself = args.myself;

                    $scope.compose($scope.size, $scope.myself, $scope.bm_address, $scope.subject);
                });


                $scope.compose = function(size, myself, to_address, msg) {

                    composeModal = $modal.open({
                        templateUrl: 'composeMessage.html',
                        controller: $scope.ComposeMessageInstanceCtrl,
                        resolve: {
                            myself: function() {
                                return myself
                            },
                            to_address: function() {
                                return to_address
                            },
                            msg: function() {
                                return msg
                            },
                        },
                        size: size
                    });
                    afterFunc = function() {
                        $scope.showDashboardPanel('messages');
                    };
                    composeModal.result.then(afterFunc,
                        function() {
                            $log.info('Modal dismissed at: ' + new Date());
                        });
                };

                $scope.view = function(size, myself, my_address, msg) {
                    console.log(msg)
                    viewModal = $modal.open({
                        templateUrl: 'viewMessage.html',
                        controller: $scope.ViewMessageInstanceCtrl,
                        resolve: {
                            myself: function() {
                                return myself
                            },
                            my_address: function() {
                                return my_address
                            },
                            msg: function() {
                                return msg
                            },
                        },
                        size: size
                    });
                    afterFunc = function() {
                        $scope.showDashboardPanel('messages');
                    };
                    viewModal.result.then(afterFunc,
                        function() {
                            $log.info('Modal dismissed at: ' + new Date());
                        });
                };
            };

            $scope.ViewMessageInstanceCtrl = function($scope, $modalInstance, myself, my_address, msg) {
                $scope.myself = myself;
                $scope.my_address = my_address;
                $scope.msg = msg;

                // Fill in form if msg is passed - reply mode
                if (msg != null) {
                    $scope.toAddress = msg.fromAddress;
                    // Make sure subject start with RE:
                    var sj = msg.subject;
                    if (sj.match(/^RE:/) == null) {
                        sj = "RE: " + sj;
                    }
                    $scope.subject = sj;
                    // Quote message
                    quote_re = /^(.*?)/mg;
                    var quote_msg = msg.message.replace(quote_re, "> $1");
                    $scope.body = "\n" + quote_msg;
                }

                $scope.send = function() {
                    // Trigger validation flag.
                    $scope.submitted = true;

                    // If form is invalid, return and let AngularJS show validation errors.
                    if (composeForm.$invalid) {
                        return;
                    }

                    var query = {
                        'type': 'send_message',
                        'to': toAddress.value,
                        'subject': subject.value,
                        'body': body.value
                    }
                    console.log('sending message with subject ' + subject)
                    socket.send('send_message', query)

                    $modalInstance.close();
                };

                $scope.close = function() {
                    $modalInstance.dismiss('cancel');
                };
            };

            $scope.ComposeMessageInstanceCtrl = function($scope, $modalInstance, myself, to_address, msg) {

                $scope.myself = myself;
                $scope.to_address = to_address;
                $scope.msg = msg;

                // Fill in form if msg is passed - reply mode
                if (msg != null) {
                    $scope.toAddress = msg.fromAddress;
                    // Make sure subject start with RE:
                    var sj = msg.subject;
                    if (sj.match(/^RE:/) == null) {
                        sj = "RE: " + sj;
                    }
                    $scope.subject = sj;
                    // Quote message
                    quote_re = /^(.*?)/mg;
                    var quote_msg = msg.message.replace(quote_re, "> $1");
                    $scope.body = "\n" + quote_msg;
                }

                $scope.send = function() {
                    // Trigger validation flag.
                    $scope.submitted = true;

                    // If form is invalid, return and let AngularJS show validation errors.
                    if (composeForm.$invalid) {
                        return;
                    }

                    var query = {
                        'type': 'send_message',
                        'to': toAddress.value,
                        'subject': subject.value,
                        'body': body.value
                    }
                    console.log('sending message with subject ' + subject)
                    socket.send('send_message', query)

                    $modalInstance.close();
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            };

        }
    ])