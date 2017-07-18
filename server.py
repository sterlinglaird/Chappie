from socket import *
from threading import Thread

# Custom Modules
from command import Command
from user import User
from chatroom import Chatroom
import util

class Server:
    def __init__(self):
        """
        The class that contains server related functionality.
        """

        self.listener = socket()
        self.address = (gethostname(), 8585)
        self.tcp_backlog = 5
        self.users = {}
        self.chatrooms = {"Default": Chatroom("Default", None, True)}

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
            data = client_sock.recv(1024)
            cmd = Command(data)
            self.execute_command(cmd, origin_address, client_sock)

        client_sock.close()

    def execute_command(self, cmd: Command, origin_address: (str, int), sock: socket):
        """
        Executes a given command and performs an action depending on the command type.
        """

        currUser = self.users.get(sock, None)

        if cmd.type == 'message':
            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            print('{}/{}: {}'.format(cmd.creator, cmd.specificChatroom, cmd.body))

            # Relays the message to all the other clients in the same chatroom that the message was sent from
            for user in self.chatrooms[cmd.specificChatroom].users.values():
                cmd.send(user.socket)

        elif cmd.type == 'connect':
            # Get the chosen alias and address
            alias = cmd.body
            address = "{}({})".format(origin_address[0], origin_address[1])

            # Check that the alias isn't already in use
            if alias in self.users.values():
                # Send warning back to client
                pass

            # Update the server data and the command
            newUser = User(alias, sock)
            self.users[sock] = newUser
            self.chatrooms[util.defaultChatroom].add_user(newUser)
            cmd.creator = newUser.alias
            cmd.specificChatroom = util.defaultChatroom

            print("{} connected with origin address: {}".format(alias, address))

            # let all users in default chatroom know about the connection
            for user in self.chatrooms[util.defaultChatroom].users.values():
                cmd.send(user.socket)
        
        elif cmd.type == 'disconnect':
            # Close the socket
            sock.close()

            connectedChatrooms = []

            # Remove the user
            self.users.pop(sock)
            for chatroom in self.chatrooms.values():
                chatroom.rem_user(currUser.alias)
                connectedChatrooms.append(chatroom.name)

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            print("{} disconnected".format(currUser.alias))

            # Relays the message to all the other clients in the same chatrooms as the user who disconnected
            for chatroom in connectedChatrooms:
                for user in self.chatrooms[chatroom].users:
                    cmd.send(user.socket)

        elif cmd.type == 'join_chatroom':
            # Remove user from previous chatroom
            for chatroom in self.chatrooms.values():
                chatroom.rem_user(currUser)

            # Add user to chatroom
            self.chatrooms[cmd.body].add_user(currUser)

            print("{} joined chatroom {}".format(currUser.alias, cmd.body))

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Notify users in chatroom that user has joined
            for user in self.chatrooms[cmd.body].users.values():
                cmd.send(user.socket)

        elif cmd.type == 'create_chatroom':

            # Create chatroom if it doesnt already exist, if it does then let user know
            if cmd.body in self.chatrooms:
                # TODO
                pass
            else:
                self.chatrooms[cmd.body] = Chatroom(cmd.body, currUser)

            print("{} created chatroom {}".format(currUser.alias, cmd.body))

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Let all users know about the new chatroom
            for user_socket in self.users:
                cmd.send(user_socket)

        elif cmd.type == 'delete_chatroom':
            self.chatrooms.pop(cmd.body, None)

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Let all users know about the new chatroom
            for user_socket in self.users:
                cmd.send(user_socket)

            print("{} deleted chatroom {}".format(currUser.alias, cmd.body))


if __name__ == '__main__':
    server = Server()
    print("Starting Server")
    server.listen()