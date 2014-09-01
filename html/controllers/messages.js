/**
 * Messages controller.
 *
 * @desc This controller is the messages controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
angular.module('app')
    .controller('Messages', ['$scope', '$interval', '$routeParams', '$location', 'Connection',
        function($scope, $interval, $routeParams, $location, Connection) {

            $scope.myOrders = []
            $scope.ordersPanel = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', false);

            /**
             * Establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            Connection.$on('load_page', function(e, msg){ $scope.load_page(msg) });
            Connection.$on('messages', function(e, msg){ $scope.parse_messages(msg) });

            $scope.load_page = function(msg) {
                $scope.messagesPanel = true;
                $scope.queryMessages();
            }


            $scope.queryMessages = function() {
                // Query for messages
                var query = {
                    'type': 'query_messages'
                }
                console.log('querying messages')
                Connection.send('query_messages', query)
                console.log($scope.myself.messages)

            }

            $scope.message = {};
            $scope.parse_messages = function(msg) {
                console.log('parsing messages',msg);
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

        }
    ]);
