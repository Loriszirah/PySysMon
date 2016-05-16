
var express = require('express');
var cookieParser = require('cookie-parser');
var uuid = require('node-uuid');
var pg = require('pg');
var bodyParser = require('body-parser');
var connectionString = "tcp://pysysmon:1234@localhost/pysysmon";
var passwordHash = require('password-hash');
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

function FirstLaunch(){
 /* Création de la table des Administrateur et création de l'utilisateur par défaut avec password crypté
    si aucun utilisateur n'existe */
  var hashedPassword = passwordHash.generate('admin');

  client.query("CREATE TABLE IF NOT EXISTS Administration(IDUser SERIAL PRIMARY KEY,Username TEXT,Password TEXT)");
  client.query("SELECT COUNT(*) AS exist FROM Administration", function(err,result){

      if(result.rows[0].exist == 0){
        client.query("INSERT INTO Administration(Username, Password) VALUES('admin', $1)", [hashedPassword], function(err, result){
          if(err){
            console.log(err);
          }
        });
      }
  });

}

FirstLaunch();


// Page d'acceuil
app.get('*',function(req,res,next){

  if (req.url === '/login') return next();
  if(req.cookies.admin == undefined || req.cookies.admin == 'undefined'){
      res.redirect("/login");


}
    else {
      return next();
    }


});
app.get('/', function(req, res, next) {
    client.query("SELECT COUNT (*) AS nb FROM Incidents WHERE Resolu = false",function(err, result) {
        if(err) {
          return console.error('error running query', err);
        }
        const nbincidents = result.rows[0].nb;
      res.status(200);
      res.render('acceuil', {nbincidents : nbincidents});
      });

});

app.get('/login', function(req,res,next){

  res.status(200);
  res.render('login', {success: null});
});

app.post('/login', function(req,res,next){

  client.query("SELECT Password AS passwd FROM Administration WHERE Username=$1",[req.body.username], function(err,result){
    if(typeof(result.rows[0]) == 'undefined'){
      res.render("login",{success : 'unknowed'});
      res.end();
    }
    else{

      var passwdSHA = result.rows[0].passwd;
      var checkPasswd = passwordHash.verify(req.body.password,passwdSHA);

      if(checkPasswd == false){
        res.render("login", {success: false});
        res.end();
      }
      if(checkPasswd == true){
        var rValue = uuid.v4(); // generation de données aléatoires et uniques
        res.status(201);
        res.cookie('admin' , rValue, {expire : new Date() + 60000});
        res.end();



      }

    }
  });

});

app.get("/logout", function(req,res,next){
  res.clearCookie('admin');
  res.redirect("/login");

})

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
        res.status(200);
        res.render('listemachine', { machines : machines, nbincidents : nbincidents, success:true});

        io.sockets.on('connection', (socket) => {
            socket.setMaxListeners(20);
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

            });

        });

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
        res.status(200);

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

                          /* Puis ecoute des requetes sur les websockets */
                          io.sockets.on('connection', (socket) => {
                            socket.setMaxListeners(20);
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
                        socket.on('disconnect', () => {

                        });
                      });

                      }
                  });
                });
            });
        });
    });
});
