angular.module('app')
  .service('Connection', ['$rootScope', function($rootScope){
    var Connection = function(onMessage) {
      socket_uri = document.URL.replace(/https?:(.*)\/html\/.*/, "ws:$1/ws");
      var websocket = new WebSocket(socket_uri);

      websocket.onopen = function(evt) {
        self.websocket.send(JSON.stringify({"id":42, "command":"load_page", "params":{}}));
        self.websocket.send(JSON.stringify({"id":42, "command":"check_order_count", "params":{}}));
        //self.websocket.send(JSON.stringify({"id":42, "command":"read_log", "params":{}}));
      };

      websocket.onclose = function(evt) {
       console.log("closed", evt);
       console.log('The websocket closed unexpectedly. Refreshing.');
       window.location.reload();
      };

      websocket.onerror = function(evt) {
       console.log("error", evt);
      };

      websocket.onmessage = function(evt) {
        var data = JSON.parse(evt.data);
        //console.log("Websocket.onMessage!");
        //console.log(data);
        onMessage(data.result);
      };
      this.websocket = websocket;
      var self = this;

      this.send = function(command, msg) {
       if (msg === undefined) {
         msg = {};
       }
       
         var request = {
            "id": 42,
            "command": command,
            "params": msg
        };

        var message = JSON.stringify(request);
        //console.log('Connection.send ->')
        //console.log(message)
        self.websocket.send(message);
      };
    };

    var scope = $rootScope.$new(true);

    var socket = new Connection(function(data){
      scope.$emit('message', data);
      if (typeof data == 'object' && typeof data.type == 'string') {
        scope.$emit(data.type, data);
      }
    });

    scope.send = socket.send;
    scope.websocket = socket.websocket;

    return scope;
  }]);
