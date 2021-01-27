from models.users import User


def create_user(username: str, password: str):
    user = User(username, password)
    user.save()


def login(username: str, password: str):
    user = User.get(username=username)
    if user.password == password:
        pass
