
var express = require('express');
var pg = require('pg');
var connectionString = "tcp://pysysmon:1234@localhost/pysysmon"
var client = new pg.Client(connectionString);
client.connect();
var app = express();
const idmachine;
app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));





const server = app.listen(8080, () => {
});

var io = require('socket.io')(server)

// Page d'acceuil

app.get('/', function(req, res, next) {

    res.render('acceuil', function(err, html){
        res.status(200).send(html);
    });
});

// Page Liste des Machines
app.get('/listemachines', function(req, res, next) {
    var machines;
    client.query("SELECT * FROM Machines ORDER BY IDMachine", function(err, result) {
    if(err) {
      return console.error('error running query', err);
    }
    machines = result.rows;
    res.render('listemachine', { machines : machines});

    });

});

// Page Liste des Machines
app.get('/incidents', function(req, res, next) {
    var incidents;
    client.query("SELECT * FROM Incidents ORDER BY IDIncident", function(err, result) {
    if(err) {
      return console.error('error running query', err);
    }
    incidents = result.rows;
    res.render('incidents', { incidents : incidents});

    });

});


// Page d'information sur une machine
app.get('/machines/:idmachine', function(req, res, next) {

    client.query("SELECT * FROM Machines WHERE IDMachine=$1",req.params.idmachine, function(err, result) {
        if(err) {
          return console.error('error running query', err);
        }
        const machine = result.rows;
        client.query("SELECT * FROM Cpu WHERE IDMachine=$1",req.params.idmachine, function(err, result) {
            if(err) {
              return console.error('error running query', err);
            }
            const cpu = result.rows;
            client.query("SELECT * FROM Ram WHERE IDMachine=$1",req.params.idmachine, function(err, result) {
                if(err) {
                  return console.error('error running query', err);
                }
                const ram = result.rows;
                client.query("SELECT * FROM Systeme WHERE IDMachine=$1",req.params.idmachine, function(err, result) {
                    if(err) {
                      return console.error('error running query', err);
                    }
                    const system = result.rows;
                    res.render('infomachine', { machine : machine, cpu : cpu, ram : ram, system : system});
                });
            });
        });
    });
});


// Temps réel pour le rafraichissement des informations sur les machines
io.sockets.on('connection', (socket) => {



    socket.on('sendID', function(datamachine) {

        client.query("SELECT PercentRam FROM Ram WHERE IDMachine=$1",[datamachine.idmachine], function(err, result) {
            if(err) {
              return console.error('error running query', err);
            }
            socket.emit('RAM', result.rows[0].percentram);

            client.query("SELECT PercentCpu FROM Cpu WHERE IDMachine=$1",[datamachine.idmachine], function(err, result) {
                if(err) {
                  return console.error('error running query', err);
                }
                socket.emit('CPU', result.rows[0].percentcpu);
                client.query("SELECT Uptime FROM Systeme WHERE IDMachine=$1",[datamachine.idmachine], function(err, result) {
                    if(err) {
                      return console.error('error running query', err);
                    }
                    socket.emit('Uptime', result.rows[0].uptime);
                });
            });
        });
    });


    socket.on('disconnect', () => {

    });
});
