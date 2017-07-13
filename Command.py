import json
from socket import socket

class Command:
    def __init__(self, data=None):
        """
        The class that contains command related functionality.
        """

        # Initialize the command based on data provided
        if data is not None:
            data = json.loads(data)
            self.type = data['type']
            self.body = data['body']
            self.creator = data['creator']
        else:
            self.type = None
            self.body = None
            self.creator = None

    def init_send_message(self, message: str):
        """
        Initializes the message command.
        """

        self.type = 'message'
        self.body = message

    def init_connect(self, alias : str):
        """
        Initializes the connect command.
        """

        self.type = 'connect'
        self.body = alias
    
    def init_disconnect(self):
        """
        Initializes the disconnect command.
        """

        self.type = 'disconnect'
        self.body = None

    def send(self, sock: socket):
        """
        Sends the command using the provided socket.
        """

        data = json.dumps({'type': self.type, 'creator': self.creator, 'body': self.body})
        sock.send(data.encode(encoding='UTF-8'))