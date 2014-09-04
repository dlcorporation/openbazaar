/**
 * Market controller.
 *
 * @desc This controller is the main controller for the market.
 * It contains all of the single page application logic.
 * @param {!angular.Scope} $scope
 * @constructor
 */
angular.module('app')
    .controller('Market', ['$scope', '$route', '$interval', '$routeParams', '$location', 'Connection',
        function($scope, $route, $interval, $routeParams, $location, Connection) {

            $scope.newuser = true;                   // Should show welcome screen?
            $scope.page = false;                     // Market page has been loaded
            $scope.dashboard = true;                 // Show dashboard
            $scope.myInfoPanel = true;               // Show information panel
            $scope.shouts = [];                      // Shout messages
            $scope.newShout = "";
            $scope.searching = "";
            $scope.currentReviews = [];
            $scope.myOrders = [];
            $scope.myReviews = [];

            $scope.peers = [];
            $scope.reviews = {};
            $scope.awaitingShop = null;
            $scope.page_loading = null;

            $scope.$emit('sidebar', true);

            /**
             * Establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            Connection.$on('peer', function(e, msg){ $scope.add_peer(msg); });
            Connection.$on('peers', function(e, msg){ $scope.update_peers(msg); });
            Connection.$on('peer_remove', function(e, msg){ $scope.remove_peer(msg); });
            Connection.$on('myself', function(e, msg){ $scope.parse_myself(msg); });
            Connection.$on('shout', function(e, msg){ $scope.parse_shout(msg); });
            Connection.$on('log_output', function(e, msg){ $scope.parse_log_output(msg); });
            Connection.$on('messages', function(e, msg){ $scope.parse_messages(msg); });
            Connection.$on('notaries', function(e, msg){ $scope.parse_notaries(msg); });
            Connection.$on('reputation', function(e, msg){ $scope.parse_reputation(msg); });
            Connection.$on('proto_response_pubkey', function(e, msg){ $scope.parse_response_pubkey(msg); });
            Connection.$on('burn_info_available', function(e, msg){ $scope.parse_burn_info(msg); });

            // Listen for Sidebar mods
            $scope.$on('sidebar', function(event, visible) {
                $scope.sidebar = visible;
            });

            var refresh_peers = function() {
                Connection.send('peers', {});
            };

            //$interval(refresh_peers,60000,0,true);

            /**
             * Create a shout and send it to all connected peers
             * Display it in the interface
             */
            $scope.createShout = function() {
                // launch a shout
                console.log($scope);
                var newShout = {
                    'type': 'shout',
                    'text': $scope.newShout,
                    'pubkey': $scope.myself.pubkey,
                    'senderGUID': $scope.myself.guid
                };
                Connection.send('shout', newShout);
                $scope.shouts.push(newShout);
                $scope.newShout = '';
            };

            // Toggle the sidebar hidden/shown
            $scope.toggleSidebar = function() {
                $scope.sidebar = !$scope.sidebar;
            };

            // Hide the sidebar
            $scope.hideSidebar = function() {
                $scope.sidebar = false;
            };

            // Show the sidebar
            $scope.showSidebar = function() {
                $scope.sidebar = true;
            };

            /**
             * [LEGACY] Adds review to a page
             * @pubkey -
             * @review -
             */
            var add_review_to_page = function(pubkey, review) {
                var found = false;

                console.log("Add review");

                if (!$scope.reviews.hasOwnProperty(pubkey)) {
                    $scope.reviews[pubkey] = [];
                }
                $scope.reviews[pubkey].forEach(function(_review) {
                    if (_review.sig == review.sig && _review.subject == review.subject && _review.pubkey == review.pubkey) {
                        console.log("Found a review for this market");
                        found = true;
                    }
                });
                if (!found) {
                    // check if the review is about me
                    if ($scope.myself.pubkey == review.subject) {
                        console.log("Found review for myself");
                        $scope.myReviews.push(review);
                    }
                    $scope.reviews[pubkey].push(review);
                }
                $scope.$apply();
                console.log($scope.reviews);
            };



            /**
             * Send log line to GUI
             * @msg - Message from server
             */
            $scope.parse_log_output = function(msg) {
                console.log(msg);
                $scope.log_output += msg.line;

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            };

            /**
             * Load notaries array into the GUI
             * @msg - Message from server
             */
            $scope.parse_notaries = function(msg) {
                $scope.trusted_notaries = msg.notaries;
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };



            $scope.parse_welcome = function(msg) {

                console.log(msg);

            };

            $scope.getNumber = function(num) {
                return new Array(num);
            };

            $scope.orders_page_changed = function() {
                console.log($scope.orders_current_page);
                var query = {
                    'page': $scope.orders_current_page - 1,
                    'merchant': $scope.merchant
                };
                Connection.send('query_orders', query);

            };

            $scope.parse_myorders = function(msg) {

                $scope.orders = msg.orders;
                $scope.orders_total = msg.total;
                $scope.orders_pages = msg.total % 10;
                $scope.orders_current_page = msg.page + 1;

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            };


            $scope.parse_contracts = function(msg) {

                console.log(msg);

                var page = msg.page;

                $scope.contracts = msg.contracts.contracts;

                $scope.total_contracts = msg.contracts.total_contracts;
                $scope.contracts_pages = $scope.total_contracts % 10;
                console.log('contracts', $scope.total_contracts);
                $scope.contracts_current_page = (page > 0) ? page - 1 : 0;
                console.log($scope);

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

            };

            $scope.message = {};
            $scope.parse_messages = function(msg) {
                if (msg !== null &&
                    msg.messages !== null &&
                    msg.messages.messages !== null &&
                    msg.messages.messages.inboxMessages !== null) {

                    $scope.messages = msg.messages.messages.inboxMessages;

                    $scope.message = {};
                    if (!$scope.$$phase) {
                        $scope.$apply();
                    }
                }
            };

            $scope.parse_response_pubkey = function(msg) {
                var pubkey = msg.pubkey;
                var nickname = msg.nickname;
                $scope.peers.forEach(function(peer) {
                    if (peer.pubkey == pubkey) {
                        // this peer!!
                        peer.nickname = msg.nickname;
                        if ($scope.searching == msg.nickname) {
                            $scope.queryShop(peer);
                        }
                    }
                });
                if (!$scope.$$phase) {

                    $scope.$apply();
                }
            };

            $scope.parse_burn_info = function(msg) {
                // console.log('Burn info available!');
                var SATOSHIS_IN_BITCOIN = 100000000;
                var amountInSatoshis = msg.amount;
                var bitcoins = msg.amount / SATOSHIS_IN_BITCOIN;
                bitcoins = Math.round(bitcoins * 10000) / 10000;

                // console.log(bitcoins);

                $scope.$apply(function() {
                    console.log(bitcoins);
                    console.log(msg.addr);
                    $scope.settings.burnAmount = bitcoins;
                    $scope.settings.burnAddr = msg.addr;
                });
            };

            // Peer information has arrived
            $scope.parse_reputation = function(msg) {

                console.log('Parsing reputation', msg.reviews);
                msg.reviews.forEach(function(review) {
                    add_review_to_page(review.subject, review);
                });
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };

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
            };

            $scope.update_peers = function(msg) {

                console.log('Refresh peers: ', msg);

                $scope.peers = msg.peers;

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };

            $scope.remove_peer = function(msg) {

                console.log('Remove peer: ', msg);

                $scope.peers = $scope.peers.filter(function(element) {
                    return element.uri != msg.uri;
                });

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };

            $scope.review = {
                rating: 5,
                text: ""
            };
            $scope.addReview = function() {

                var query = {
                    'type': 'review',
                    'pubkey': $scope.page.pubkey,
                    'text': $scope.review.text,
                    'rating': parseInt($scope.review.rating)
                };
                Connection.send('review', query);

                // store in appropriate format (its different than push format :P)
                add_review_to_page($scope.page.pubkey, {
                    type: 'review',
                    'pubkey': $scope.myself.pubkey,
                    'subject': $scope.page.pubkey,
                    'rating': query.rating,
                    text: query.text
                });

                $scope.review.rating = 5;
                $scope.review.text = '';
                $scope.showReviewForm = false;
            };

            // My information has arrived
            $scope.parse_myself = function(msg) {


                $scope.myself = msg;

                if (!$scope.$$phase) {
                    $scope.$apply();
                }


                // Settings
                $scope.settings = msg.settings;
                console.log(msg.settings);

                //msg.reputation.forEach(function(review) {
                //   add_review_to_page($scope.myself.pubkey, review)
                //});

                msg.peers.forEach(function(peer) {
                    $scope.add_peer(peer);
                });


            };

            // A shout has arrived
            $scope.parse_shout = function(msg) {
                $scope.shouts.push(msg);
                console.log('Shout', $scope.shouts);
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };



            $scope.checkOrderCount = function() {
                Connection.send('check_order_count', {});
            };

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
            };

            //TODO: This should probably be moved to the settings controllers.
            $scope.saveSettings = function(notify) {
                console.log($scope.settings);
                var query = {
                    'type': 'update_settings',
                    settings: $scope.settings
                };
                Connection.send('update_settings', query);
                if (typeof notify === "undefined") {
                    Notifier.success('Success', 'Settings saved successfully.');
                }
            };
            
            // Create a new order and send to the network
            $scope.newOrder = {
                message: '',
                tx: '',
                listingKey: '',
                productTotal: ''
            };
            $scope.createOrder = function() {

                $scope.creatingOrder = false;

                var newOrder = {
                    'text': $scope.newOrder.message,
                    'state': 'new',
                    'buyer': $scope.myself.pubkey,
                    'seller': $scope.page.pubkey,
                    'listingKey': $scope.newOrder.pubkey
                };

                Connection.send('order', newOrder);
                $scope.sentOrder = true;

                $scope.showDashboardPanel('orders');

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

                $('#pill-orders').addClass('active').siblings().removeClass('active').blur();
                $("#orderSuccessAlert").alert();
                window.setTimeout(function() {
                    $("#orderSuccessAlert").alert('close');
                }, 5000);

            };
            $scope.payOrder = function(order) {
                order.state = 'paid';
                order.tx = $scope.newOrder.tx;
                $scope.newOrder.tx = '';
                Connection.send('order', order);
            };
            $scope.receiveOrder = function(order) {
                order.state = 'received';
                Connection.send('order', order);
            };
            $scope.sendOrder = function(order) {
                order.state = 'Sent';
                Connection.send('order', order);

                $scope.queryMyOrder(0);

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            };

            $scope.cancelOrder = function(order) {
                order.state = 'cancelled';
                Connection.send('order', order);
            };

            $scope.addArbiter = function(arbiter) {
                var arbiterGUID = (arbiter !== '') ? arbiter : $('#inputArbiterGUID').val();
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
                    if ($.inArray(el, uniqueArbiters) === -1) {
                        uniqueArbiters.push(el);
                    }
                });

                $scope.settings.trustedArbiters = uniqueArbiters;

                $scope.saveSettings(false);
                Notifier.success('Success', 'Arbiter added successfully.');
            };

            $scope.removeArbiter = function(arbiterGUID) {

                // Dedupe arbiter GUIDs
                var uniqueArbiters = $scope.settings.trustedArbiters;
                $.each($scope.settings.trustedArbiters, function(i, el) {
                    if (el == arbiterGUID) {
                        uniqueArbiters.splice(i, 1);
                    }
                });

                $scope.settings.trustedArbiters = uniqueArbiters;

                $scope.saveSettings(false);
                Notifier.success('Success', 'Arbiter removed successfully.');
            };

            $scope.compose_message = function(size, myself, address, subject) {
                $scope.$broadcast("compose_message", {
                    size: size,
                    myself: myself,
                    bm_address: address,
                    subject: subject
                });
            };

            $scope.clearDHTData = function() {
                Connection.send('clear_dht_data', {});
                Notifier.success('Success', 'DHT cache cleared');
            };

            $scope.clearPeers = function() {
                Connection.send('clear_peers_data', {});
                Notifier.success('Success', 'Peers table cleared');
            };



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

            $scope.showDashboardPanel = function(panelName, e) {
                if (e) {
                    e.preventDefault();
                }

                resetPanels();

                if (panelName != 'myInfo') {
                    $scope.hideSidebar();
                    $('#dashboard-container').removeClass('col-sm-8').addClass('col-sm-12');
                } else {
                    $scope.showSidebar();
                    $('#dashboard-container').removeClass('col-sm-12').addClass('col-sm-8');
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

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            };

            $scope.getNotaries = function() {
                console.log('Getting notaries');
                Connection.send('get_notaries', {});
            };

            $scope.go = function (url, guid) {
              $location.path(url);
              if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };

            /**
             * Query the network for a merchant and then
             * show the page
             * @guid - GUID of page to load
             */
            $scope.queryShop = function(guid) {

                $scope.awaitingShop = guid;
                console.log('Querying for shop [market]: ', guid);

                var query = {
                    'type': 'query_page',
                    'findGUID': guid
                };

                $scope.page = null;
                Connection.send('query_page', query);
                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            };

            $scope.queryMessages = function() {
                // Query for messages
                var query = {
                    'type': 'query_messages'
                };
                console.log('querying messages');
                Connection.send('query_messages', query);
                console.log($scope.myself.messages);

            };

            // Modal Code
            $scope.WelcomeModalCtrl = function($scope, $modal, $log, $rootScope) {

                // Listen for changes to settings and if welcome is empty then show the welcome modal
                $scope.$watch('settings', function () {
                    console.log('settings',$scope.settings);
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
                        templateUrl: 'partials/welcome.html',
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

                };

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
                    Connection.send('welcome_dismissed', {});
                    $modalInstance.dismiss('cancel');
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
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
                    var composeModal = $modal.open({
                        templateUrl: 'partials/modal/composeMessage.html',
                        controller: $scope.ComposeMessageInstanceCtrl,
                        resolve: {
                            myself: function() {
                                return myself;
                            },
                            to_address: function() {
                                return to_address;
                            },
                            msg: function() {
                                return msg;
                            },
                        },
                        size: size
                    });
                    var afterFunc = function() {
                        $scope.showDashboardPanel('messages');
                    };
                    composeModal.result.then(
                        afterFunc,
                        function() {
                            $scope.queryMessages();
                            $log.info('Modal dismissed at: ' + new Date());
                        }
                    );
                };

                $scope.view = function(size, myself, to_address, msg) {
                    var viewModal = $modal.open({
                        templateUrl: 'partials/modal/viewMessage.html',
                        controller: $scope.ViewMessageInstanceCtrl,
                        resolve: {
                            myself: function() {
                                return myself;
                            },
                            to_address: function() {
                                return to_address;
                            },
                            msg: function() {
                                return msg;
                            },
                        },
                        size: size
                    });
                    var afterFunc = function() {
                        $scope.showDashboardPanel('messages');
                    };
                    viewModal.result.then(
                        afterFunc,
                        function() {
                            $log.info('Modal dismissed at: ' + new Date());
                        }
                    );
                };
            };

            $scope.ViewMessageInstanceCtrl = function($scope, $modalInstance, myself, to_address, msg) {
                $scope.myself = myself;
                $scope.my_address = myself.bitmessage;
                $scope.to_address = to_address;
                $scope.msg = msg;

                // Fill in form if msg is passed - reply mode
                if (msg !== null) {
                    $scope.toAddress = msg.fromAddress;
                    // Make sure subject start with RE:
                    var sj = msg.subject;
                    if (sj.match(/^RE:/) === null) {
                        sj = "RE: " + sj;
                    }
                    $scope.subject = sj;
                    // Quote message
                    var quote_re = /^(.*?)/mg;
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
                    };
                    console.log('sending message with subject ' + subject);
                    Connection.send('send_message', query);

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
                if (msg !== null) {
                    $scope.toAddress = msg.fromAddress;
                    // Make sure subject start with RE:
                    var sj = msg.subject;
                    if (sj.match(/^RE:/) === null) {
                        sj = "RE: " + sj;
                    }
                    $scope.subject = sj;
                    // Quote message
                    var quote_re = /^(.*?)/mg;
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
                    };
                    Connection.send('send_message', query);

                    $modalInstance.close();
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };


            };

            // Modal Code
            $scope.AddNodeModalCtrl = function($scope, $modal, $log) {

                $scope.open = function(size, backdrop, scope) {

                    backdrop = backdrop ? backdrop : true;

                    var modalInstance = $modal.open({
                        templateUrl: 'partials/modal/addNode.html',
                        controller: AddNodeModalInstance,
                        size: size,
                        backdrop: backdrop,
                        resolve: {
                        }
                    });

                    modalInstance.result.then(function(selectedItem) {
                        $scope.selected = selectedItem;
                    }, function() {
                        $log.info('Modal dismissed at: ' + new Date());
                    });

                };

            };

            var AddNodeModalInstance = function($scope, $modalInstance) {

                $scope.addGUID = function(newGUID) {

                    if(newGUID.length == 40 && newGUID.match(/^[A-Za-z0-9]+$/)) {
                        Connection.send('add_node', { 'type': 'add_guid', 'guid': newGUID });
                        console.log('Added node by GUID');
                    }
                    $modalInstance.dismiss('cancel');
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            };

        }
    ]);
