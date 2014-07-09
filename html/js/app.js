angular.module('app', ['ui.bootstrap'])

angular.module('app').directive('identicon', function () {
    return {
      restrict: 'E', // element
      scope: {
        hash: '=',
        iconSize: '='
      },
      link: function(scope, element, attrs) {
        var iconSize = scope.iconSize || 32;

        // Create the identicon
        function createFromHex(dataHex) {
          var data = new Identicon(dataHex, iconSize).toString();
          element.html('<img class="identicon" src="data:image/png;base64,' + data + '">');
        }
        // Watch for hash changes
        scope.$watch('hash', function() {
          if (scope.hash) {
            var tohash = scope.hash.substring(32, 64)
            createFromHex(tohash);
          }
        })
      }
    }
  });

angular.module('app')
  .controller('Market', ['$scope', function($scope) {

  $scope.newuser = true
  $scope.page = false
  $scope.dashboard = true
  $scope.myInfoPanel = true
  $scope.shouts = [];
  $scope.newShout = ""
  $scope.searching = ""
  $scope.currentReviews = []
  $scope.myOrders = []
  $scope.myReviews = []
  $scope.sidebar = true

  $scope.createShout = function() {
     // launch a shout
     console.log($scope)
     var newShout = {'type': 'shout', 'text': $scope.newShout, 'pubkey': $scope.myself.pubkey, 'senderGUID': $scope.myself.guid}
     socket.send('shout', newShout)
     $scope.shouts.push(newShout)
     $scope.newShout = '';
  }

  $scope.peers = [];
  $scope.reviews = {};

  $scope.toggleSidebar = function() {
    $scope.sidebar = ($scope.sidebar) ? false : true;
  }

  $scope.hideSidebar = function() {
    $scope.sidebar = false;
  }

  $scope.showSidebar = function() {
    $scope.sidebar = true;
  }

  $scope.awaitingShop = null;
  $scope.queryShop = function(peer) {
     console.log('Shop',peer);
     $scope.awaitingShop = peer.guid;
     console.log('Querying for shop: ',peer);
     var query = {'type': 'query_page', 'findGUID': peer.guid}

     $('#listing-loader').show();
     socket.send('query_page', query)
     $('#store-tabs li').removeClass('active');
  	 $('#store-tabs li').first().addClass('active');
  }


 // Open the websocket connection and handle messages
  var socket = new Connection(function(msg) {

   switch(msg.type) {

      case 'peer':
         $scope.add_peer(msg)
         break;
      case 'peers':
         $scope.update_peers(msg)
         break;
      case 'peer_remove':
         $scope.remove_peer(msg)
         break;
      case 'page':
         $scope.parse_page(msg)
         break;
      case 'myself':
         $scope.parse_myself(msg)
         break;
      case 'shout':
         $scope.parse_shout(msg)
         break;
      case 'order':
         $scope.parse_order(msg)
         break;
      case 'myorders':
      	 $scope.parse_myorders(msg)
      	 break;
      case 'contracts':
         $scope.parse_contracts(msg)
         break;
      case 'messages':
         $scope.parse_messages(msg)
         break;
      case 'store_products':
         $scope.parse_store_products(msg)
         break;
      case 'new_listing':
         $scope.parse_new_listing(msg)
         break;
      case 'orderinfo':
         $scope.parse_orderinfo(msg)
         break;
      case 'reputation':
      	 console.log(msg);
         $scope.parse_reputation(msg)
         break;
      case 'proto_response_pubkey':
         $scope.parse_response_pubkey(msg)
         break;
      default:
         console.log("Unhandled message!",msg)
         break;
    }
  })

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

  $scope.parse_order = function(msg) {

  	  console.log("Order update");

      if ($scope.myOrders.hasOwnProperty(msg.id)) {
          console.log("Updating order!")
          $scope.myOrders[msg.id].state = msg.state
          $scope.myOrders[msg.id].tx = msg.tx
          $scope.myOrders[msg.id].escrows = msg.escrows
          $scope.myOrders[msg.id].address = msg.address
          return;
      } else {
          console.log(msg);
          $scope.myOrders.push(msg);
      }
      if (!$scope.$$phase) {
      	 console.log($scope.myOrders);
         $scope.$apply();
      }
  }

  $scope.parse_orderinfo = function(msg) {

      console.log("Order info retrieved");
      console.log(msg.order);

      $scope.modalOrder = msg.order;


      if(msg.order.state == 'accepted') {
        $scope.modalOrder.waitingForPayment = true;
      } else if (msg.order.state == 'paid') {

        if (msg.order.seller == $scope.myself.pubkey) {
          $scope.modalOrder.waitingForShipment = true;
        } else {
          $scope.modalOrder.waitingForSellerToShip = true;
        }
      } else if(msg.order.state == 'sent') {
        $scope.modalOrder.flagForArbitration = true;
      } else {
        $scope.modalOrder.waitingForPayment = false;
      }

      if (!$scope.$$phase) {

         $scope.$apply();
      }
  }

  $scope.parse_welcome = function(msg) {

    console.log(msg)

  }

  $scope.parse_myorders = function(msg) {


  	  $scope.orders = msg['orders'];


      if (!$scope.$$phase) {
	       $scope.$apply();
	    }

  }

  $scope.contract2 = {};
  $scope.parse_contracts = function(msg) {
      console.log(msg);

      $scope.contracts = msg.contracts.contracts;

      $scope.contract2 = {};
      if (!$scope.$$phase) {
         $scope.$apply();
      }

  }

  $scope.message = {};
  $scope.parse_messages = function(msg) {
      if(msg != null &&
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

  $scope.parse_page = function(msg) {

    console.log('Receive a page for: ',msg)
    console.log('Waiting for: '+$scope.awaitingShop)

    $scope.dashboard = false;
    $scope.showStorePanel('storeInfo');

    if (msg.senderGUID != $scope.awaitingShop)
       return
    if (!$scope.reviews.hasOwnProperty(msg.pubkey)) {
        $scope.reviews[msg.pubkey] = []
    }

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

  $scope.add_peer = function(msg) {

    console.log('Add peer: ', msg);

    /* get index if peer is already known */
    var index = [-1].concat($scope.peers).reduce(
        function(previousValue, currentValue, index, array){
            return currentValue.uri == msg.uri ? index : previousValue ;
    });

    if(index == -1) {
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

    console.log('Remove peer: ',msg);

    $scope.peers = $scope.peers.filter(function(element) {
        return element.uri != msg.uri;
    });

    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }

  $scope.review= {rating:5, text:""}
  $scope.addReview = function() {

     var query = {'type': 'review', 'pubkey': $scope.page.pubkey, 'text': $scope.review.text, 'rating': parseInt($scope.review.rating)}
     socket.send('review', query)

     // store in appropriate format (its different than push format :P)
     add_review_to_page($scope.page.pubkey, {type: 'review', 'pubkey': $scope.myself.pubkey, 'subject': $scope.page.pubkey, 'rating': query.rating, text: query.text})

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

    msg.reputation.forEach(function(review) {
       add_review_to_page($scope.myself.pubkey, review)
    });

    msg.peers.forEach(function(peer) {
       $scope.add_peer(peer)
    });


  }

  // A shout has arrived
  $scope.parse_shout = function(msg) {
    $scope.shouts.push(msg)
    console.log('Shout',$scope.shouts)
    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }

  // A listing has shown up from the network
  $scope.store_listings = [];
  $scope.parse_new_listing = function(msg) {
    console.log(msg.data);
    contract_data = msg.data;
    $scope.store_listings.push(contract_data)
    $scope.store_listings = jQuery.unique($scope.store_listings);
    $.each( $scope.store_listings, function(index, contract){
        console.log('TEST',contract);
        if (contract.Contract.item_images.length < 1) {
            $scope.store_listings[index].productImageData = "img/no-photo.png";
        }
    });
    $('#listing-loader').hide();
    console.log('New Listing',$scope.store_listings)
    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }

  $scope.search = ""
  $scope.searchNetwork = function() {
     var query = {'type': 'search', 'key': $scope.search };
     $scope.searching = $scope.search;
     $scope.awaitingShop = $scope.search;
     socket.send('search', query)
     $scope.search = ""
  }

  $scope.settings = { email:'',
                      PGPPubKey:'',
                      bitmessage:'',
                      pubkey:'',
                      secret:'',
                      nickname:'',
                      welcome:'',
                      escrowAddresses:''}
  $scope.saveSettings = function() {
      var query = {'type': 'update_settings', settings: $scope.settings }
      socket.send('update_settings', query)
  }


  // Create a new order and send to the network
  $scope.newOrder = {message:'', tx: '', listingKey:'', productTotal:''}
  $scope.createOrder = function() {

      $scope.creatingOrder = false;

      var newOrder = {
          'text': $scope.newOrder.message,
          'state': 'new',
          'buyer': $scope.myself.pubkey,
          'seller': $scope.page.pubkey,
          'listingKey': $scope.newOrder.pubkey
      }
      console.log(newOrder);
      //$scope.newOrder.text = '';
      //$scope.orders.push(newOrder);     // This doesn't really do much since it gets wiped away
      socket.send('order', newOrder);
      $scope.sentOrder = true;

      $scope.showDashboardPanel('orders');

      $('#pill-orders').addClass('active').siblings().removeClass('active').blur();
      $("#orderSuccessAlert").alert();
      window.setTimeout(function() { $("#orderSuccessAlert").alert('close') } , 5000);

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
      order.state = 'sent'
      socket.send('order', order);
  }

  $scope.cancelOrder = function(order) {
  	order.state = 'cancelled'
  	socket.send('order', order)
  }

  $scope.removeContract = function(contract_id) {
     socket.send("remove_contract", {"contract_id":contract_id});
     socket.send("query_contracts", {})
  }

  $scope.republishListing = function(productID) {
     socket.send("republish_listing", {"productID":productID});
     socket.send("query_contracts", {})
  }


  $scope.addEscrow = function() {
    escrowAddress = $('#inputEscrowAddress').val();
    $('#inputEscrowAddress').val('');

    // TODO: Check for valid escrow address

    if(!$scope.settings.escrowAddresses) {
      $scope.settings.escrowAddresses = [];
    }
    $scope.settings.escrowAddresses.push(escrowAddress);

    // Dedupe escrow addresses
    var uniqueEscrows = [];
    $.each($scope.settings.escrowAddresses, function(i, el){
        if($.inArray(el, uniqueEscrows) === -1) uniqueEscrows.push(el);
    });

    $scope.settings.escrowAddresses = uniqueEscrows;

    $scope.saveSettings();
  }

  function resetPanels() {
  	$scope.messagesPanel = false;
  	$scope.reviewsPanel = false;
  	$scope.productCatalogPanel = false;
  	$scope.settingsPanel = false;
    $scope.arbitrationPanel = false;
  	$scope.ordersPanel = false;
  	$scope.myInfoPanel = false;
  }

  $scope.showDashboardPanel = function(panelName) {

    resetPanels();

    if(panelName != 'myInfo') {
      $scope.hideSidebar();
      $('#dashboard-container').removeClass('col-sm-8').addClass('col-sm-12')
    } else {
      $scope.showSidebar();
      $('#dashboard-container').removeClass('col-sm-12').addClass('col-sm-8')
    }

    $scope.dashboard = true;
    $scope.page = false;

  	switch(panelName) {
  		case 'messages':
            $scope.queryMessages();
  			$scope.messagesPanel = true;
  			break;
  		case 'reviews':
  			$scope.reviewsPanel = true;
  			break;
  		case 'orders':
  			$scope.ordersPanel = true;
  			$scope.queryMyOrder();
  			break;
        case 'arbitration':
            $scope.arbitrationPanel = true;
            break;
  		case 'productCatalog':
            $scope.queryProducts();
  			$scope.productCatalogPanel = true;
  			break;
  		case 'settings':
  			$scope.settingsPanel = true;
  			break;
  		case 'myInfo':
  			$scope.myInfoPanel = true;
  			break;

  	}
  }


  function resetStorePanels() {
    $scope.storeInfoPanel = false;
  	$scope.storeProductsPanel = false;
  	$scope.storeReviewsPanel = false;
  	$scope.storeOrderHistoryPanel = false;
    $scope.storeArbiterPanel = false;
  }

  $scope.showStorePanel = function(panelName) {

    resetStorePanels();
  	$scope.dashboard = false;

  	switch(panelName) {
      case 'storeInfo':
        $scope.storeInfoPanel = true;
        break;
      case 'storeProducts':
            $('#listing-loader').show();
  	        $scope.storeProductsPanel = true;
            $scope.store_listings = [];
            $scope.queryStoreProducts($scope.awaitingShop);
  			break;
  		case 'storeOrders':
  			//$scope.storeOrdersPanel = true;
  			break;
  		case 'storeReviews':
  			$scope.storeReviewsPanel = true;
  			break;
  	  case 'storeArbiter':
  			$scope.storeArbiterPanel = true;
  			break;

  	}
  }

  // Query for product listings from this store
  $scope.queryStoreProducts = function(storeID) {

    console.log('Querying for contracts in store: '+storeID);
    var query = { 'type':'query_store_products', 'key': storeID }
    socket.send('query_store_products', query);

  }


  $scope.queryMyOrder = function() {
    	// Query for orders
    	var query = {'type': 'query_orders', 'pubkey': ''}
    	console.log('querying orders')
    	socket.send('query_orders', query)

  }

  $scope.queryProducts = function() {
      // Query for products
      var query = {'type': 'query_contracts', 'pubkey': ''}
      console.log('querying products')
      socket.send('query_contracts', query)

  }

  $scope.queryMessages = function() {
      // Query for messages
      var query = {'type': 'query_messages'}
      console.log('querying messages')
      socket.send('query_messages', query)
      console.log($scope.myself.messages)

  }

  $scope.generateNewSecret = function() {

    var query = {'type': 'generate_secret'}
    console.log('Generating new secret key')
    socket.send('generate_secret', query)
    console.log($scope.myself.settings)

  }



  $('ul.nav.nav-pills li a').click(function() {
	    $(this).parent().addClass('active').siblings().removeClass('active').blur();
	});



// Modal Code
$scope.WelcomeModalCtrl = function ($scope, $modal, $log) {



  $scope.open = function (size, backdrop) {

      backdrop = backdrop ? backdrop : true;

      var modalInstance = $modal.open({
        templateUrl: 'myModalContent.html',
        controller: ModalInstanceCtrl,
        size: size,
        backdrop: backdrop,
        resolve: {
          settings: function () {
            return $scope.settings;
          }
        }
      });

      modalInstance.result.then(function (selectedItem) {
        $scope.selected = selectedItem;
      }, function () {
        $log.info('Modal dismissed at: ' + new Date());
      });

    }


};

  // Please note that $modalInstance represents a modal window (instance) dependency.
  // It is not the same as the $modal service used above.

  var ModalInstanceCtrl = function ($scope, $modalInstance, settings) {

    $scope.settings = settings;
    // $scope.selected = {
    //   item: $scope.items[0]
    // };
    //

    $scope.welcome = settings.welcome;



    $scope.ok = function () {
      $modalInstance.dismiss('cancel');
    };

    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
  };




  $scope.ViewOrderCtrl = function ($scope, $modal, $log) {



    $scope.open = function (size, orderId) {

      // Send socket a request for order info
      socket.send('query_order', { orderId: orderId } )

      var modalInstance = $modal.open({
        templateUrl: 'viewOrder.html',
        controller: ViewOrderInstanceCtrl,
        size: size,
        resolve: {
          orderId: function() {
            return orderId;
          },
          scope: function() { return $scope }
        }
      });

      modalInstance.result.then(function () {

      }, function () {
        $log.info('Modal dismissed at: ' + new Date());
      });
    };
  };


 var ViewOrderInstanceCtrl = function ($scope, $modalInstance, orderId, scope) {


   $scope.orderId = orderId;
   $scope.Market = scope;

   $scope.markOrderPaid = function(orderId) {

    socket.send("pay_order", { orderId: orderId} )

    scope.modalOrder.state = 'paid';
    scope.modalOrder.waitingForPayment = false;

    // Refresh orders in background
    scope.queryMyOrder();

    if (!$scope.$$phase) {
       $scope.$apply();
    }

   }


   $scope.markOrderShipped = function(orderId) {

    socket.send("ship_order", { orderId: orderId} )

    scope.modalOrder.state = 'sent';
    scope.modalOrder.waitingForShipment = false;

    // Refresh orders in background
    scope.queryMyOrder();

    if (!$scope.$$phase) {
       $scope.$apply();
    }

   }

    $scope.ok = function () {
      $modalInstance.close();
    };

    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
  };


// Modal Code

$scope.ProductModal = function ($scope, $modal, $log) {

  $scope.open = function (size, backdrop) {

      backdrop = backdrop ? backdrop : true;

      var modalInstance = $modal.open({
        templateUrl: 'addContract.html',
        controller: ProductModalInstance,
        size: size,
        backdrop: backdrop,
        resolve: {
          contract: function () {
            return {"contract":$scope.contract};
          }
        }
      });

      modalInstance.result.then(function (selectedItem) {
        $scope.selected = selectedItem;
      }, function () {
        $log.info('Product modal dismissed at: ' + new Date());
      });

    }


};

var ProductModalInstance = function ($scope, $modalInstance, contract) {

  $scope.contract = contract;
  $scope.contract.productCondition = 'New';

    $scope.createContract = function() {

        console.log($scope.contract);

        if(contract.contract) {

            // Imported JSON format contract
            jsonContract = $scope.contract.rawText;
            console.log(jsonContract);

            socket.send("import_raw_contract", {'contract':jsonContract});

        } else {

            contract = {  };
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
            $.each(keywords, function(i, el){
                if($.inArray(el, contract.Contract.item_keywords) === -1) contract.Contract.item_keywords.push(el);
            });

            var imgUpload = document.getElementById('inputProductImage').files[0];

            if(imgUpload) {

              if (imgUpload.type != '' && $.inArray(imgUpload.type, ['image/jpeg', 'image/gif', 'image/png']) != -1) {

                var r = new FileReader();
                r.onloadend = function(e){
                  var data = e.target.result;

                  contract.Contract.item_images.image1 = imgUpload.result;

                  console.log(contract);
                  socket.send("create_contract", contract);
                  socket.send("query_contracts", {})


                }
                r.readAsArrayBuffer(imgUpload);


              } else {

                console.log(contract);
                socket.send("create_contract", contract);

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

  $scope.saveProduct = function () {

    var imgUpload = document.getElementById('inputProductImage').files[0];

    if(imgUpload) {

      if (imgUpload.type != '' && $.inArray(imgUpload.type, ['image/jpeg', 'image/gif', 'image/png']) != -1) {

        var r = new FileReader();
        r.onloadend = function(e){
          var data = e.target.result;

          $scope.product.productImageName = imgUpload.name;
          $scope.product.productImageData = imgUpload.result;
          console.log(imgUpload);

          console.log('SAVED:',$scope.product);
          socket.send("save_product", $scope.product)
          socket.send("query_contracts", {})

          $modalInstance.dismiss('cancel');


        }
        r.readAsArrayBuffer(imgUpload);

      } else {
        console.log('SAVED:',$scope.product);
        socket.send("save_product", $scope.product)
        socket.send("query_contracts", {})

        $modalInstance.dismiss('cancel');
      }

    } else {

      console.log('SAVED:',$scope.product);
      socket.send("save_product", $scope.product)
      socket.send("query_contracts", {})

      $modalInstance.dismiss('cancel');
    }



  };

  $scope.cancel = function () {
    socket.send("query_contracts", {});
    $modalInstance.dismiss('cancel');
  };

  $scope.toggleItemAdvanced = function() {

    $scope.itemAdvancedDetails = ($scope.itemAdvancedDetails) ? 0 : 1;
  }




};


$scope.BuyItemCtrl = function ($scope, $modal, $log) {

    $scope.open = function (size, myself, merchantPubkey, productTitle, productPrice, productDescription, productImageData) {



      // Send socket a request for order info
      //socket.send('query_order', { orderId: orderId } )

      modalInstance = $modal.open({
        templateUrl: 'buyItem.html',
        controller: $scope.BuyItemInstanceCtrl,
        resolve: {
            merchantPubkey: function() { return merchantPubkey },
            myself: function() { return myself },
            productTitle: function() { return productTitle},
            productPrice: function() { return productPrice},
            productDescription: function() { return productDescription},
            productImageData: function() { return productImageData}
        },
        size: size
      });

      modalInstance.result.then(function () {

        $scope.showDashboardPanel('orders');

        $('#pill-orders').addClass('active').siblings().removeClass('active').blur();
        $("#orderSuccessAlert").alert();
        window.setTimeout(function() { $("#orderSuccessAlert").alert('close') } , 5000);

      }, function () {
        $log.info('Modal dismissed at: ' + new Date());

      });
    };
  };


$scope.BuyItemInstanceCtrl = function ($scope, $modalInstance, myself, merchantPubkey, productTitle, productPrice, productDescription, productImageData) {

    console.log(productTitle, productPrice, productDescription, productImageData);
    $scope.myself = myself;
    $scope.merchantPubkey = merchantPubkey;
    $scope.productTitle = productTitle;
    $scope.productPrice = productPrice;
    $scope.productDescription = productDescription;
    $scope.productImageData = productImageData;

    $scope.ok = function () {
      $modalInstance.close();
    };

    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };


    $scope.newOrder = {message:'', tx: '', listingKey:'', listingTotal:'', productTotal:''}
    $scope.createOrder = function() {

      $scope.creatingOrder = false;

      var newOrder = {
          'message': $scope.newOrder.message,
          'state': 'new',
          'buyer': $scope.myself.pubkey,
          'seller': $scope.merchantPubkey,
          'listingKey': $scope.newOrder.listingKey,
          'listingTotal': $scope.newOrder.listingTotal
      }
      //console.log(newOrder);
      //$scope.newOrder.text = '';
      //$scope.orders.push(newOrder);     // This doesn't really do much since it gets wiped away
      socket.send('order', newOrder);
      $scope.sentOrder = true;

      console.log($scope);

      $modalInstance.close();

    }



  };


$scope.ComposeMessageCtrl = function ($scope, $modal, $log) {
    $scope.compose = function (size, myself, my_address, msg) {
      composeModal = $modal.open({
        templateUrl: 'composeMessage.html',
        controller: $scope.ComposeMessageInstanceCtrl,
        resolve: {
            myself: function() { return myself },
            my_address: function() { return my_address },
            msg: function() { return msg; },
        },
        size: size
      });
      afterFunc = function () {
        $scope.showDashboardPanel('messages');
      };
      composeModal.result.then(afterFunc,
          function () {
            $log.info('Modal dismissed at: ' + new Date());
      });
    };
    $scope.view = function (size, myself, my_address, msg) {
      viewModal = $modal.open({
        templateUrl: 'viewMessage.html',
        controller: $scope.ViewMessageInstanceCtrl,
        resolve: {
            myself: function() { return myself },
            my_address: function() { return my_address },
            msg: function() { return msg },
        },
        size: size
      });
      afterFunc = function () {
        $scope.showDashboardPanel('messages');
      };
      viewModal.result.then(afterFunc,
          function () {
            $log.info('Modal dismissed at: ' + new Date());
      });
    };
  };


$scope.ComposeMessageInstanceCtrl = function ($scope, $modalInstance, myself, my_address, msg) {
    $scope.myself = myself;
    $scope.my_address = my_address;
    $scope.msg = msg;

    // Fill in form if msg is passed - reply mode
    if(msg != null) {
        $scope.toAddress = msg.fromAddress;
        // Make sure subject start with RE: 
        var sj = msg.subject;
        if(sj.match(/^RE:/) == null) {
            sj = "RE: " + sj;
        }
        $scope.subject = sj;
        // Quote message
        quote_re = /^(.*?)/mg;
        var quote_msg = msg.message.replace(quote_re, "> $1");
        $scope.body = "\n"+quote_msg;
    }

    $scope.send = function () {
      // Trigger validation flag.
      $scope.submitted = true;

      // If form is invalid, return and let AngularJS show validation errors.
      if (composeForm.$invalid) {
        return;
      }

      var query = {'type': 'send_message', 'to': toAddress.value,
                   'subject': subject.value, 
                   'body': body.value}
      console.log('sending message with subject ' + subject)
      socket.send('send_message', query)

      $modalInstance.close();
    };

    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
};

$scope.ViewMessageInstanceCtrl = function ($scope, $modalInstance, myself, my_address, msg) {

    $scope.myself = myself;
    $scope.my_address = my_address;
    $scope.msg = msg;

    $scope.close = function () {
      $modalInstance.dismiss('cancel');
    };
};

}])
