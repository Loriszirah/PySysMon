#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, pickle, sqlite3, time, hashlib, sys ,os
from queue import Queue
from threading import Thread

                                ###                ###
                                # Variables globales #
                                ###                ###

# Information du serveur #
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 50000))
# Chemin vers la base de données #
db = 'server.db'

# Connexion à la base de données #
conn = sqlite3.connect(db , check_same_thread = False )
conn.execute('pragma foreign_keys = on')
conn.commit()
cur = conn.cursor()

# Mot de passe de sécurité #
passwd = "test"



                ###                                                                   ###
                #   Programme serveur stockant les informations des clients dans une BD #
                ###                                                                   ###



                                ###                            ###
                                # Actions sur la base de données #
                                ###                            ###





###
# Création des tables
###

def SqlTables():
    """ Création des tables au lancement du programme """



    # Table de Stagging #
    cur.execute("""CREATE TABLE IF NOT EXISTS Stage(
                    IDMachine INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    NomMachine TEXT,
                    IPMachine TEXT)""", ())

    # Table des Machines #
    cur.execute("""CREATE TABLE IF NOT EXISTS Machines(
                    IDMachine INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    NomMachine TEXT,
                    IPMachine TEXT)""", ())

    # Table des informations CPU #
    cur.execute("""CREATE TABLE IF NOT EXISTS Cpu(
                    IDCpuInfo INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    ModelCpu TEXT,
                    FrequencyCpu TEXT,
                    NbCore TEXT,
                    NbThread TEXT,
                    PercentCpu TEXT,
                    Machine TEXT)""", ())

    # Table des informations RAM #
    cur.execute("""CREATE TABLE IF NOT EXISTS Ram(
                    IDRam INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    TotalRam TEXT,
                    UseRam TEXT,
                    PercentRam TEXT,
                    Machine TEXT)""", ())

    # Table des informations Systeme #
    cur.execute("""CREATE TABLE IF NOT EXISTS Systeme(
                    IDSysteme INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    Uptime TEXT,
                    Load TEXT,
                    Machine TEXT)""", ())


    conn.commit()

    return

###
# Enregistrement du client dans la zone de stagging
###

def SqlAddToStage(data):
    """ Ecriture des informations dans la base de données """

    client = data.get("Client")
    nom = client.get("Hostname")
    IP = client.get("IP")

    cur.execute("INSERT INTO Stage(NomMachine, IPMachine) VALUES(?,?)", (nom,IP,))

    conn.commit()

    return

###
# Test l'existance d'une machine dans la table Machines
###

def SqlIsInStage(IP):
    """ Test de présence d'une machine dans la table grâce à son IP """

    res = list(cur.execute("SELECT * FROM Stage WHERE IPMachine = ?", (IP,)))


    if bool(res) != False:
        return 0
    else:
        return 1


###
# Test l'existance d'une machine dans la table Machines
###

def SqlMachineExist(IP):
    """ Test de présence d'une machine dans la table grâce à son IP """

    res = list(cur.execute("SELECT * FROM Machines WHERE IPMachine = ?", (IP,)))


    if bool(res) != False:
        return 0
    else:
        return 1


###
# Ecriture dans la base de données
###

def SqlAddMachine(data):
    """ Ecriture des informations dans la base de données """



    client = data.get("Client")
    nom = client.get("Hostname")
    IP = client.get("IP")

    # On supprime le client de la stagging area #
    cur.execute("""DELETE FROM Stage WHERE IPMachine = ?""",(IP,))

    cur.execute("INSERT OR REPLACE INTO  Machines(NomMachine, IPMachine) VALUES(?,?)", (nom,IP,))

    conn.commit()

    return

###
# Mise à jour des informations d'une machine existante
###

def SqlSaveInfos(data):
    """ Ecriture des informations dans la base de données """

    # Récupération de l'IP du clinet pour lier les informations stockées à sa machine #
    IP = data.get("IP")

    nomMachine = cur.execute("""SELECT NomMachine FROM Machines WHERE IPMachine =?""", (IP,))
    nom = list(nomMachine)
    nomMachine = nom[0][0]

    # Ajout des informations Cpu #
    Cpu = data.get("CPU")
    model = Cpu.get("Model")
    frequency = Cpu.get("Frequency")
    core = Cpu.get("Core")
    thread = Cpu.get("Thread")
    percent = Cpu.get("Percent")

    cur.execute("INSERT INTO Cpu(ModelCpu, FrequencyCpu, NbCore, NbThread, PercentCpu, Machine) VALUES(?,?,?,?,?,?)", (model,frequency,core,thread,percent,str(nomMachine),))

    conn.commit()

    # Ajout des informations Ram #

    Ram = data.get("RAM")
    total = Ram.get("Total")
    use = Ram.get("Use")
    percent = Ram.get("Percent")

    cur.execute("INSERT INTO Ram(TotalRam, UseRam, PercentRam, Machine) VALUES(?,?,?,?)", (total, use,percent,str(nomMachine),))

    conn.commit()

    # Ajout des informations Systeme #

    System = data.get("System")
    uptime = System.get("Uptime")
    load = System.get("Load")

    cur.execute("INSERT INTO Systeme(Uptime, Load, Machine) VALUES(?,?,?)", (uptime, load,str(nomMachine),))

    conn.commit()

    print("[+] Les informations du client " + str(nomMachine) + " ont été reçues et enregistrées.")
    return



                        ###                                           ###
                        # Envois et réception de messages via le réseau #
                        ###                                           ###


###
# Ajout du nouveau Client
###

class AddClient(Thread):
    """ Thread de récupération des informations sur le CPU """

    def __init__(self, socket, address, password):
        Thread.__init__(self)
        self.address = address
        self.socket = socket
        self.password = password
        self.res = 2

    def run(self):
        """ Tâches à effectuer pour chaque client"""

        response = self.socket.recv(255)
        data = pickle.loads(response)

        data["Client"]["IP"] = self.address

        # Enregistrement de la machine dans le Stage #
        SqlAddToStage(data)
        token = SendToken(self.socket, self.password, 1)
        if token == 0:
            SqlAddMachine(data)
            self.res = 0
            self.result()
        elif token == 1:
            self.res = 1
            self.result()


    def result(self):

        if self.res == 0:
            return 0
        elif self.res == 1:
            return 1








###
# Réception des infortions depuis un client enregistré
###

class ReceptionClient(Thread):
    """ Thread de récupération des informations sur le CPU """

    def __init__(self, socket, address):
        Thread.__init__(self)
        self.address = address
        self.socket = socket
        self.stay = True

    def run(self):
        """ Tâches à effectuer pour chaque client"""


        while self.stay == True:
            response = self.socket.recv(512)
            try:
                data = pickle.loads(response)
            except (socket.error , EOFError):
                break
            if isinstance(data, dict):
                data["IP"] = self.address
                SqlSaveInfos(data)
            elif data == "exit":
                self.stay = False
                break
        print("[!] Déconnexion du client: " + self.address)
        self.socket.close()




###
# Envoi du token au client
###

def SendToken(sock, password, step):
    """ Envoi d'un token d'approbation au client pour initialiser l'échange de données """

    hash_object = hashlib.sha512(password.encode('utf-8'))
    passhash = hash_object.hexdigest()



    response = sock.recv(512)
    if step == 2:
        response = sock.recv(512)
    response = pickle.loads(response)
    if isinstance(response, dict):
        SendToken(sock,password)
    elif response == passhash:
        sock.send(pickle.dumps("OK"))
        return 0

    elif response != passhash:
        sock.send(pickle.dumps("Mauvais mot de passe"))
        return 1
    else:
        return 1






def main():
    """ Programme principal """

    password = passwd
    SqlTables()
    token = None

    while (1):
        s.listen(10)

        client,(address, port) = s.accept()
        print("[+] Connexion depuis " + address)
        exist =SqlMachineExist(address)
        if exist == 1:
            threadAddClient = AddClient(client, address, password)
            threadAddClient.start()
            threadAddClient.join()

            if threadAddClient.result() == 0:
                print("[?] Succes de l'authentification de " + address)
                threadRecepClient = ReceptionClient(client, address)
                threadRecepClient.start()


            elif threadAddClient.result() == 1:
                print("[!] Echec de l'authentification de " + address)
                client.close()


        elif exist == 0:

            token = SendToken(client, password, 2)
            if token == 1:

                print("[!] Echec de l'authentification de " + address)
                client.close()

            elif token == 0:

                print("[?] Succes de l'authentification de " + address)
                threadRecepClient = ReceptionClient(client, address)
                threadRecepClient.start()



if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Fermeture du serveur")
        try:
            s.close()
            sys.exit(0)
        except SystemExit:
            os._exit(0)
