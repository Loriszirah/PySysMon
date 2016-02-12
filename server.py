#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, pickle
from threading import Thread

                                ###                ###
                                # Variables globales #
                                ###                ###

# Information du serveur #
port = 50000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 50000))
# Informations de chaque Threads #
Infos = {}

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
        
        if response != "":
            data = pickle.loads(response)
            data["Client"]["IP"] = self.address
            print(data)




def main():
    """ Programme principal """

    while (1):
        s.listen(10)

        client, (address, port) = s.accept()
        threadClient = ConnexionClient(client, address)
        threadClient.start()

if __name__ == '__main__':
    main()
