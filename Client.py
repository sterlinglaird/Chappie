import socket
import Command


class Client:
    def __init__(self):
        self.socket = socket.socket()

        # Needs to be changed if you want the client to connect to a different machine
        self.hostAddress = (socket.gethostname(), 9999)
        self.address = (socket.gethostname(), 9998)

    def send(self):
        cmd = Command.Command()
        cmd.init_send_message('Tester')
        cmd.send(self.hostAddress, self.socket)

if __name__ == "__main__":
    client = Client()
    client.send()

