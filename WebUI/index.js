
var express = require('express');
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('server.sqlite3');
var app = express();
const idmachine;
app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));





const server = app.listen(8080, () => {
  console.log('listening on *:8080');
});
var io = require('socket.io')(server)

// Page d'acceuil

app.get('/', function(req, res, next) {

    res.render('acceuil', function(err, html){
        res.status(200).send(html);
    });
});

// Page Liste des Machines

function findAllMachine(req, res, next) {
    db.all("SELECT * FROM Machines ORDER BY IDMachine", function(err, row) {
        req.allmachine = row;
        return next();
    });
}

function renderAllMachine(req, res) {
    res.render('listemachine', { machines : req.allmachine });
}

app.get('/listemachines', findAllMachine, renderAllMachine);

// Page d'information sur une machine

function findMachine(req, res, next) {
    db.all("SELECT * FROM Machines WHERE IDMachine = ?", req.params.idmachine , function(err, row) {
        req.machine = row;
        return next();
    });
}

function findCpu(req, res, next) {
    db.all("SELECT * FROM Cpu WHERE IDMachine = ?", req.params.idmachine , function(err, row) {
        req.cpu = row;
        return next();
    });
}

function findRam(req, res, next) {
    db.all("SELECT * FROM Ram WHERE IDMachine = ?", req.params.idmachine , function(err, row) {
        req.ram = row;
        return next();
    });
}

function findSystem(req, res, next) {
    db.all("SELECT * FROM Systeme WHERE IDMachine = ?", req.params.idmachine , function(err, row) {
        req.sys = row;
        return next();
    });
}

function renderMachine(req, res) {
    res.render('infomachine', { cpu : req.cpu, ram : req.ram, system : req.sys, machine : req.machine });
}


app.get('/machines/:idmachine', findMachine, findCpu, findRam, findSystem, renderMachine);


io.sockets.on('connection', (socket) => {
    console.log('a user connected');
    function refreshCpu(idmachine) {
        db.all("SELECT * FROM Cpu WHERE IDMachine = ?", idmachine , function(err, row) {
            socket.emit('CPU', row[0].PercentCpu);
            return;
        });
    };
    function refreshRam(idmachine) {
        db.all("SELECT * FROM Ram WHERE IDMachine = ?", idmachine , function(err, row) {
            socket.emit('RAM', row[0].PercentRam);
            return;
        });
    };

    socket.on('sendID', function(datamachine) {
        refreshCpu(datamachine.idmachine);
        refreshRam(datamachine.idmachine);
    });


    socket.on('disconnect', () => {
        console.log('user disconnected');

    });
});
