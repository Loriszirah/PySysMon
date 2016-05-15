
var express = require('express');
var cookieParser = require('cookie-parser');
var pg = require('pg');
var bodyParser = require('body-parser');
var connectionString = "tcp://pysysmon:1234@localhost/pysysmon";
var client = new pg.Client(connectionString);
client.connect();
var app = express();
app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));
app.use(express.static(__dirname + '/views'));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(cookieParser("My cookieParser"));


const server = app.listen(8080, () => {
});

var io = require('socket.io')(server);


// Page d'acceuil

app.get('/', function(req, res, next) {
  client.query("SELECT COUNT (*) AS nb FROM Incidents WHERE Resolu = false",function(err, result) {
      if(err) {
        return console.error('error running query', err);
      }
      const nbincidents = result.rows[0].nb;
    res.render('acceuil', {nbincidents : nbincidents});
    });
});

app.get('/login', function(req,res,next){
  res.render('login');
});
// Page Liste des Machines
app.get('/listemachines', function(req, res, next) {
    var machines;
    client.query("SELECT * FROM Machines ORDER BY IDMachine", function(err, result) {
    if(err) {
      return console.error('error running query', err);
    }
    machines = result.rows;
    client.query("SELECT COUNT (*) AS nb FROM Incidents WHERE Resolu = false",function(err, result) {
        if(err) {
          return console.error('error running query', err);
        }
        const nbincidents = result.rows[0].nb;
    res.render('listemachine', { machines : machines, nbincidents : nbincidents, success:true});

    });
  });
});

app.get('/searchmachine', function(req,res,next){
  if(req.query.success == 'true'){
    res.render("listemachine",{machines : req.query.machines, nbincidents: req.query.nbincidents, success:true});
  } else if(req.query.success == 'false'){
    res.render("listemachine",{machines : req.query.machines, nbincidents: req.query.nbincidents, success:false});
  }
});

app.get('/searchincidents', function(req,res,next){
  if(req.query.success == 'true'){
    res.render("incidents",{incidents : req.query.incidents, nbincidents: req.query.nbincidents, success:true});
  } else if(req.query.success == 'false'){
    res.render("incidents",{incidents : req.query.incidents, nbincidents: req.query.nbincidents, success:false});
  }
});

// Page Liste des Machines
app.get('/incidents', function(req, res, next) {
    var incidents;
    client.query("SELECT * FROM Incidents ORDER BY IDIncident", function(err, result) {
    if(err) {
      return console.error('error running query', err);
    }
    incidents = result.rows;
    client.query("SELECT COUNT (*) AS nb FROM Incidents WHERE Resolu = false",function(err, result) {
        if(err) {
          return console.error('error running query', err);
        }
        const nbincidents = result.rows[0].nb;
        res.render('incidents', { incidents : incidents, nbincidents : nbincidents, success:true});

    });
  });
});



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
                    client.query("SELECT COUNT (*) AS nb FROM Incidents WHERE Resolu = false",function(err, result) {
                        if(err) {
                          return console.error('error running query', err);
                        }
                        const nbincidents = result.rows[0].nb;
                        if(typeof(machine[0]) == 'undefined'){
                          res.status(404);
                          res.render('404', {nbincidents : nbincidents});
                        }
                        else{
                          res.status(200);
                          res.render('infomachine', { machine : machine, cpu : cpu, ram : ram, system : system, nbincidents : nbincidents});

                        }
                  });
                });
            });
        });
    });
});




// Temps réel pour le rafraichissement des informations sur les machines
io.sockets.on('connection', (socket) => {
  // Recherche de machine



    socket.on('sendID', function(datamachine) {
        var ram, cpu , uptime;
        client.query("SELECT PercentRam FROM Ram WHERE IDMachine=$1",[datamachine.idmachine], function(err, result) {
            if(err) {
              return console.error('error running query', err);
            }
            ram = result.rows[0].percentram;

            client.query("SELECT PercentCpu FROM Cpu WHERE IDMachine=$1",[datamachine.idmachine], function(err, result) {
                if(err) {
                  return console.error('error running query', err);
                }
                cpu = result.rows[0].percentcpu;
                client.query("SELECT Uptime FROM Systeme WHERE IDMachine=$1",[datamachine.idmachine], function(err, result) {
                    if(err) {
                      return console.error('error running query', err);
                    }
                    uptime = result.rows[0].uptime;
                    var infos = {Cpu : cpu, Ram : ram, Uptime : uptime};
                    socket.emit('Infos', infos);
                });
            });
        });
      });
      socket.on('suppr', function(idmachine){
        client.query("DELETE FROM Machines WHERE IDMachine=$1",[idmachine], function(err, result) {
            if(err) {
              return console.error('error running query', err);
            }
        });

    });
    socket.on('searchmachine', function(data){
      client.query('SELECT * from Machines where nommachine like $1',['%' + data.data + '%'], function(err , result) {
          if(err) {
            return console.error('error running query', err);
          }
          var machines = result.rows;
          client.query("SELECT COUNT (*) AS nb FROM Incidents WHERE Resolu = false",function(err, result) {
              if(err) {
                return console.error('error running query', err);
              }
              const nbincidents = result.rows[0].nb;
              if(typeof(machines[0]) == 'object'){
                var newInfos =  { machines : machines, nbincidents : nbincidents, success:true};
              }else if(typeof(machines[0]) == 'undefined'){
                var newInfos =  { machines : machines, nbincidents : nbincidents, success:false};
              }
              socket.emit('searchResmachine', newInfos);


          });
         });
    })
    socket.on('searchincidents', function(data){
      client.query('SELECT * from Incidents where hote like $1',['%' + data.data + '%'], function(err , result) {
          if(err) {
            return console.error('error running query', err);
          }
          var incidents = result.rows;
          client.query("SELECT COUNT (*) AS nb FROM Incidents WHERE Resolu = false",function(err, result) {
              if(err) {
                return console.error('error running query', err);
              }
              const nbincidents = result.rows[0].nb;
              if(typeof(incidents[0]) == 'object'){
                var newInfos =  { incidents : incidents, nbincidents : nbincidents, success:true};
              }else if(typeof(incidents[0]) == 'undefined'){
                var newInfos =  { incidents : incidents, nbincidents : nbincidents, success:false};
              }
              socket.emit('searchResincidents', newInfos);


          });
         });
    })
    socket.on('disconnect', () => {

    });
  });
