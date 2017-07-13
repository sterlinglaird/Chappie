import sys
from socket import *
from threading import Thread

# Custom Modules
from command import Command

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
            print("{} Connected".format(cmd.creator))
        elif cmd.type == 'disconnect':
            print("{} Disconnected".format(cmd.creator))
    
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

        lst_parsed_input = raw_input.split(' ')
        if lst_parsed_input == 0:
            print("You must enter a command.")
            return
        
        cmd_name = lst_parsed_input[0]
        cmd_body = ''
        for i in range(1, len(lst_parsed_input)):
            if i == 1:
                cmd_body = lst_parsed_input[i]
            else:
                cmd_body = '{} {}'.format(cmd_body, lst_parsed_input[i])

        if cmd_name == '/message':
            cmd.init_send_message(cmd_body)
        elif cmd_name == '/quit':
            cmd.init_disconnect()
            sys.exit()
        else:
            print("\"{}\" is not a valid command.".format(cmd_name))
            return
        
        # Send the command to the server
        cmd.send(self.host_sock)

    def start(self):
        """
        Starts the client by connecting to the server then awaits commands.
        """

        # Connects to the server and begin listening for traffic
        self.host_sock.connect(self.host_address)
        Thread(target=self.listen).start()

        # Prompt the user to provide an alias
        alias = input("Please enter an alias: ")
        while len(alias.strip()) <= 4:
            print("An alias must be greater than four characters long.")
            alias = input("Please enter an alias: ")

        # Send a connection request to the server
        cmd = Command()
        cmd.init_connect(alias)
        cmd.send(self.host_sock)

        # Continually parse input from the user
        while True:
            self.parse_input()

if __name__ == '__main__':
    client = Client()
    client.start()