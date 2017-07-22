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
        self.userlist = []
        self.chatrooms = {"General": Chatroom("General", None, True)}

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
            except: # Should specify the actual exception that is occuring
                break

            if data is not None:
                cmd = Command(data)
                self.execute_command(cmd, origin_address, client_sock)

        print("{} lost connection".format(self.users[client_sock].alias))
        self.users.pop(client_sock, None)
        client_sock.close()

    def execute_command(self, cmd: Command, origin_address: (str, int), sock: socket):
        """
        Executes a given command and performs an action depending on the command type.
        """

        currUser = self.users.get(sock, None)

        if cmd.type == 'message':
            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Notifies user if chatroom doesnt exist
            if cmd.specificChatroom not in self.chatrooms:
                errorResponse = Command()
                errorResponse.init_error("Chatroom {} doesnt exist.".format(cmd.specificChatroom))
                errorResponse.send(sock)
                return

            print('{}/{}: {}'.format(cmd.creator, cmd.specificChatroom, cmd.body))

            # Relays the message to all the other clients in the same chatroom that the message was sent from
            self.chatrooms[cmd.specificChatroom].send_all(cmd)
            
        elif cmd.type == 'alias':
            # Get the chosen alias and address
            alias = cmd.body
            
            # Check that the alias isn't already in use
            if alias in self.userlist:
                # Send warning back to client
                errorResponse = Command()
                errorResponse.init_error("Alias '{}' already exist.".format(alias))
                errorResponse.send(sock)
                return

            # Update the server data and the command
            newUser = User(alias, sock)
            self.users[sock] = newUser
            self.chatrooms[util.defaultChatroom].add_user(newUser)
            cmd.creator = newUser.alias
            self.userlist.append(newUser.alias)
            cmd.specificChatroom = util.defaultChatroom

            print("Alias '{}' accepted".format(alias))

            # let all users in default chatroom know about the connection
            self.chatrooms[cmd.specificChatroom].send_all(cmd)

        elif cmd.type == 'connect':
            # Get the chosen alias and address
            address = "{}:{}".format(origin_address[0], origin_address[1])
            alias = address
            
            print("Connected with address '{}'".format(address))

            # let users about connection
            cmd.send(sock)
        
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
                chatroom.send_all(cmd)

        elif cmd.type == 'join_chatroom':
            chatroom = self.chatrooms.get(cmd.body, None)

            if chatroom is None:
                errorResponse = Command()
                errorResponse.init_error("Chatroom '{}' doesn't exist.".format(cmd.body))
                errorResponse.send(sock)
                return

            # Remove user from previous chatroom
            for chatroom in self.chatrooms.values():
                chatroom.rem_user(currUser)

            # Add user to chatroom
            chatroom.add_user(currUser)

            print("{} joined chatroom {}".format(currUser.alias, cmd.body))

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Notify users in chatroom that user has joined
            self.chatrooms[cmd.body].send_all(cmd)

        elif cmd.type == 'create_chatroom':
            # Create chatroom if it doesnt already exist, if it does then let user know
            if cmd.body in self.chatrooms:
                errorResponse = Command()
                errorResponse.init_error("Chatroom \"{}\" already exists.".format(cmd.body))
                errorResponse.send(sock)
                return
            else:
                self.chatrooms[cmd.body] = Chatroom(cmd.body, currUser)

            print("{} created chatroom {}".format(currUser.alias, cmd.body))

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Let all users know about the new chatroom
            self.send_all(cmd)

        elif cmd.type == 'delete_chatroom':
            chatroom = self.chatrooms.get(cmd.body, None)

            if chatroom is None:
                # Send error if chatroom doesnt exist
                errorResponse = Command()
                errorResponse.init_error("Chatroom \"{}\" doesn't exist.".format(cmd.body))
                errorResponse.send(sock)
                return
            elif chatroom.owner is not currUser:
                # Send error if user doesnt own the chatroom
                errorResponse = Command()
                errorResponse.init_error("Chatroom {} is not owned by you so you cannot delete it.".format(chatroom.name))
                errorResponse.send(sock)
                return

            # Move all current users in chatroom to default room
            userList = list(chatroom.users.values())
            for user in userList:
                chatroom.rem_user(user)
                self.chatrooms[util.defaultChatroom].add_user(user)

            self.chatrooms.pop(cmd.body, None)

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Let all users know about the deleted chatroom
            self.send_all(cmd)

            # Let all users know about the joins to default chatroom
            for deletedUser in userList:
                joinCmd = Command()
                joinCmd.init_join_chatroom(util.defaultChatroom)
                joinCmd.creator = deletedUser.alias

                for user_socket in self.chatrooms[util.defaultChatroom].users.values():
                    joinCmd.send(user_socket.socket)

            print("{} deleted chatroom {}".format(currUser.alias, cmd.body))
        
        elif cmd.type == 'get_chatrooms':
            get_chatrooms_cmd = Command()
            get_chatrooms_cmd.init_get_chatrooms(list(self.chatrooms.keys()))
            get_chatrooms_cmd.send(sock)

    def send_all(self, cmd: Command):
        for user_socket in list(self.users):
            try:
                cmd.send(user_socket)
            except:
                print("{} lost connection".format(self.users[user_socket].alias))
                self.users.pop(user_socket, None)

if __name__ == '__main__':
    server = Server()
    print("Starting Server")
    server.listen()
