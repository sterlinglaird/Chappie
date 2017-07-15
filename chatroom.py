from user import User

class Chatroom:
    def __init__(self, name: str, owner: User, default=False):
        self.name = name
        self.owner = owner
        self.default = default
        self.users = {}

    def add_user(self, user: User):
        self.users[user.alias] = user

    def rem_user(self, user: User):
        self.users.pop(user.alias, None)
