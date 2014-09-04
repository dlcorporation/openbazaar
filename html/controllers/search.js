/**
 * Search controller.
 *
 * @desc This controller is the search controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
angular.module('app')
    .controller('Search', ['$scope', '$interval', '$routeParams', '$location', 'Connection',
        function($scope, $interval, $routeParams, $location, Connection) {

            $scope.searchPanel = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', false);

            /**
             * Establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            Connection.$on('load_page', function(e, msg){ $scope.load_page(msg); });
            Connection.$on('global_search_result', function(e, msg){ $scope.parse_search_result(msg); });

            $scope.load_page = function(msg) {
                console.log($location.search());
                $('#dashboard-container').removeClass('col-sm-8').addClass('col-sm-12');
                $scope.searchNetwork();
            };

            function getJsonFromUrl() {
                var query = location.search.substr(1);
                var result = {};
                query.split("&").forEach(function(part) {
                    var item = part.split("=");
                    result[item[0]] = decodeURIComponent(item[1]);
                });
                return result;
            }

            url_json = getJsonFromUrl();
            $scope.search = url_json.searchterm;

            $scope.searchNetwork = function() {

                /*
                var query = {
                    'type': 'search',
                    'key': url_json.searchterm
                };
                $scope.searching = $scope.search;

                $scope.search_results = [];
                $scope.awaitingShop = $scope.search;
                Connection.send('search', query)
                $scope.search = ""
                $scope.showDashboardPanel('search');
                */
            };

            $scope.search_results = [];
            $scope.parse_search_result = function(msg) {
                console.log(msg);
                contract_data = msg.data;
                contract_data.key = msg.key;
                contract_data.rawContract = msg.rawContract;
                contract_data.nickname = msg.nickname;
                $scope.search_results.push(contract_data);
                $scope.search_results = jQuery.unique($scope.search_results);
                $.each($scope.search_results, function(index, contract) {
                    if (jQuery.isEmptyObject(contract.Contract.item_images)) {
                        console.log('empty object');
                        contract.Contract.item_images = "img/no-photo.png";
                    }
                });

                console.log('Search Results', $scope.search_results);

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };

            if (Connection.websocket.readyState == 1) {
                $scope.load_page({});
            }

        }
    ]);
