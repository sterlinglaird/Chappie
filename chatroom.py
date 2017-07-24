from user import User
from command import Command

class Chatroom:
    def __init__(self, name: str, owner: User, default=False):
        self.name = name
        self.owner = owner
        self.default = default
        self.users = {}
        self.blocked = {}

    def add_user(self, user: User):
        self.users[user.alias] = user

    def rem_user(self, user: User):
        self.users.pop(user.alias, None)

    def  block_user(self, user: User):
        self.blocked[user.alias] = user

    def unblock_user(self, user: User):
        self.blocked.pop(user.alias, None)

    def send_all(self, cmd: Command):
        for user in list(self.users):
            try:
                cmd.send(self.users[user].socket)
            except:
                print("{} lost connection".format(self.users[user].alias))
                self.users.pop(user, None)