import json
from socket import socket
import struct

class Command:
    def __init__(self, data=None):
        """
        The class that contains command related functionality.
        """

        # Initialize the command based on data provided
        if data is not None:
            data = json.loads(data)
            self.type = data['type']
            self.body = data['body']
            self.creator = data['creator']
            self.specificChatroom = data['specificChatroom']
            self.suppress = data['suppress']
        else:
            self.type = None
            self.body = None
            self.creator = None
            self.specificChatroom = None
            self.suppress = False

    def init_send_message(self, message: str, specificChatroom: str):
        """
        Initializes the message command.
        """

        self.type = 'message'
        self.body = message
        self.specificChatroom = specificChatroom

    def init_set_alias(self, alias: str):
        """
        Initializes the set alias command.
        """

        self.type = 'alias'
        self.body = alias

    def init_connect(self):
        """
        Initializes the connect command.
        """

        self.type = 'connect'
        self.body = None

    def init_disconnect(self):
        """
        Initializes the disconnect command.
        """

        self.type = 'disconnect'
        self.body = None

    def init_join_chatroom(self, chatroom: str):
        """
        Initializes the join chatroom command.
        """

        self.type = 'join_chatroom'
        self.body = chatroom

    def init_create_chatroom(self, chatroom: str):
        """
        Initializes the create chatroom command.
        """

        self.type = 'create_chatroom'
        self.body = chatroom

    def init_delete_chatroom(self, chatroom: str):
        """
        Initializes the delete chatroom command.
        """

        self.type = 'delete_chatroom'
        self.body = chatroom
    
    def init_get_chatrooms(self, chatrooms: list):
        """
        Initializes the get chatrooms command.
        """

        self.type = 'get_chatrooms'
        self.body = chatrooms

    def init_block_user(self, user: str):
        """
        Initializes the block user command.
        """

        self.type = 'block_user'
        self.body = user

    def init_unblock_user(self, user: str):
        """
        Initializes the unblock user command.
        """

        self.type = 'unblock_user'
        self.body = user

    def init_error(self, message):
        """
        Initializes the error command.
        """

        self.type = 'error'
        self.body = message

    def init_list_users(self, chatroom):
        """
        Initializes the delete chatroom command.
        """

        self.type = 'list_users'
        self.body = chatroom

    def send(self, sock: socket):
        """
        Sends the command using the provided socket.
        """

        data = json.dumps({'type': self.type, 'creator': self.creator, 'specificChatroom': self.specificChatroom, 'body': self.body, 'suppress': self.suppress}).encode(encoding='UTF-8')
        length = struct.pack('!I', len(data))
        data = length + data
        sock.sendall(data)

    def stringify(self):
        """
        returns the json representation of the command.
        """

        return json.dumps({'type': self.type, 'creator': self.creator, 'specificChatroom': self.specificChatroom, 'body': self.body, 'suppress': self.suppress})
