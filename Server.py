from socket import *
from threading import Thread

# Custom Modules
from command import Command
from user import User

class Server:
    def __init__(self):
        """
        The class that contains server related functionality.
        """

        self.listener = socket()
        self.address = (gethostname(), 8585)
        self.tcp_backlog = 5
        self.users = {}

    def listen(self):
        """
        Listens for all new traffic and delegates a separate thread for each client.
        """

        # Begins listening for a connection
        self.listener.bind(self.address)
        self.listener.listen(self.tcp_backlog)

        # Accepts all new traffic and delegates a thread to be responsible for the new client
        while True:
            client_sock, origin_address = self.listener.accept()
            Thread(target=self.handle_client, args=(origin_address, client_sock)).start()

    def handle_client(self, origin_address: (str, int), client_sock: socket):
        """
        Handles all commands sent from the client.
        """

        while True:
            try:
                data = client_sock.recv(1024)
                cmd = Command(data)
                self.execute_command(cmd, origin_address, client_sock)
            except:
                # Notify other users that the client has disconnected
                print("Server exception thrown")
                break

        client_sock.close()

    def execute_command(self, cmd: Command, origin_address: (str, int), sock: socket):
        """
        Executes a given command and performs an action depending on the command type.
        """

        if cmd.type == 'message':
            # Adds a tag that says who authored the message
            cmd.creator = self.users[sock].alias
            print('{}: {}'.format(cmd.creator, cmd.body))

            # Relays the message to all the other clients
            for user_socket in self.users.keys():
                cmd.send(user_socket)

        elif cmd.type == 'connect':
            # Get the chosen alias and address
            alias = cmd.body
            address = "{}({})".format(origin_address[0], origin_address[1])

            # Check that the alias isn't already in use
            if alias in self.users.values():
                # Send warning back to client
                pass

            # Show who connected and where their origin address is
            print("{} connected with origin address: {}".format(alias, address))

            self.users[sock] = User(alias)
            cmd.send(sock)
        
        elif cmd.type == 'disconnect':
            # Close the socket
            sock.close()

            # Show that the user disconnected
            print("{} disconnected".format(self.users[sock].alias))

            # Relays the message to all the other clients
            for user_socket in self.users.keys():
                cmd.send(user_socket)

if __name__ == '__main__':
    server = Server()
    print("Starting Server")
    server.listen()