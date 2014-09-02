/**
 * User controller.
 *
 * @desc This controller is the user controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
angular.module('app')
    .controller('User', ['$scope', '$interval', '$routeParams', '$location', 'Connection',
        function($scope, $interval, $routeParams, $location, Connection) {

            $scope.page_loading = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', true);
            $scope.guid = $routeParams.userId;

            /**
             * Establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            Connection.$on('load_page', function(e, msg){ $scope.load_page(msg) });
            Connection.$on('store_contracts', function(e, msg){ $scope.parse_store_listings(msg) });
            Connection.$on('store_contract', function(e, msg){ $scope.parse_store_contract(msg) });
            Connection.$on('page', function(e, msg){ $scope.parse_page(msg) });
            Connection.$on('store_products', function(e, msg){ $scope.parse_store_products(msg) });
            Connection.$on('new_listing', function(e, msg){ $scope.parse_new_listing(msg) });

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
                Connection.send('query_page', query)

            }

            $scope.parse_page = function(msg) {

                $scope.page_loading = null
                console.log('Received a page for: ', msg)

                msg.senderNick = msg.senderNick.substring(0, 120);
                msg.text = msg.text.substring(0, 2048);

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
                Connection.send('query_store_products', query);

            }

            $scope.addNotary = function(guid, nickname) {

                //if(notaryGUID.length != 40 || !notaryGUID.match(/^[0-9a-z]+$/)) {
                //    alert('Incorrect format for GUID');
                //    return;
                //}
                $scope.page.isTrustedNotary = true

                Connection.send('add_trusted_notary', { 'type': 'add_trusted_notary',
                    'guid': guid,
                    'nickname': nickname
                    }
                );

                Notifier.success('Success', 'Notary added successfully.');


            }

            $scope.BuyItemCtrl = function($scope, $modal, $log) {

                $scope.open = function(size, myself, merchantPubkey, productTitle, productPrice, productDescription, productImageData, key, rawContract,
                    notaries, arbiters, btc_pubkey, guid) {

                    // Send socket a request for order info
                    //Connection.send('query_order', { orderId: orderId } )

                    notaries = $scope.settings.notaries;


                    modalInstance = $modal.open({
                        templateUrl: 'partials/modal/buyItem.html',
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

                        if (!$scope.$$phase) {
                            $scope.$apply();
                        }

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

                $scope.notaries = notaries

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
                        'sellerGUID': $scope.guid,
                        'listingKey': $scope.key,
                        'orderTotal': $('#totalPrice').html(),
                        'rawContract': rawContract,
                        'notary': $scope.order.notary,
                        'btc_pubkey': $scope.order.btc_pubkey,
                        'arbiter': $scope.order.arbiter
                    }
                    console.log(newOrder);
                    Connection.send('order', newOrder);
                    $scope.sentOrder = true;



                }

                $scope.closeConfirmation = function() {
                    $modalInstance.close();
                    window.location = '#/orders/purchases';
                }

                $scope.load_page({});

            };

            $scope.load_page({});
        }
    ]);
