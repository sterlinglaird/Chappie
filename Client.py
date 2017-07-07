from socket import *
from command import Command
from threading import Thread


class Client:
    def __init__(self):

        # Needs to be changed if you want the client to connect to a different machine
        self.hostAddress = (gethostname(), 9999)
        self.tcpBacklog = 5
        self.hostSock = socket()

    def listen(self):

        # Listens for new traffic from the socket
        while True:
            data = self.hostSock.recv(1024)
            cmd = Command(data)
            self.execute_command(cmd)

    def execute_command(self, cmd: Command):

        # Performs the appropriate action depending on the command type
        if cmd.type == 'message':
            print('{}: {}'.format(cmd.createdBy, cmd.body))
        elif cmd.type == 'connect':
            print('Connected')

    def start(self):

        # Connects to the server and begin listening for traffic
        self.hostSock.connect(self.hostAddress)
        Thread(target=self.listen).start()

        # Send a connection request to the server
        connect = Command()
        connect.init_connect()
        connect.send(self.hostSock)

        # Continually take new input from user and send it as a message to the server
        while True:
            text = input()
            cmd = Command()
            cmd.init_send_message(text)
            cmd.send(self.hostSock)

if __name__ == "__main__":
    client = Client()
    client.start()



