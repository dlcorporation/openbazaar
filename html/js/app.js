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

angular.module('app').controller('Market', ['$scope', function($scope) {

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
     var newShout = {'type': 'shout', 'text': $scope.newShout, 'pubkey': $scope.myself.pubkey}
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
     $scope.dashboard = false;
     $scope.showStorePanel('storeProducts');
     $scope.awaitingShop = peer.pubkey;
     var query = {'type': 'query_page', 'pubkey': peer.pubkey}
     socket.send('query_page', query)
  }


 // Open the websocket connection and handle messages
  var socket = new Connection(function(msg) {
   switch(msg.type) {
      case 'peer':
         $scope.add_peer(msg)
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

      $('#modalOrderDescription').html(msg.order.text);
      $('#modalBuyer').html(msg.order.buyer);
      $('#modalPaymentAddress').html('<a href="https://blockchain.info/address/'+msg.order.address+'" target="_blank">'+msg.order.address+'</a>');
      $('#modalCreated').html(new Date(msg.order.created*1000));

      msg.order.escrows.forEach(function(escrow) {
        escrows = "<li>" + escrow + "</li>";
      });

      $('#modalEscrows').html(escrows);


      if (!$scope.$$phase) {
         //console.log($scope.myOrders);
         $scope.$apply();
      }
  }

  $scope.parse_welcome = function(msg) {

    console.log(msg)

  }

  $scope.parse_myorders = function(msg) {

  	  console.log('Retrieved my orders: ',msg);
  	  $scope.orders = msg['orders'];
      console.log($scope.orders);

      if (!$scope.$$phase) {
	       $scope.$apply();
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

  $scope.parse_page = function(msg) {

    if (msg.pubkey != $scope.awaitingShop)
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

    console.log('Add peer: ',msg);

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
    console.log('Shout',msg)
    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }
  $scope.search = ""
  $scope.searchNickname = function() {
     var query = {'type': 'search', 'text': $scope.search };
     $scope.searching = $scope.search;
     socket.send('search', query)
     $scope.search = ""
  }

  $scope.settings = { email:'', PGPPubKey:'', bitmessage:'', pubkey:'', secret:'', nickname:'', welcome:'', escrowAddresses:''}
  $scope.saveSettings = function() {
      var query = {'type': 'update_settings', settings: $scope.settings }
      socket.send('update_settings', query)
  }


  // Create a new order and send to the network
  $scope.newOrder = {text:'', tx: ''}
  $scope.createOrder = function() {
      $scope.creatingOrder = false;
      var newOrder = {
          'text': $scope.newOrder.text,
          'state': 'new',
          'buyer': $scope.myself.pubkey,
          'seller': $scope.page.pubkey
      }
      $scope.newOrder.text = '';
      //$scope.orders.push(newOrder);     // This doesn't really do much since it gets wiped away
      socket.send('order', newOrder);
      $scope.sentOrder = true;

      $scope.showDashboardPanel('orders');

      $('#pill-orders').addClass('active').siblings().removeClass('active').blur();
      $("#orderSuccessAlert").alert();
      window.setTimeout(function() { $("#orderSuccessAlert").alert('close') } , 5000);

  }
  $scope.payOrder = function(order) {
      order.state = 'payed'
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
  			$scope.messagesPanel = true;
  			break;
  		case 'reviews':
  			$scope.reviewsPanel = true;
  			break;
  		case 'orders':
  			$scope.ordersPanel = true;
  			$scope.queryMyOrder();
  			break;
  		case 'productCatalog':
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
  	$scope.storeProductsPanel = false;
  	$scope.storeReviewsPanel = false;
  	$scope.storeOrdersPanel = false;
  	$scope.storeInfoPanel = false;
  	$scope.storeOrderHistoryPanel = false;
  }

  $scope.showStorePanel = function(panelName) {

    resetStorePanels();
  	$scope.dashboard = false;


  	switch(panelName) {
  		case 'storeProducts':
  			$scope.storeProductsPanel = true;
  			break;
  		case 'storeOrders':
  			//$scope.storeOrdersPanel = true;
  			break;
  		case 'storeReviews':
  			$scope.storeReviewsPanel = true;
  			break;
  		case 'storeInfo':
  			$scope.storeInfoPanel = true;
  			break;

  	}
  }


  $scope.queryMyOrder = function() {
    	// Query for orders
    	var query = {'type': 'query_orders', 'pubkey': ''}
    	console.log('querying orders')
    	socket.send('query_orders', query)

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
          }
        }
      });

      modalInstance.result.then(function () {

      }, function () {
        $log.info('Modal dismissed at: ' + new Date());
      });
    };
  };

 var ViewOrderInstanceCtrl = function ($scope, $modalInstance, orderId) {

   $scope.orderId = orderId;

    $scope.ok = function () {
      $modalInstance.close();
    };

    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
  };




}])
