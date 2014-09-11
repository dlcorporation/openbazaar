/**
 * Settings controller.
 *
 * @desc This controller is the settings controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
angular.module('app')
    .controller('Settings', ['$scope', '$interval', '$routeParams', '$location', 'Connection', '$route',
        function($scope, $interval, $routeParams, $location, Connection, $route) {

            $scope.settingsPanel = true;
            $scope.path = $location.path();
            $('#keys-form').siblings().hide();
            $scope.$emit('sidebar', false);


            /**
             * (These are response handlers when the server talks back to the websocket)
             * Establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            Connection.$on('load_page', function(e, msg){ $scope.load_page(msg); });
            Connection.$on('settings_notaries', function(e, msg){ $scope.parse_notaries(msg); });
            Connection.$on('create_backup_result', function(e, msg){ $scope.onCreateBackupResult(msg); });
            Connection.$on('on_get_backups_response', function(e, msg){ $scope.onGetBackupsResponse(msg); });

            $scope.load_page = function(msg) {
                console.log($scope.path);
                $('#dashboard-container').removeClass('col-sm-8').addClass('col-sm-12');

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
                        $scope.getNotaries();
                        break;
                    case "/settings/advanced":
                        $('#advanced-form').show();
                        $('#advanced-form').siblings().hide();
                        $('#settings-advanced').addClass('active');
                        break;
                    case "/settings/backup":
                      $('#backup-form').show();
                      $('#backup-form').siblings().hide();
                      $('#settings-backup').addClass('active');
                      $scope.getBackups();
                      break;
                    default:
                        $('#profile-form').show();
                        $('#profile-form').siblings().hide();
                        $('#settings-storeinfo').addClass('active');
                        break;
                }

            };

            $scope.addNotary = function(notary) {
                var notaryGUID = (notary !== '') ? notary : $scope.newNotary;
                $scope.newNotary = '';

                if(notaryGUID.length != 40 || !notaryGUID.match(/^[0-9a-z]+$/)) {
                    alert('Incorrect format for GUID');
                    return;
                }

                Connection.send('add_trusted_notary', { 'type': 'add_trusted_notary',
                    'guid': notaryGUID,
                    'nickname': ''
                    }
                );

                Notifier.success('Success', 'Notary added successfully.');

                if (!$scope.$$phase) {
                    $scope.$apply();
                }

            };

            $scope.stopServer = function() {
                Connection.send('stop_server', { 'type': 'stop_server' });
            };

            $scope.removeNotary = function(notaryGUID) {

                $('#notary_'+notaryGUID).parent().hide();
                Connection.send('remove_trusted_notary', { 'type': 'remove_trusted_notary',
                    'guid': notaryGUID
                    }
                );

                Notifier.success('Success', 'Notary removed successfully.');

                $scope.getNotaries();

                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };

            $scope.getNotaries = function() {
                console.log('Getting notaries');
                Connection.send('get_notaries', {});
            };

            $scope.generateNewSecret = function(e) {
                if (e) {
                    e.preventDefault();
                }

                var query = {
                    'type': 'generate_secret'
                };
                console.log('Generating new secret key');
                Connection.send('generate_secret', query);
                console.log($scope.myself.settings);

            };

            /**
             * Load notaries array into the GUI
             * @msg - Message from server
             */
            $scope.parse_notaries = function(msg) {
                console.log('Parsing notaries');
                $scope.settings.notaries = msg.notaries;
                console.log(msg.notaries);
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            };
            
            $scope.createBackup = function() {
              Connection.send('create_backup',{});
            };
            
            $scope.onCreateBackupResult = function(msg) {
              if (msg.result) {
                if (msg.result === 'success') {
                  Notifier.success('Success','The backup was created successfully at ' + msg.detail);
                } else if (msg.result === 'failure') {
                  Notifier.error(msg.detail,'Couldn\'t create backup.');
                }
              }
            };
            
            $scope.getBackups = function() {
              //console.log("executing getBackups()!")
              Connection.send('get_backups');
            };
            
            $scope.onGetBackupsResponse = function (msg) {
              //console.log("executing onGetBackupsResponse!")
              if (msg.result === 'success') {
                //update UI with list of backups. (could be empty list)
                if (msg.backups) {
                  $scope.backups = [];
                  //convert list of json objects into JS objects.
                  for (var i=0; i < msg.backups.length; i++) {
                    $scope.backups[i] = $.parseJSON(msg.backups[i]);
                  }
                  if (!$scope.$$phase) {
                    $scope.$apply();
                  }
                }
              } else if (msg.result === 'failure') {
                //console.log('onGetBackupsResponse: failure')
                Notifier.error(msg.detail, 'Could not fetch list of backups, check your backup folder');
              }
            };

            $scope.load_page({});

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
        }
    ]);
