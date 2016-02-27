#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, pickle, psycopg2, time, hashlib, sys ,os
from threading import Thread

                                ###                ###
                                # Variables globales #
                                ###                ###

# Information du serveur #
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 50000))
# Chemin vers la base de données #


# Connexion à la base de données #
conn = psycopg2.connect(database='pysysmon' , user='pysysmon' )

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



    # Table des Machines #
    cur.execute("""CREATE TABLE IF NOT EXISTS Machines(
                    IDMachine SERIAL PRIMARY KEY,
                    NomMachine TEXT,
                    DistributionMachine TEXT,
                    DistributionVersion TEXT,
                    KernelVersion TEXT,
                    IPMachine TEXT)""", ())

    # Table des informations CPU #
    cur.execute("""CREATE TABLE IF NOT EXISTS Cpu(
                    IDCpuInfo SERIAL PRIMARY KEY,
                    ModelCpu TEXT,
                    FrequencyCpu TEXT,
                    NbCore TEXT,
                    NbThread TEXT,
                    PercentCpu TEXT,
                    HeureCpu TEXT,
                    IDMachine INTEGER,
                    FOREIGN KEY(IDMachine) REFERENCES Machines(IDMachine))""", ())

    # Table des informations RAM #
    cur.execute("""CREATE TABLE IF NOT EXISTS Ram(
                    IDRam SERIAL PRIMARY KEY,
                    TotalRam TEXT,
                    UseRam TEXT,
                    PercentRam TEXT,
                    HeureRam TEXT,
                    IDMachine INTEGER,
                    FOREIGN KEY(IDMachine) REFERENCES Machines(IDMachine))""", ())

    # Table des informations Systeme #
    cur.execute("""CREATE TABLE IF NOT EXISTS Systeme(
                    IDSysteme SERIAL PRIMARY KEY,
                    Uptime TEXT,
                    Load TEXT,
                    HeureSystem TEXT,
                    IDMachine INTEGER,
                    FOREIGN KEY(IDMachine) REFERENCES Machines(IDMachine))""", ())


    conn.commit()

    return



###
# Test l'existance d'une machine dans la table Machines
###

def SqlMachineExist(IP):
    """ Test de présence d'une machine dans la table grâce à son IP """
    cur.execute("SELECT * FROM Machines WHERE IPMachine=%s", (IP,))
    res = bool(cur.fetchone())

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
    distribution = client.get("Distribution")
    version = client.get("Version")
    kernel = client.get("Kernel")
    print(IP + "coucou")

    cur.execute("INSERT INTO  Machines(NomMachine, DistributionMachine, DistributionVersion, KernelVersion, IPMachine) VALUES(%s,%s,%s,%s,%s)", (nom,distribution,version, kernel,str(IP)))
    conn.commit()

    date = os.popen("date |cut -d \" \" -f 4", "r").read()
    date = date.split("\n")
    date = date[0]

    cur.execute("""SELECT IDMachine FROM Machines WHERE IPMachine =%s AND NomMachine=%s""", (IP,nom))
    idmachine = cur.fetchone()
    idmachine = idmachine[0]

    # Ajout des informations Cpu #
    Cpu = data.get("CPU")
    model = Cpu.get("Model")
    frequency = Cpu.get("Frequency")
    core = Cpu.get("Core")
    thread = Cpu.get("Thread")
    percent = Cpu.get("Percent")

    cur.execute("INSERT INTO Cpu(ModelCpu, FrequencyCpu, NbCore, NbThread, PercentCpu, HeureCpu, IDMachine) VALUES(%s,%s,%s,%s,%s,%s,%s)", (model,frequency,core,thread,percent, date,str(idmachine)))
    conn.commit()


    Ram = data.get("RAM")
    total = Ram.get("Total")
    use = Ram.get("Use")
    percent = Ram.get("Percent")

    cur.execute("INSERT INTO Ram(TotalRam, UseRam, PercentRam, HeureRam, IDMachine) VALUES(%s,%s,%s,%s,%s)", (total, use,percent,date,str(idmachine)))
    conn.commit()

    System = data.get("System")
    uptime = System.get("Uptime")
    load = System.get("Load")

    cur.execute("INSERT INTO Systeme(Uptime, Load, HeureSystem, IDMachine) VALUES(%s,%s,%s,%s)", (uptime, load,date,str(idmachine),))
    conn.commit()


    return

###
# Mise à jour des informations d'une machine existante
###

def SqlSaveInfos(data):
    """ Ecriture des informations dans la base de données """

    # Récupération de l'IP du client pour lier les informations stockées à sa machine #
    client = data.get("Client")
    nom = client.get("Hostname")
    IP = client.get("IP")
    date = os.popen("date |cut -d \" \" -f 4", "r").read()
    date = date.split("\n")
    date = date[0]

    cur.execute("""SELECT IDMachine FROM Machines WHERE IPMachine =%s AND NomMachine=%s""", (IP,nom,))
    idmachine = cur.fetchone()
    idmachine = str(idmachine[0])

    # Ajout des informations Cpu #
    Cpu = data.get("CPU")
    model = Cpu.get("Model")
    frequency = Cpu.get("Frequency")
    core = Cpu.get("Core")
    thread = Cpu.get("Thread")
    percent = Cpu.get("Percent")

    cur.execute("UPDATE Cpu SET ModelCpu=%s , FrequencyCpu=%s , NbCore=%s , NbThread=%s , PercentCpu=%s , HeureCpu=%s , IDMachine=%s WHERE IDMachine='"+idmachine+"'", (model,frequency,core,thread,percent,date, idmachine,))

    conn.commit()

    # Ajout des informations Ram #

    Ram = data.get("RAM")
    total = Ram.get("Total")
    use = Ram.get("Use")
    percent = Ram.get("Percent")

    cur.execute("UPDATE Ram SET TotalRam=%s , UseRam=%s , PercentRam=%s , HeureRam=%s , IDMachine=%s WHERE IDMachine='"+idmachine+"'", (total, use,percent,date,idmachine,))

    conn.commit()

    # Ajout des informations Systeme #

    System = data.get("System")
    uptime = System.get("Uptime")
    load = System.get("Load")

    cur.execute("UPDATE Systeme SET Uptime=%s , Load=%s , HeureSystem=%s , IDMachine=%s WHERE IDMachine='"+idmachine+"'", (uptime, load,date,idmachine,))

    conn.commit()

    print("[+] Les informations du client " + str(nom) + " ont été reçues et enregistrées.")
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

        response = self.socket.recv(512)
        data = pickle.loads(response)

        data["Client"]["IP"] = self.address


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
                data["Client"]["IP"] = self.address
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
        s.listen(3)

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
