import tkinter as tk

# Custom Modules
from client import Client

class ClientGUI(tk.Frame):
    def __init__(self, client):
        """
        Initialize the client GUI.
        """

        # Assign the client
        self.client = client

        # Initialize Tkinter GUI
        self.master = tk.Tk()
        super().__init__(self.master)
        self.initialize_window()

        # Chat Rooms
        self.initialize_chatrooms()

        # Message Window
        self.initialize_messages()

        # User List
        self.initialize_users()


    def initialize_window(self):
        """
        Initialize the window of the chat application.
        """

        self.master.title("Chat Application")

        # Set size of window and central start location
        w = 800
        h = 600
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw/2) - (w/2)
        y = (sh/2) - (h/2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    def initialize_chatrooms(self):
        """
        Initialize the layout of the chat room list.
        """

        # Label for the chat room list
        self.lbl_chatrooms = tk.Label(self.master, text="Chat Rooms")

        # Add a frame for the list of chat room buttons
        self.frm_btn_chatrooms = tk.Frame(self.master)

        # List of chat rooms as buttons
        # Need to figure out how to update this from the client
        self.lst_btn_chatrooms = [
            # Initialize with the general chat room
            tk.Button(self.frm_btn_chatrooms, text="General", command=None)
        ]

        # Create chat room button
        # Need to create the create chat room command
        self.btn_create_chatroom = tk.Button(self.master, text="Create Chat Room", command=None)

        # Delete chat room button
        # Need to create the delete chat room command
        self.btn_delete_chatroom = tk.Button(self.master, text="Delete Chat Room", command=None)

        # Handle the grid layout of the widgets
        self.lbl_chatrooms.grid(row=0, column=0)

        # Display each chat room
        chatroom_count = 1
        for chatroom in self.lst_btn_chatrooms:
            chatroom.grid(row=chatroom_count, column=0)
            chatroom_count += 1

        self.btn_create_chatroom.grid(row=2, column=0)
        self.btn_delete_chatroom.grid(row=3, column=0)

    def initialize_messages(self):
        """
        Initialize the layout of the messages list.
        """

    def initialize_users(self):
        """
        Initialize the layout of the user list.
        """

if __name__ == '__main__':
    # Intialize the client
    client = Client()
    client.start()

    # Initilize the GUI
    application = ClientGUI(client)
    application.mainloop()