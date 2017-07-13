import tkinter as tk

# Custom Modules
from client import Client

class ClientGUI(tk.Frame):
    def __init__(self, client):
        """
        Initialize the client GUI.
        """

        self.master = tk.Tk()
        super().__init__(self.master)
        self.initialize_window()

        # Message Window
        self.messages = tk.Text(self.master)
        self.messages.pack()

        self.input_user = tk.StringVar()

        # Message Box
        self.input_field = tk.Entry(self.master, text=self.input_user)
        self.input_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_field.bind("<Return>", self.enter_pressed)
    
    def enter_pressed(self, event):
        input_get = self.input_field.get()
        print(input_get)

        self.messages.insert(tk.INSERT, '%s\n' % input_get)
        self.input_user.set('')

        return "break"

    def initialize_window(self):
        self.master.title("Chat Application")

        # Set size of window and central start location
        w = 800
        h = 600
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw/2) - (w/2)
        y = (sh/2) - (h/2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

if __name__ == '__main__':
    # Intialize the client
    client = Client()
    client.start()

    # Initilize the GUI
    application = ClientGUI(client)
    application.mainloop()