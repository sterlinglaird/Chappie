import json
from socket import socket

class Command:
    def __init__(self, data=None):
        if data is not None:
            data = json.loads(data)
            self.type = data['type']
            self.body = data['body']
            self.createdBy = data['createdBy']
        else:
            self.type = None
            self.body = None
            self.createdBy = None

    def init_send_message(self, message: str):
        self.type = 'message'
        self.body = message

    def init_connect(self):
        self.type = 'connect'
        self.body = None

    def send(self, sock: socket):
        # Sends the command using the provided socket

        data = json.dumps({'type': self.type, 'createdBy': self.createdBy, 'body': self.body})
        sock.send(data.encode(encoding='UTF-8'))

