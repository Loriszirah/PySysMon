# PySysMon

[![Build Status](https://travis-ci.org/alexandrebouthinon/PySysMon.svg?branch=master)](https://travis-ci.org/alexandrebouthinon/PySysMon)

Application Linux client/serveur de monitoring et d'agrégation de logs en Python


## Prérequis : 

- Python 3.
- Node.js

## Installation et démarrage :
Lancez le programme serveur.py:

<code>python3.2 server.py</code>

Dans un autre terminal ou sur une autre machine lancez le programme agent.py :

<code>python3.2 agent.py</code>

Ensuite placez-vous dans le répertoire WebUI et lancez :

<code> npm install </code>

Enfin, pour finir,  toujours dans le répertoire WebUI, démarrez le serveur Node.js:

<code>node index.js</code>


Ouvrez votre navigateur et rendez-vous sur : http://localhost:8080 ( localhost ou l'IP du serveur )

## Fonctionnalités : 

- Interface Web (Node.js) pour la consultation des performances de chaque client (CPU et RAM) en temps réel.
- Un programme Agent (Python) à lancer sur chaque client.
- Un programme Serveur (Python) pour récupérer les données envoyées par les agents.
- Un script serveur (Node.js) à lancé sur le serveur pour avoir accés à l'interface web (par défaut : http://localhost:8080)

### Ajouts futurs :  

- Sauvegarde des logs.
- Gestions d'incidents permettant d'avoir un historique des pics de charge sur les clients.
- Authentification par compte et mot de passe afin d'accéder à l'interface web.


#### Auteur : 

Alexandre BOUTHINON  
