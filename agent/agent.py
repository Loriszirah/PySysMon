#!/usr/bin/python
# -*- coding: utf-8 -*-


import psutil, bitmath, socket, pickle, time, os
from threading import Thread


                                ###                ###
                                # Variables globales #
                                ###                ###

# Information du serveur #
server = "localhost"
portServer = 50000

# Informations de chaque Threads #
Infos = {}





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

        # Uptime #
        uptime = os.popen("uptime", "r").read()
        uptime = uptime.split(" ")
        uptime = uptime[4].split(",")

        Client["Uptime"] = uptime[0]

        # Stockage des infos sur la RAM dans la variable globale
        Infos["Client"] = Client


###
# Envoie des informations
###


def SendInfos():
    """ Envoie des informations récoltées au serveur """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, portServer))

    # Encryption du paquet avec Pickle pour l'envoi du dictionnaire
    s.send(pickle.dumps(Infos))

    s.close()

    return 0

def main():
    """ Programme principal """

    while (1):
        # Création des threads
        threadCpu = InfosCpu()
        threadRam = InfosRam()
        threadClient = InfosClient()

        # Démarrage des threads
        threadCpu.start()
        threadRam.start()
        threadClient.start()

        # Attente de terminaison des threads
        threadCpu.join()
        threadRam.join()
        threadClient.join()

        print(Infos)

        # Envoi des informations
        SendInfos()

        # Petite pause pour laisser le serveur recevoir le paquet
        time.sleep(2)



if __name__ == '__main__':
    main()
