
var express = require('express');
var sqlite3 = require('sqlite3').verbose();
var util = require('util');

var db = new sqlite3.Database('server.sqlite3');
var app = express();
var machine;

app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));


app.get('/', function(req, res, next) {

    res.render('acceuil', function(err, html){
        res.status(200).send(html);
    });
});

app.get('/machines', function(req, res, next) {
    db.all("SELECT * FROM Machines ORDER BY IDMachine", function(err, row) {
        if(err != null) {
            next(err);
        }
        else{
            res.render('machine', { machines : row }, function(err, html){
                res.status(200).send(html);
            });
        }
    });
});

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

app.get('/:idmachine', findMachine, findCpu, findRam, findSystem, renderMachine);


app.listen(8080);
console.log('Démarrage de Pysysmon WebUI');
