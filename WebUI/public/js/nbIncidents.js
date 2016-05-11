var socket = io();
var i = 0;
var socket = io.connect();

setInterval(UpdateIncident, 1000);
function UpdateIncident(){
  socket.emit('sendNbIncidents');
  socket.on('NbIncidents', function(data){
    if(data != 0){
        document.getElementById("nbincidents").innerHTML= "<a href=\"/incidents\">Incidents <span class=\"badge\">" + data + "</span></a>";
    }
});
