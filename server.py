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

        if isinstance(data, dict) and data != "":
            data["Client"]["IP"] = self.address

            # Connection à la base de données #
            db = 'server.db'

            # Ecriture des données dans la base de données #
            SqlSave(data, db)

        else:
            return

###
# Ecriture dans la base de données
###

def SqlSave(data, db):
    """ Ecriture des informations dans la base de données """

    sql = SqlAccess(db)
    sql.execute("""CREATE TABLE IF NOT EXISTS Machines(
                    IDMachine INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    NomMachine TEXT,
                    IPMachine TEXT,
                    Load TEXT,
                    Uptime TEXT)""", ())
    client = data.get("Client")
    nom = client.get("Hostname")
    IP = client.get("IP")
    Load = client.get("Load")
    Uptime = client.get("Uptime")
    sql.execute("INSERT INTO Machines(NomMachine, IPMachine, Load, Uptime) VALUES(?,?,?,?)", (nom,IP,Load,Uptime))

    for v, w, x, y, z in sql.select("""SELECT * FROM Machines ORDER BY IDMachine DESC LIMIT 1 """):
        print(v, w, x, y, z)

    sql.close()

    return



###
# Thread d'accés à la base de données
###

class SqlAccess(Thread):
    def __init__(self, db):
        Thread.__init__(self)
        self.db=db
        self.reqs=Queue()
        self.start()
    def run(self):
        conn = apsw.Connection(self.db)
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


def main():
    """ Programme principal """


    while (1):
        s.listen(10)

        client, (address, port) = s.accept()
        threadClient = ConnexionClient(client, address)
        threadClient.start()

if __name__ == '__main__':
    main()
