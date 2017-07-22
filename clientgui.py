import tkinter as tk
import tkinter.font as tkFont
from threading import Thread
from subprocess import Popen, PIPE

from command import Command
import util

class ClientGUI(tk.Frame):
    def __init__(self, client: Popen):
        """
        Initialize the client GUI.
        """

        # Client specific properties
        self.client = client
        self.chatroom = None
        self.alias = None
        self.lst_all_chatrooms = []
        self.bool_lst_all_chatrooms_updated = False

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
        h = 460
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
                                             font=self.default_font, relief=tk.FLAT, bg='white')
        self.btn_create_chatroom.grid(row=1, column=0, pady=2)

        # Delete chat room button
        self.btn_delete_chatroom = tk.Button(self.frm_chatrooms, text="Delete Chat Room", 
                                             command=self.btn_delete_chatroom_click, height=1, width=20, 
                                             font=self.default_font, relief=tk.FLAT, bg='white')
        self.btn_delete_chatroom.grid(row=2, column=0, pady=2)

        # Add a frame for the list of chat room buttons
        self.frm_btn_chatrooms = tk.Frame(self.frm_chatrooms, pady=5)
        self.frm_btn_chatrooms.grid(row=3, column=0)
        self.frm_btn_chatrooms.configure(bg="gray20")

        # General chat room button
        self.btn_general_chatroom = tk.Button(self.frm_btn_chatrooms, text="General", 
                                         height=1, width=20, font=self.default_font, 
                                         pady=2, relief=tk.FLAT, bg='LightSkyBlue1', state=tk.DISABLED)
        self.btn_general_chatroom.configure(command=lambda b=self.btn_general_chatroom: self.btn_chatroom_click(b))

        # List of chat rooms as buttons
        # Initialize with the general chat room
        self.lst_btn_chatrooms = [
            self.btn_general_chatroom
        ]

        # Get the list of chatrooms, create a button for each not currently a button
        cmd_get_chatrooms = '/get_chatrooms'
        self.send_to_client(cmd_get_chatrooms)

    def initialize_messages(self):
        """
        Initialize the layout of the messages list.
        """

        # Frame to hold the following widgets in
        self.frm_messages = tk.Frame(self.master)
        self.frm_messages.grid(row=0, column=1, pady=10)
        self.frm_messages.configure(bg="gray20")

        # Message Display Window
        self.txt_messages = tk.Text(self.frm_messages, height=25, width=70, font=self.default_font)
        self.txt_messages.grid(row=0, column=0, columnspan=2, sticky=tk.N, pady=2)
        self.txt_messages.config(state=tk.DISABLED)

        # Send Message Box
        self.txt_send_message = tk.Text(self.frm_messages, height=1, width=64, font=self.default_font, pady=5)
        self.txt_send_message.grid(row=1, column=0, sticky=tk.W, pady=3, padx=3)
        self.txt_send_message.bind('<Return>', self.txt_send_message_return)

        # Send Message Button
        self.btn_send_message = tk.Button(self.frm_messages, text="Send",
                                          command=self.btn_send_message_click,
                                          font=self.default_font, relief=tk.FLAT, bg='white')
        self.btn_send_message.grid(row=1, column=1, sticky=tk.W, pady=3, padx=2)

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
        self.lst_box_users = tk.Listbox(self.frm_users, bd=0)
        self.lst_box_users.grid(row=1, column=0)

    def btn_chatroom_click(self, btn_chatroom):
        """
        Joins the chat room clicked on.
        """

        # Make the previous chatroom button active again
        prev_btn_chatroom = next((btn for btn in self.lst_btn_chatrooms if btn['state'] == 'disabled'), None)
        if prev_btn_chatroom != None:
            prev_btn_chatroom.config(state=tk.ACTIVE, bg='white')

        # Disable the chatroom button clicked on
        btn_chatroom.configure(state=tk.DISABLED, bg='LightSkyBlue1')

        # Send join command
        joinCmd = '/join {}'.format(btn_chatroom['text'])
        self.send_to_client(joinCmd)

        # Send list user command
        lsCmd = '/list_users {}'.format(btn_chatroom['text'])
        self.send_to_client(lsCmd)

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
                                              font=self.default_font, relief=tk.FLAT)
        self.btn_confirm_creation.grid(row=2, column=0, sticky=tk.E, padx=10, pady=5)
    
    def btn_confirm_creation_click(self):
        """
        Confirms chat room creation and closes the window.
        """

        # Send create command
        cmd = '/create {}'.format(self.txt_chatroom_name.get('1.0', '1.end'))
        self.send_to_client(cmd)

        # Close the create chat room window
        self.wnd_create_chatroom.destroy()
    
    def create_chatroom_btn(self, chatroom_name):
        """
        Creates a button for a newly created chat room.
        """

        # Chat room button
        btn_chatroom = tk.Button(self.frm_btn_chatrooms, text=chatroom_name, 
                                 height=1, width=20, font=self.default_font, 
                                 pady=2, relief=tk.FLAT, bg='white')
        btn_chatroom.configure(command=lambda b=btn_chatroom: self.btn_chatroom_click(b))

        # Add it to the list of buttons
        self.lst_btn_chatrooms.append(btn_chatroom)
        self.update()
    
    def btn_delete_chatroom_click(self):
        """
        Deletes the current chat room if the user is the owner.
        """

        # Get the current chat room
        curr_btn_chatroom = next((btn for btn in self.lst_btn_chatrooms if btn['state'] == 'disabled'), None)

        # TODO: Check if the user is the owner
        if curr_btn_chatroom['text'] == 'General':
            self.insert_text("Error: You cannot delete the General chat room.\n")
            return

        # Send delete command
        cmd = '/delete {}'.format(curr_btn_chatroom['text'])
        self.send_to_client(cmd)

        self.btn_general_chatroom.configure(state=tk.DISABLED, bg='LightSkyBlue1')
        
    def delete_chatroom_btn(self, chatroom_name):
        """
        Deletes the corresponding chat room button.
        """

        # Get the chat room button
        curr_btn_chatroom = next((btn for btn in self.lst_btn_chatrooms if btn['text'] == chatroom_name), None)

        # Remove from the list of buttons
        self.lst_btn_chatrooms.remove(curr_btn_chatroom)
        curr_btn_chatroom.destroy()
        self.update()

    def add_user(self, alias):
        self.lst_box_users.insert('end', alias)

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

    def update(self):
        """
        Updates the GUI.
        """

        # Create a button for each new chat room
        lst_names_btn_chatrooms = (btn['text'] for btn in self.lst_btn_chatrooms)
        lst_new_chatrooms = (cht for cht in self.lst_all_chatrooms if cht not in lst_names_btn_chatrooms)

        for new_chatroom in lst_new_chatrooms:
            self.create_chatroom_btn(new_chatroom)

        # Display each chat room
        chatroom_count = 0
        for chatroom in self.lst_btn_chatrooms:
            chatroom.grid(row=chatroom_count, column=0, sticky=tk.N, pady=2)
            chatroom_count += 1

    def send_to_client(self, body: str):
        """
        Sends data back to the client process.
        """

        lst_parsed_input = body.split(' ', 1)

        cmd_name = lst_parsed_input[0] if len(lst_parsed_input) >= 1 else ''
        cmd_body = lst_parsed_input[1] if len(lst_parsed_input) >= 2 else ''

        cmd = Command()

        if cmd_name == '/message':
            cmd.init_send_message(cmd_body, self.chatroom)
        elif cmd_name == '/set_alias':
            self.alias = cmd_body
            cmd.init_set_alias(cmd_body)
        elif cmd_name == '/quit':
            cmd.init_disconnect()
        elif cmd_name == '/join':
            cmd.init_join_chatroom(cmd_body)
        elif cmd_name == '/create':
            cmd.init_create_chatroom(cmd_body)
        elif cmd_name == '/delete':
            cmd.init_delete_chatroom(cmd_body)
        elif cmd_name == '/list_users':
            cmd.init_list_users(cmd_body)
        else:
            print("\"{}\" is not a valid command.".format(cmd_name))
            return

        self.client.stdin.write("{}\n".format(cmd.stringify()).encode())
        self.client.stdin.flush()

        print(cmd.stringify().encode())

    def handle_data(self):
        """
        Handles data from the client process' stdout.
        """

        while True:
            line = client.stdout.readline()
            received = line.decode("utf-8").strip()
            print('Receiving: ' + received)

            try:
                cmd = Command(received)
                self.handle_command(cmd)
            except:
                self.insert_text(line)

    def handle_command(self, cmd: Command):
        line = ""

        if cmd.type == 'message':
            line += "{}: {}".format(cmd.creator, cmd.body)
        elif cmd.type == 'connect':
            line += "Connection Successful!\nPlease enter  an alias (/set_alias <alias>):"
        elif cmd.type == 'alias':
            if cmd.creator == self.alias:
                self.chatroom = util.defaultChatroom
                line += "Alias '{}' confirmed! ".format(cmd.creator)
            else:
                line += "'{}' joins Chat. ".format(cmd.creator)
            self.add_user(cmd.creator)
        elif cmd.type == 'disconnect':
            line += "{} disconnected".format(cmd.creator)
        elif cmd.type == 'join_chatroom':
            if cmd.creator == self.alias:
                self.chatroom = cmd.body
                self.lst_box_users.delete(0, 'end')
                line += "{} joined chatroom {}".format(cmd.creator, cmd.body)
            self.add_user(cmd.creator)
        elif cmd.type == 'create_chatroom':
            line += "{} created chatroom {}".format(cmd.creator, cmd.body)
            self.create_chatroom_btn(cmd.body)
        elif cmd.type == 'delete_chatroom':
            line += "{} deleted chatroom {}".format(cmd.creator, cmd.body)
        elif cmd.type == 'error':
            line += "Error: {}".format(cmd.body)

        self.insert_text("{}\n".format(line))
        
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