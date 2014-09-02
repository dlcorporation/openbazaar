/**
 * Contracts controller.
 *
 * @desc This controller is the contracts controller.
 * @param {!angular.Scope} $scope
 * @constructor
 */
angular.module('app')
    .controller('Contracts', ['$scope', '$interval', '$routeParams', '$location', 'Connection',
        function($scope, $interval, $routeParams, $location, Connection) {

            $scope.contractsPanel = true;
            $scope.path = $location.path();
            $scope.$emit('sidebar', false);


            /**
             * Establish message handlers
             * @msg - message from websocket to pass on to handler
             */
            Connection.$on('load_page', function(e, msg){ $scope.load_page(msg) });
            Connection.$on('contracts', function(e, msg){ $scope.parse_contracts(msg) });

            $scope.load_page = function(msg) {
                console.log($scope.path);
                    $scope.sidebar = false;
                    $scope.queryContracts();

            }

            $scope.queryContracts = function() {
                var query = { 'type': 'query_contracts' }
                Connection.send('query_contracts', query)
            }

            $scope.removeContract = function(contract_id) {
                $('#contract-row-'+contract_id).fadeOut({ "duration": 1000 });
                Connection.send("remove_contract", {
                    "contract_id": contract_id
                });
                Connection.send("query_contracts", {})
            }

            $scope.republishContracts = function() {
                Connection.send("republish_contracts", {});
                Connection.send("query_contracts", {})
            }

            $scope.ProductModal = function($scope, $modal, $log) {

                $scope.contracts_page_changed = function() {
                    console.log($scope.contracts_current_page)
                    var query = {
                        'page': $scope.contracts_current_page - 1
                    }
                    console.log(query)
                    Connection.send('query_contracts', query)

                }

                $scope.open = function(size, backdrop) {

                    backdrop = backdrop ? backdrop : true;

                    var modalInstance = $modal.open({
                        templateUrl: 'partials/modal/addContract.html',
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

                        Connection.send("import_raw_contract", {
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
                                    Connection.send("create_contract", contract);
                                    Notifier.success('Success', 'Contract saved successfully.');
                                    Connection.send("query_contracts", {})


                                }
                                r.readAsArrayBuffer(imgUpload);


                            } else {

                                console.log(contract);
                                Connection.send("create_contract", contract);
                                Notifier.success('Success', 'Contract saved successfully.');
                                Connection.send("query_contracts", {})

                            }

                        } else {
                            console.log(contract);
                            Connection.send("create_contract", contract);

                            Connection.send("query_contracts", {})

                        }
                    }
                    $modalInstance.dismiss('cancel');
                }

                $scope.cancel = function() {
                    Connection.send("query_contracts", {});
                    $modalInstance.dismiss('cancel');
                };

                $scope.toggleItemAdvanced = function() {
                    $scope.itemAdvancedDetails = ($scope.itemAdvancedDetails) ? 0 : 1;
                }

                $scope.load_page({});
            };

        }
    ]);
