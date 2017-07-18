from socket import *
from threading import Thread

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
            if cmd.creator == self.username:
                self.chatroom = util.defaultChatroom
            print("{} connected".format(cmd.creator))
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
        elif cmd.type == 'error':
            print("Error: {}".format(cmd.body))
    
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

        cmd_name = lst_parsed_input[0]
        cmd_body = lst_parsed_input[1]

        if cmd_name == '/message':
            cmd.init_send_message(cmd_body, self.chatroom)
        elif cmd_name == '/quit':
            cmd.init_disconnect()
            sys.exit()
        elif cmd_name == '/join':
            cmd.init_join_chatroom(cmd_body)
        elif cmd_name == '/create':
            cmd.init_create_chatroom(cmd_body)
        elif cmd_name == '/delete':
            cmd.init_delete_chatroom(cmd_body)
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
        print("Please enter an alias: ")
        alias = input()

        while len(alias.strip()) <= 4:
            print("An alias must be greater than four characters long.")
            alias = input("Please enter an alias: ")

        # Send a connection request to the server and sets the current user
        cmd = Command()
        cmd.init_connect(alias)
        cmd.send(self.host_sock)

        self.username = alias

        if cmdline:
            # Continually parse input from the user
            while True:
                self.parse_input()

if __name__ == '__main__':
    client = Client()
    client.start(True)