from socket import socket

class User:
    def __init__(self, alias: str, sock: socket):
        """
        The class that contains user related functionality.
        """

        self.alias = alias
        self.socket = sock