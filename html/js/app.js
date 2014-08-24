var app = angular.module('app', ['ui.bootstrap', 'ngRoute', 'obControllers'])


app.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/dashboard', {
        templateUrl: 'partials/dashboard.html',
        controller: 'Market'
      }).
      when('/orders/sales', {
        templateUrl: 'partials/orders.html',
        controller: 'Orders'
      }).
      when('/orders/purchases', {
        templateUrl: 'partials/orders.html',
        controller: 'Orders'
      }).
      when('/contracts', {
        templateUrl: 'partials/contracts.html',
        controller: 'Contracts'
      }).
      when('/settings', {
        templateUrl: 'partials/settings.html',
        controller: 'Settings'
      }).
      when('/search', {
        templateUrl: 'partials/search.html',
        controller: 'Search'
      }).
      when('/arbiter', {
        templateUrl: 'partials/arbiter.html',
        controller: 'Arbiter'
      }).
      when('/user/:userId/products', {
        templateUrl: 'partials/user.html',
        controller: 'User'
      }).
      when('/user/:userId/services', {
        templateUrl: 'partials/user.html',
        controller: 'User'
      }).
      when('/user/:userId', {
        templateUrl: 'partials/user.html',
        controller: 'User'
      }).
      when('/settings/:section', {
        templateUrl: 'partials/settings.html',
        controller: 'Settings'
      }).
      otherwise({
        redirectTo: '/dashboard'
      });
}]);

/**
 * This directive is used for converting identicon tags
 * to actual identicons in the HTML
 */
angular.module('app').directive('identicon', function() {
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

app.directive('numberOnlyInput', function () {
    return {
        restrict: 'EA',
        template: '<input name="{{inputName}}" ng-model="inputValue" placeholder="" class="form-control" />',
        scope: {
            inputValue: '=',
            inputName: '=',
            inputPlaceholder: '='
        },
        link: function (scope) {
            scope.$watch('inputValue', function(newValue,oldValue) {
                var arr = String(newValue).split("");
                if (arr.length === 0) return;
                if (arr.length === 1 && (arr[0] == '-' || arr[0] === '.' )) return;
                if (arr.length === 2 && newValue === '-.') return;
                if (isNaN(newValue)) {
                    scope.inputValue = oldValue;
                }
            });
        }
    };
});

/**
 * This configuration item allows us to safely use the bitcoin:
 * URI for applications that register that URI
 */
angular.module('app')
    .config([
        '$compileProvider',
        function($compileProvider) {
            $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|chrome-extension|bitcoin):/);
            // Angular before v1.2 uses $compileProvider.urlSanitizationWhitelist(...)
        }
    ]);

app.directive("validateOnBlur", [function() {
    var ddo = {
        restrict: "A",
        require: "ngModel",
        scope: {},
        link: function(scope, element, attrs, modelCtrl) {
            element.on('blur', function () {
                modelCtrl.$showValidationMessage = modelCtrl.$dirty;
                scope.$apply();
            });
        }
    };
    return ddo;
}]);



function validate_bitcoin_address(address) {
    var result = false;

    if(address.length>34 || address.length<27)  /* not valid string length */
        return result;

    if(/[0OIl]/.test(address))   /* this character are invalid in base58 encoding */
        return result;

    $.ajax({
        url : "https://blockchain.info/it/q/addressbalance/" + address,   /* return balance in satoshi */
        async : false
    }).done(function(data) {
        var isnum = /^\d+$/.test(data);
        if (isnum) {                         /* if the returned data are all digits, it's valid */
            console.log("data is integer");
            result = true;
        }
    });
    return result;
}