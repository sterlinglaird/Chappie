from socket import *
from threading import Thread
import sys

# Custom Modules
from command import Command
import util

class Client:
    def __init__(self):
        """
        The class that contains client related functionality.
        """

        # Needs to be changed if you want the client to connect to a different machine
        # Using port 8585 since we chose that in our technical design
        self.host_address = (gethostname(), 8585)
        self.tcp_backlog = 5
        self.host_sock = socket()
        self.username = None
        self.chatroom = None
        self.chatrooms = []

    def listen(self):
        """
        Listens for new traffic from the server socket.
        """

        while True:
            data = self.host_sock.recv(1024)
            cmd = Command(data)
            self.execute_command(cmd)

    def execute_command(self, cmd: Command):
        """
        Executes a given command and performs an action depending on the command type.
        """

        if cmd.type == 'message':
            print("{}: {}".format(cmd.creator, cmd.body))

        elif cmd.type == 'connect':
            print("Connection Successful!")
            print("Please enter an alias (/set_alias <alias>):")

        elif cmd.type == 'alias':
            if cmd.creator == self.username:
                self.chatroom = util.defaultChatroom
                print("Alias '{}' confirmed! ".format(cmd.creator))
            else:
                print("'{}' joins Chat. ".format(cmd.creator))

        elif cmd.type == 'disconnect':
            print("{} disconnected".format(cmd.creator))

        elif cmd.type == 'join_chatroom':
            if cmd.creator == self.username:
                self.chatroom = cmd.body
            print("{} joined chatroom {}".format(cmd.creator, cmd.body))

        elif cmd.type == 'create_chatroom':
            print("{} created chatroom {}".format(cmd.creator, cmd.body))

        elif cmd.type == 'delete_chatroom':
            print("{} deleted chatroom {}".format(cmd.creator, cmd.body))

        elif cmd.type == 'get_chatrooms':
            chatrooms = cmd.body
            for chatroom in chatrooms:
                print('CR: {}'.format(chatroom))
            print('DONE_CR_LIST')

        elif cmd.type == 'error':
            print("Error: {}".format(cmd.body))

        sys.stdout.flush()

    def parse_input(self):
        """
        Parses input sent by the client.
        Eventually will be replaced with GUI sending commands.
        """

        # Prompt for commands
        raw_input = input()

        # Initialize command object
        cmd = Command()

        # Command Structure:
        # /[command_name] [command_body]
        # ie. /message Hello World!

        lst_parsed_input = raw_input.split(' ', 1)
        if lst_parsed_input == 0:
            print("You must enter a command.")
            return

        cmd_name = lst_parsed_input[0] if len(lst_parsed_input) >= 1 else ''
        cmd_body = lst_parsed_input[1] if len(lst_parsed_input) >= 2 else ''

        if cmd_name == '/message':
            cmd.init_send_message(cmd_body, self.chatroom)
        elif cmd_name == '/set_alias':
            alias = cmd_body.strip()
            while len(alias) <= 3:
                print("An alias must be greater than three characters long.")
                print("Please enter an alias (/set_alias <alias>):")
                return            
            self.username = alias
            cmd.init_set_alias(alias)
        elif cmd_name == '/quit':
            cmd.init_disconnect()
            sys.exit()
        elif cmd_name == '/join':
            cmd.init_join_chatroom(cmd_body)
        elif cmd_name == '/create':
            cmd.init_create_chatroom(cmd_body)
        elif cmd_name == '/delete':
            cmd.init_delete_chatroom(cmd_body)
        elif cmd_name == '/get_chatrooms':
            cmd.init_get_chatrooms(None)
        else:
            print("\"{}\" is not a valid command.".format(cmd_name))
            return
        
        # Send the command to the server
        cmd.send(self.host_sock)

    def start(self, cmdline=False):
        """
        Starts the client by connecting to the server then awaits commands.
        """

        # Connects to the server and begin listening for traffic
        self.host_sock.connect(self.host_address)
        Thread(target=self.listen).start()

        # Prompt the user to provide an alias. Seperate so that the first message gets sent as a full line which will be picked up by the client gui
        print("Starting Connection ... ")

        # Send a connection request to the server and sets the current user
        cmd = Command()
        cmd.init_connect()
        cmd.send(self.host_sock)

        if cmdline:
            # Continually parse input from the user
            while True:
                self.parse_input()

if __name__ == '__main__':
    client = Client()
    client.start(True)
