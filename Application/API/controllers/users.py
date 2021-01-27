from mongoengine import connect

from models.users import User


connect(db='book_rec', host='mongo', port=27017)


async def create_user(username: str, password: str):
    user = User(username, password)
    user.save()


async def login(username: str, password: str):
    user = User.get(username=username)
    if user.password == password:
        pass
