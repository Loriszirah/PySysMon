# PySysMon

[![Build Status](https://travis-ci.org/alexandrebouthinon/PySysMon.svg?branch=master)](https://travis-ci.org/alexandrebouthinon/PySysMon)

Application Linux client/serveur de monitoring et d'agrégation de logs en Python avec interface Web Node.js.


## Prérequis :

- Python 3.
- Node.js

## Installation et démarrage :

### Installation des dépendances :

Installez les modules python psutil et bitmath sur les machines à surveiller:

<code>pip install psutil bitmath</code>

Installez ensuite sur le serveur le module psycopg2:

<code>pip install psycopg2</code>

### Installation et configuration de la base de données Postgresql :

**Installation :**

Installez le paquet Postgresql sur votre distribution :

*Par exemple pour ArchLinux :*

<code>yaourt -S postgresql</code>

*Par exemple pour Ubuntu / Debian  :*

<code> apt-get install postgresql</code>

...

**Configuration :**

Connectez-vous au compte Unix de postgres :

<code>su - postgres</code>

Créez l'utilisateur "pysysmon" :

<code>createuser pysysmon -W</code>

Créez la base de données "pysysmon" et ajoutez l'utilisateur "pysysmon" aux "Owners" :

<code>createdb -O pysysmon pysysmon</code>

Pour finir ouvrez le fichier index.js dans le répertoire WebUI, et modifié la ligne :

<code>var connectionString = "tcp://pysysmon:1234@localhost/pysysmon"
</code>

par :

<code>var connectionString = "tcp://pysysmon:motdepassedepysysmon@localhost/pysysmon"
</code>

Il ne reste plus qu'à démarré le service Postgresql :

<code>systemctl start postgresql.service</code>

ou

<code>service start postgresql</code>

### Démarrage des daemons :

Lancez le programme serveur.py:

<code>python3.2 server.py</code>

Dans un autre terminal ou sur une autre machine lancez le programme agent.py :

<code>python3.2 agent.py</code>

*P.S. : Utilisez toujours la dernière version de Python 3 disponible sur votre distribution*

### Installation des modules Node.js :

Ensuite placez-vous dans le répertoire WebUI et lancez :

<code> npm install </code>


### Démarrage de l'interface Web :

Enfin, pour finir,  toujours dans le répertoire WebUI, démarrez le serveur Node.js:

<code>node index.js</code>


Ouvrez votre navigateur et rendez-vous sur : http://localhost:8080 ( localhost ou l'IP du serveur )

## Fonctionnalités :

- Interface Web (Node.js) pour la consultation des performances de chaque client (CPU et RAM) en temps réel.
- Un programme Agent (Python) à lancer sur chaque client.
- Un programme Serveur (Python) pour récupérer les données envoyées par les agents.
- Un script serveur (Node.js) à lancé sur le serveur pour avoir accés à l'interface web (par défaut : http://localhost:8080)
- Gestion d'incidents permettant d'avoir un historique des pics de charge et des excés de consommation RAM sur les clients.


## Ajouts futurs :  

- Sauvegarde des logs.
- Authentification par compte et mot de passe afin d'accéder à l'interface web.


## Auteur :

Alexandre BOUTHINON  
