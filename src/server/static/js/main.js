$(document).ready(function() {
  var url = "http://" + document.domain + ":" + location.port;
  var socket = io.connect(url + "/");
  $("#cityform").submit(function(event) {
      socket.emit('city', {'city': $('#city').val()});
      $('#city').val('');
      return false;
  });
  socket.on('city', function(msg) {
      $("#cities-list").prepend('<li>' + msg.city + '</li>');
      console.log ('city event')
      console.log (msg);
  });
  socket.on('connect', function(){
      console.log ('CONNECTED')
  });
  socket.on('disconnect', function() {
      console.log ('DISCONNECTED')
  });
  socket.on('debug', function(msg) {
      console.log ('debug: ')
      console.log (msg);
  });
  window.socket = socket;

});