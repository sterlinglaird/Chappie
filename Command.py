import json

class Command:

    def __init__(self, data=None):
        if data is not None:
            data = json.loads(data)
            self.type = data['type']
            self.body = data['body']
        else:
            self.type = None
            self.body = None

    def init_send_message(self, message):
        self.type = 'message'
        self.body = message

    def send(self, hostAddress, socket):
        data = json.dumps({'type': self.type, 'body': self.body})
        socket.connect(hostAddress)
        socket.send(data.encode(encoding='UTF-8'))

