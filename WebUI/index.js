
var express = require('express');
var sqlite3 = require('sqlite3').verbose();
var util = require('util');

var db = new sqlite3.Database('server.sqlite3');
var app = express();
var machine;

app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));


app.get('/', function(req, res, next) {
    db.all("SELECT * FROM Machines ORDER BY IDMachine", function(err, row) {
        if(err != null) {
            next(err);
        }
        else{
            res.render('index', { machines : row }, function(err, html){
                res.status(200).send(html);
            });
        }
    });
});



app.listen(8080);
console.log('Démarrage de Pysysmon WebUI');
