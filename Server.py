from socket import *
from threading import Thread
from command import Command
from user import User


class Server:
    def __init__(self):
        self.listener = socket()
        self.address = (gethostname(), 9999)
        self.tcpBacklog = 5
        self.users = {}

    def listen(self):

        # Begins listening for a connection
        self.listener.bind(self.address)
        self.listener.listen(self.tcpBacklog)

        # Accepts all new traffic and delegates a thread to be responsible for the new client
        while True:
            clientSock, originAddress = self.listener.accept()
            Thread(target=self.handle_client, args=(originAddress, clientSock)).start()

    def handle_client(self, originAddress: (str, int), clientSock: socket):

        # Handles all new traffic from the client
        while True:
            data = clientSock.recv(1024)
            if not data:
                break
            cmd = Command(data)
            self.execute_command(cmd, originAddress, clientSock)

        clientSock.close()

    def execute_command(self, cmd: Command, originAddress: (str, int), sock: socket):

        # Performs the appropriate action depending on the command type
        if cmd.type == 'message':
            cmd.createdBy = self.users[sock].alias  # Adds a tag that says who authored the message
            print('{}: {}'.format(cmd.createdBy, cmd.body))

            # Relays the message to all the other clients
            for user in self.users.keys():
                cmd.send(user)

        elif cmd.type == 'connect':
            alias = '{}({})'.format(originAddress[0], originAddress[1])
            print('{} connected'.format(alias))
            self.users[sock] = User(alias)
            cmd.send(sock)

if __name__ == "__main__":
    server = Server()

    print('Starting Server')
    server.listen()


