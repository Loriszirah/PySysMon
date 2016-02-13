#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, pickle, sqlite3, apsw
from queue import Queue
from threading import Thread

                                ###                ###
                                # Variables globales #
                                ###                ###

# Information du serveur #
port = 50000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 50000))
# Chemin vers la base de données #
db = 'server.db'





                ###                                                                   ###
                #   Programme serveur stockant les informations des clients dans une BD #
                ###                                                                   ###


###
# Connexion Client
###


class ConnexionClient(Thread):
    """ Thread de récupération des informations sur le CPU """

    def __init__(self, socket, address):
        Thread.__init__(self)
        self.address = address
        self.socket = socket

    def run(self):
        """ Tâches à effectuer pour chaque client"""

        response = self.socket.recv(512)
        data = pickle.loads(response)

        if isinstance(data, dict):
            data["Client"]["IP"] = self.address

            res = SqlMachineExist(db, self.address)
            print(res)
            # Ecriture des données dans la base de données #
                #SqlAddMachine(data, db)
            #else:
                #print("Machine déjà sauvegardé")

        else:
            return




###
# Thread d'accés à la base de données
###

class SqlAccess(Thread):
    def __init__(self, database):
        Thread.__init__(self)
        self.database=database
        self.reqs=Queue()
        self.start()
    def run(self):
        conn = apsw.Connection(self.database)
        cursor = conn.cursor()
        while True:
            req, arg, res = self.reqs.get()
            if req=='--close--': break
            cursor.execute(req, arg)
            if res:
                for rec in cursor:
                    res.put(rec)
                res.put('--no more--')
        conn.close()
    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))
    def select(self, req, arg=None):
        res=Queue()
        self.execute(req, arg, res)
        while True:
            rec=res.get()
            if rec=='--no more--': break
            yield rec
    def close(self):
        self.execute('--close--')


###
# Création des tables
###

def SqlTables(database):
    """ Création des tables au lancement du programme """

    sql = SqlAccess(database)

    # Table des Machines #
    sql.execute("""CREATE TABLE IF NOT EXISTS Machines(
                    IDMachine INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    NomMachine TEXT,
                    IPMachine TEXT,
                    Load TEXT,
                    Uptime TEXT)""", ())

    # Table des informations CPU #
    sql.execute("""CREATE TABLE IF NOT EXISTS Cpu(
                    IDCpuInfo INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    ModelCpu TEXT,
                    FrequencyCpu TEXT,
                    NbCore TEXT,
                    NbThread TEXT,
                    PercentCpu TEXT)""", ())

    # Table des informations RAM #
    sql.execute("""CREATE TABLE IF NOT EXISTS Ram(
                    IDRam INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    TotalRam TEXT,
                    UseRam TEXT,
                    PercentRam TEXT)""", ())

    sql.close()


###
# Ecriture dans la base de données
###

def SqlAddMachine(data, database):
    """ Ecriture des informations dans la base de données """

    sql = SqlAccess(database)


    client = data.get("Client")
    nom = client.get("Hostname")
    IP = client.get("IP")
    Load = client.get("Load")
    Uptime = client.get("Uptime")
    sql.execute("INSERT INTO Machines(NomMachine, IPMachine, Load, Uptime) VALUES(?,?,?,?)", (nom,IP,Load,Uptime))

    machine = sql.select("""SELECT * FROM Machines ORDER BY IDMachine DESC LIMIT 1 """)
    print(list(machine))

    sql.close()

    return

###
# Test l'existance d'une machine dans la table Machines
###

def SqlMachineExist(database, IP):
    """ Test de présence d'une machine dans la table grâce à son IP """

    sql = SqlAccess(database)

    res = sql.select("SELECT * FROM Machines WHERE IPMachine = ?", (IP,))

    sql.close()

    print(str(list(res)))
    if list(res) != None:
        return 0
    else:
        return 1


def main():
    """ Programme principal """

    SqlTables(db)

    while (1):
        s.listen(10)

        client, (address, port) = s.accept()
        threadClient = ConnexionClient(client, address)
        threadClient.start()

if __name__ == '__main__':
    main()
