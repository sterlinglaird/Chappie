import tkinter as tk
import tkinter.font as tkFont
from threading import Thread
from subprocess import Popen, PIPE

class ClientGUI(tk.Frame):
    def __init__(self, client: Popen):
        """
        Initialize the client GUI.
        """

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

        self.master.title("Chappie")
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=4)
        self.master.columnconfigure(2, weight=1)
        self.master.configure(bg="gray20")
        self.master.resizable(0,0)

        # Custom Fonts
        self.header_font = tkFont.Font(family="Verdana", size=14, weight="bold")
        self.default_font = tkFont.Font(family="Verdana", size=10)

        # Set size of window and central start location
        w = 900
        h = 450
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw/2) - (w/2)
        y = (sh/2) - (h/2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    def initialize_chatrooms(self):
        """
        Initialize the layout of the chat room list.
        """

        # Frame to hold the following widgets in
        self.frm_chatrooms = tk.Frame(self.master)
        self.frm_chatrooms.grid(row=0, column=0, sticky=tk.NW, padx=10, pady=10)
        self.frm_chatrooms.configure(bg="gray20")

        # Label for the chat room list
        self.lbl_chatrooms = tk.Label(self.frm_chatrooms, text="Chat Rooms", font=self.header_font, pady=2)
        self.lbl_chatrooms.grid(row=0, column=0)
        self.lbl_chatrooms.configure(bg="gray20", fg="white")

        # Create chat room button
        self.btn_create_chatroom = tk.Button(self.frm_chatrooms, text="Create Chat Room", 
                                             command=self.btn_create_chatroom_click, height=1, width=20, 
                                             font=self.default_font, pady=2)
        self.btn_create_chatroom.grid(row=1, column=0)

        # Delete chat room button
        self.btn_delete_chatroom = tk.Button(self.frm_chatrooms, text="Delete Chat Room", 
                                             command=self.btn_delete_chatroom_click, height=1, width=20, 
                                             font=self.default_font, pady=2)
        self.btn_delete_chatroom.grid(row=2, column=0)

        # Add a frame for the list of chat room buttons
        self.frm_btn_chatrooms = tk.Frame(self.frm_chatrooms, pady=5)
        self.frm_btn_chatrooms.grid(row=3, column=0)
        self.frm_btn_chatrooms.configure(bg="gray20")

        # List of chat rooms as buttons
        # Need to figure out how to update this from the client
        self.lst_btn_chatrooms = [
            # Initialize with the general chat room
            tk.Button(self.frm_btn_chatrooms, text="General", 
                      command=None, height=1, width=20,
                      font=self.default_font, pady=2)
        ]

        # Display each chat room
        chatroom_count = 0
        for chatroom in self.lst_btn_chatrooms:
            chatroom.grid(row=chatroom_count, column=0, sticky=tk.N, pady=2)
            chatroom_count += 1

    def initialize_messages(self):
        """
        Initialize the layout of the messages list.
        """

        # Frame to hold the following widgets in
        self.frm_messages = tk.Frame(self.master)
        self.frm_messages.grid(row=0, column=1, pady=10)
        self.frm_messages.configure(bg="gray20")

        # Message Display Window
        self.txt_messages = tk.Text(self.frm_messages, height=25, width=70, font=self.default_font, pady=2)
        self.txt_messages.grid(row=0, column=0, columnspan=2, sticky=tk.N)
        self.txt_messages.config(state=tk.DISABLED)

        # Send Message Box
        self.txt_send_message = tk.Text(self.frm_messages, height=1, width=64, font=self.default_font, pady=2)
        self.txt_send_message.grid(row=1, column=0, sticky=tk.W)
        self.txt_send_message.bind('<Return>', self.txt_send_message_return)

        # Send Message Button
        self.btn_send_message = tk.Button(self.frm_messages, text="Send",
                                          command=self.btn_send_message_click,
                                          font=self.default_font)
        self.btn_send_message.grid(row=1, column=1, sticky=tk.W)

    def initialize_users(self):
        """
        Initialize the layout of the user list.
        """

        # Frame to hold the following widgets in
        self.frm_users = tk.Frame(self.master)
        self.frm_users.grid(row=0, column=2, sticky=tk.NE, padx=10, pady=10)
        self.frm_users.configure(bg="gray20")

        # Label for the user list
        self.lbl_users = tk.Label(self.frm_users, text="Users", font=self.header_font)
        self.lbl_users.grid(row=0, column=0)
        self.lbl_users.configure(bg="gray20", fg="white")

        # List of users
        # Need to populate with real users eventually
        self.lst_box_users = tk.Listbox(self.frm_users)
        self.lst_box_users.grid(row=1, column=0)
        for user in ["Matt", "Sterling", "Spencer", "Rabjot"]:
            self.lst_box_users.insert(tk.END, user)

    def btn_create_chatroom_click(self):
        """
        Creates a window for the create chat room command.
        """

        self.wnd_create_chatroom = tk.Toplevel(self.master)
        self.wnd_create_chatroom.wm_title("Create Chat Room")
        self.wnd_create_chatroom.configure(bg="gray20")
        self.wnd_create_chatroom.resizable(0,0)

        # Set size of window and central start location
        w = 300
        h = 125
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw/2) - (w/2)
        y = (sh/2) - (h/2)
        self.wnd_create_chatroom.geometry('%dx%d+%d+%d' % (w, h, x, y))

        # Label for the create chat room window
        self.lbl_create_chatroom = tk.Label(self.wnd_create_chatroom, text="Create Chat Room", font=self.header_font)
        self.lbl_create_chatroom.grid(row=0, column=0, padx=10, pady=5)
        self.lbl_create_chatroom.configure(bg="gray20", fg="white")
        
        # Text for the chat room name
        self.txt_chatroom_name = tk.Text(self.wnd_create_chatroom, height=1, width=35, font=self.default_font)
        self.txt_chatroom_name.grid(row=1, column=0, padx=10, pady=5)

        # Button to confirm chat room name
        self.btn_confirm_creation = tk.Button(self.wnd_create_chatroom, text="Confirm",
                                              command=self.btn_confirm_creation_click,
                                              font=self.default_font)
        self.btn_confirm_creation.grid(row=2, column=0, sticky=tk.E, padx=10, pady=5)
    
    def btn_confirm_creation_click(self):
        """
        Confirms chat room creation and closes the window.
        """

        # Prepare create command
        cmd = '/create {}'.format(self.txt_chatroom_name.get('1.0', '1.end'))
        self.send_to_client(cmd)

        # Close the create chat room window
        self.wnd_create_chatroom.destroy()

    def btn_delete_chatroom_click(self):
        """
        Handles a click on the delete chat room button.
        """
        pass
    
    def insert_text(self, text):
        """
        Allows only the code to update the text message box.
        """

        self.txt_messages.configure(state=tk.NORMAL)
        self.txt_messages.insert('end', text)
        self.txt_messages.configure(state=tk.DISABLED)

    def txt_send_message_return(self, event):
        """
        Handles event of a return being entered to the message box.
        """

        self.btn_send_message_click()
        return 'break'  # Stops the <Return> event from updating the text box with a newline

    def btn_send_message_click(self):
        """
        Handles a click on the send message button.
        """

        self.send_to_client(self.txt_send_message.get('1.0', '1.end'))
        self.txt_send_message.delete('1.0', '1.end')

    def send_to_client(self, body: str):
        """
        Sends data back to the client process
        """

        client.stdin.write("{}\n".format(body).encode())
        client.stdin.flush()
        print(self.txt_send_message.get('1.0', '1.end'))

    def handle_data(self):
        """
        Handles data from the client process's stdout
        """

        while True:
            line = client.stdout.readline()
            self.insert_text(line)

if __name__ == '__main__':
    # Start the client
    client = Popen(['python', 'client.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=False)

    # Initilize the GUI
    application = ClientGUI(client)

    # Start the thread which handles new data from the client
    clientHandler = Thread(target=application.handle_data)
    clientHandler.start()

    # Start the GUI mainloop
    application.mainloop()