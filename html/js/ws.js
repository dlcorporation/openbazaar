function Connection(onMessage) {

  socket_uri = document.URL.replace(/https?:(.*)\/html\/.*/, "ws:$1/ws");
  var websocket = new WebSocket(socket_uri);

  websocket.onopen = function(evt) {
    self.websocket.send(JSON.stringify({"id":42, "command":"load_page", "params":{}}))
    self.websocket.send(JSON.stringify({"id":42, "command":"check_order_count", "params":{}}))
    //self.websocket.send(JSON.stringify({"id":42, "command":"read_log", "params":{}}))
  }

  websocket.onclose = function(evt) {
   console.log("closed", evt)
   console.log('The websocket closed unexpectedly. Refreshing.');
   window.location.reload()
  }

  websocket.onerror = function(evt) {
   console.log("error", evt)
  }

  websocket.onmessage = function(evt) {
   	var data = JSON.parse(evt.data)
    onMessage(data.result)
  }
  this.websocket = websocket;
  var self = this;

  this.send = function(command, msg) {
     var request = {
        "id": 42,
        "command": command,
        "params": msg
    };

    var message = JSON.stringify(request);    
    self.websocket.send(message);

  }


}
