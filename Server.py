import socket
import Command


class Server:
    def __init__(self):
        self.socket = socket.socket()
        self.address = (socket.gethostname(), 9999)
        self.tcpBacklog = 5

    def listen(self):
        print('Starting Server...')

        try:
            self.socket.bind(self.address)
            self.socket.listen(self.tcpBacklog)
        except OSError:
            print("Error: Could not start server")
            exit(1)

        while True:
            client, originAddress = self.socket.accept()
            data = client.recv(1024)

            command = Command.Command(data)
            self.execute_command(command, originAddress)

    def execute_command(self, command, originAddress):
        if command.type == 'message':
            print('%s: %s' % (originAddress[0], command.body))


if __name__ == "__main__":
    server = Server()
    server.listen()