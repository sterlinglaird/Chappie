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
        print(cmd.stringify())
        sys.stdout.flush()

    def parse_input(self):
        """
        Parses input sent by the client.
        Eventually will be replaced with GUI sending commands.
        """

        # Prompt for commands
        raw_input = input()

        # Initialize command object
        try:
            cmd = Command(raw_input)
            cmd.send(self.host_sock)
        except:
            print("\"{}\" is not a valid command.".format(raw_input.split()[0]))
            sys.stdout.flush()

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
