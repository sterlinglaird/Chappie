from socket import *
from threading import Thread
import struct

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
                lengthbuf = client_sock.recv(4)
                length, = struct.unpack('!I', lengthbuf)
                data = client_sock.recv(length)
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

            # let users know about connection
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
            userOccupies = self.get_all_chatrooms(currUser)
            newChatroom = self.chatrooms.get(cmd.body, None)

            if newChatroom in userOccupies:
                errorResponse = Command()
                errorResponse.init_error("You are already in chatroom '{}'.".format(cmd.body))
                errorResponse.send(sock)
                return

            if newChatroom is None:
                errorResponse = Command()
                errorResponse.init_error("Chatroom '{}' doesn't exist.".format(cmd.body))
                errorResponse.send(sock)
                return

            # Check if user is blocked from the room they are trying to join
            if currUser.alias in self.chatrooms[cmd.body].blocked:
                errorResponse = Command()
                errorResponse.init_error("You are blocked from joining chatroom '{}'.".format(cmd.body))
                errorResponse.send(sock)
                return

            # Remove user from previous chatrooms
            for chatroom in self.chatrooms.values():
                chatroom.rem_user(currUser)

            # Add user to chatroom
            newChatroom.add_user(currUser)

            print("{} joined chatroom {}".format(currUser.alias, newChatroom.name))

            # Adds a tag that says who authored the command
            cmd.creator = currUser.alias

            # Notify users in chatroom that user has joined
            self.chatrooms[newChatroom.name].send_all(cmd)

            # Notify users in old chatrooms that user joined a different one
            for chatroom in userOccupies:
                chatroom.send_all(cmd)

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
                errorResponse.init_error("Chatroom \"{}\" is not owned by you so you cannot delete it.".format(chatroom.name))
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

        elif cmd.type == 'block_user':
            # Find location of blocker
            for blocker_chatroom in self.chatrooms:
                # When the blocker is found
                if currUser.alias in self.chatrooms[blocker_chatroom].users:
                    user_location = self.chatrooms[blocker_chatroom]
                    # Check if they are the owner of the room they're in
                    if user_location.owner is not currUser:
                        errorResponse = Command()
                        errorResponse.init_error("You are not the owner of chatroom {}, so you cannot block users from joining it.".format(user_location.name))
                        errorResponse.send(sock)
                        return
                    # If they are the owner
                    else:
                        # Find the location of the user being blocked
                        for chatroom in self.chatrooms:
                            if cmd.body in self.chatrooms[chatroom].users:
                                blocked_user_location = self.chatrooms[chatroom]
                                blocked_user = blocked_user_location.users[cmd.body]
                                # Block the user
                                user_location.block_user(blocked_user)
                                
                                # Add a tag that says who authored the command
                                cmd.creator = currUser.alias

                                # Add a tag that says which room the user is blocked from
                                cmd.specificChatroom = user_location.name

                                # Let all users in the blocker's room know about the block
                                user_location.send_all(cmd)

                                # If the blocker and the user being blocked are in the same room
                                if user_location == blocked_user_location:
                                    # Remove the blocked user from the room, and return them to Default
                                    user_location.rem_user(blocked_user)
                                    self.chatrooms[util.defaultChatroom].add_user(blocked_user)
                                else:
                                    # Let the blocked user's room know about the block
                                    blocked_user_location.send_all(cmd)

                                print("{} blocked {} from chatroom {}".format(currUser.alias, cmd.body, user_location.name))

                                return
    
            # If the user can't be found
            errorResponse = Command()
            errorResponse.init_error("User \"{}\" does not exist.".format(cmd.body))
            errorResponse.send(sock)
            return

        elif cmd.type == 'unblock_user':
            # Find location of unblocker
            for unblocker_chatroom in self.chatrooms:
                # When the unblocker is found
                if currUser.alias in self.chatrooms[unblocker_chatroom].users:
                    user_location = self.chatrooms[unblocker_chatroom]
                    # Check if they are the owner of the room they're in
                    if user_location.owner is not currUser:
                        errorResponse = Command()
                        errorResponse.init_error("You are not the owner of chatroom {}, so you cannot unblock blocked users.".format(user_location.name))
                        errorResponse.send(sock)
                        return
                    # If they are the owner
                    else:
                        # Find the location of the user being unblocked
                        for chatroom in self.chatrooms:
                            if cmd.body in self.chatrooms[chatroom].users:
                                blocked_user_location = self.chatrooms[chatroom]
                                blocked_user = blocked_user_location.users[cmd.body]
                                # unlock the user
                                user_location.unblock_user(blocked_user)
                                
                                print("{} unblocked {} from chatroom {}".format(currUser.alias, cmd.body, user_location.name))

                                # Add a tag that says who authored the command
                                cmd.creator = currUser.alias

                                # Add a tag that says which room the user is unblocked from
                                cmd.specificChatroom = user_location.name

                                # Let all users in the room know about the unblock
                                user_location.send_all(cmd)

                                if user_location != blocked_user_location:
                                    # Let the blocked user's room know about the block
                                    blocked_user_location.send_all(cmd)
                                
                                return

            # If the user can't be found
            errorResponse = Command()
            errorResponse.init_error("User \"{}\" does not exist.".format(cmd.body))
            errorResponse.send(sock)
            return

        elif cmd.type == 'get_chatrooms':
            get_chatrooms_cmd = Command()
            get_chatrooms_cmd.init_get_chatrooms(list(self.chatrooms.keys()))
            get_chatrooms_cmd.send(sock)


        elif cmd.type == 'list_users':
            newChatroom = self.chatrooms.get(cmd.body, None)

            # send a join command for every user in the chatroom, except the current user
            for user in newChatroom.users:
                if user == currUser.alias:
                    continue

                responseCmd = Command()
                responseCmd.init_join_chatroom(newChatroom.name)
                responseCmd.creator = user
                responseCmd.send(sock)

                print("Listing user '{}' for '{}'".format(user, currUser.alias))

    def get_all_chatrooms(self, user: User):
        '''
        Returns all chatrooms a user belongs to
        '''

        occupies = []
        for chatroom in self.chatrooms.values():
            if chatroom.users.get(user.alias, None):
                occupies.append(chatroom)

        return occupies

    def send_all(self, cmd: Command):
        '''
        Sends a command to all users
        '''

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
