#!/usr/bin/python
# -*- coding: utf-8 -*-


import psutil, bitmath, socket, pickle, time, os, hashlib, sys
from threading import Thread


                                ###                ###
                                # Variables globales #
                                ###                ###

# Information du serveur #
server = "localhost"
portServer = 50000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server, portServer))
# Informations de chaque Threads #
Infos = {}

# Mot de passe pour le serveur #
passwd = "test"





                ###                                                   ###
                #   Agent client récupérant les informations du systeme #
                ###                                                   ###


###
# CPU
###


class InfosCpu(Thread):
    """ Thread de récupération des informations sur le CPU """

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        Cpu = {}

        # Modéle et fréquence de base du CPU #
        model = os.popen("cat /proc/cpuinfo | grep \"model name\" | uniq", "r").read()
        model = model.split(": ")
        model = model[1].split(" @ ")

        frequency = model[1].split("\n")

        Cpu["Model"] = model[0]
        Cpu["Frequency"] = frequency[0]

        # Nombre de coeurs et "threads" #
        cpuCore = psutil.cpu_count(logical = False)

        Cpu["Core"] = cpuCore

        cpuThreads = psutil.cpu_count()

        Cpu["Thread"] = cpuThreads

        # Pourcentage d'utilisation général #
        cpuUtil = psutil.cpu_percent(interval=1)

        Cpu["Percent"] = cpuUtil

        # Stockage des infos sur le CPU dans la variable globale
        Infos["CPU"] = Cpu




###
# Mémoire RAM
###


class InfosRam(Thread):
    """ Thread de récupération des informations sur le CPU """

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        Ram = {}

        # Mémoire totale #
        ramTotal = round(float(bitmath.Bit(psutil.virtual_memory().total).to_Gib()),2)

        Ram["Total"] = str(ramTotal) + " GB"

        # Mémoire utilisée (en GB) #
        ramUse = round(float(bitmath.Bit(psutil.virtual_memory().active).to_Gib()),2)
        Ram["Use"] = str(ramUse) + " GB"

        # Pourcentage d'utilisation #
        ramPercent = psutil.virtual_memory().percent

        Ram["Percent"] = ramPercent

        # Stockage des infos sur la RAM dans la variable globale
        Infos["RAM"] = Ram

###
# Informations sur le client
###

class InfosSystem(Thread):
    """ Thread de récupération des informations sur le CPU """

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        System = {}

        # Uptime #
        uptime = os.popen("uptime -p", "r").read()
        uptime = uptime.split("\n")
        uptime = uptime[0].split()
        uptimetmp = uptime[1:]
        uptime = ""
        for x in uptimetmp:
            uptime = uptime + " " + x

        System["Uptime"] = str(uptime)

        # Charge systeme #
        loadavg = os.popen("cat /proc/loadavg", "r").read()
        loadavg = loadavg.split()
        loadavg = loadavg[0]

        System["Load"] = loadavg

        # Stockage des infos systeme dans Infos
        Infos["System"] = System


###
# Informations sur le client
###

class InfosClient(Thread):
    """ Thread de récupération des informations sur le CPU """

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        Client = {}

        # Information sur le hostname du client #
        hostname = os.popen("hostname", "r").read()
        hostname = hostname.split("\n")

        Client["Hostname"] = hostname[0]

        # Nom de la distribution #
        distribname = os.popen("lsb_release -a |grep Description", "r").read()
        distribname = distribname.split(":\t")
        distribname = distribname[1].split("\n")

        distribname = distribname[0]
        Client["Distribution"] = distribname

        # Version de la distribution #
        distribversion = os.popen("lsb_release -a |grep Release", "r").read()
        distribversion = distribversion.split(":\t")
        distribversion = distribversion[1].split("\n")
        distribversion = distribversion[0]

        Client["Version"] = distribversion

        # Version du kernel #
        kernel = os.popen("uname -r", "r").read()
        kernel = kernel.split("\n")
        kernel = kernel[0]
        Client["Kernel"] = kernel


        # Stockage des infos du client
        Infos["Client"] = Client



###
# Procédure d'appareillage
###

def SayHello(sync, sock, password):
    """ Procédure d'appareillage avec le serveur """

    hash_object = hashlib.sha512(password.encode('utf-8'))
    password = hash_object.hexdigest()

    # Encryption du paquet avec Pickle pour l'envoi du dictionnaire
    sock.send(pickle.dumps(Infos))
    time.sleep(2)
    sock.send(pickle.dumps(password))

    while sync == False:
        response = sock.recv(64)

        data = pickle.loads(response)

        if data == "OK":
            sync = True
        elif data == "Mauvais mot de passe":
            print(data)
            exit()

    return sync


###
# Envoie des informations
###


def SendInfos(sock):
    """ Envoie des informations récoltées au serveur """



    # Encryption du paquet avec Pickle pour l'envoi du dictionnaire
    sock.send(pickle.dumps(Infos))


    return 0


def main():
    """ Programme principal """

    password = passwd
    sync = False

    while sync == False:

        # Appareillage avec le serveur #
        threadClient = InfosClient()
        threadCpu = InfosCpu()
        threadRam = InfosRam()
        threadSystem = InfosSystem()

        threadClient.start()
        threadCpu.start()
        threadRam.start()
        threadSystem.start()

        threadClient.join()
        threadCpu.join()
        threadRam.join()
        threadSystem.join()

        # time.sleep(1)
        sync = SayHello(sync, s, passwd)
        print("[+] Le serveur a accepté l'appareillage")



    while (1):
        print("[+] Envoi des infos")
        # Création des threads
        threadCpu = InfosCpu()
        threadRam = InfosRam()
        threadSystem = InfosSystem()

        # Démarrage des threads
        threadCpu.start()
        threadRam.start()
        threadSystem.start()

        # Attente de terminaison des threads
        threadCpu.join()
        threadRam.join()
        threadSystem.join()


        #print(Infos)
        try:
            # Envoi des informations
            SendInfos(s)
            # time.sleep(1)
        except BrokenPipeError:
            print("[!] Le serveur est injoignable")
            s.close()
            print("[-] Arret du daemon Pysysmon")
            exit()

        # Petite pause pour laisser le serveur recevoir le paquet



if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Arret du daemon Pysysmon")
        try:
            s.send(pickle.dumps("exit"))
            s.close()
            sys.exit(0)
        except SystemExit:
            s.close()
            os._exit(0)
