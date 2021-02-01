from mongoengine import connect
from passlib.context import CryptContext

from models.users import User


connect(db='book_rec', host='mongo', port=27017)

pwd_ctxt = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
    bcrypt__rounds=13
)


async def create_user(username: str, password: str):
    assert 6 <= len(password) <= 20, \
        'Password should be between 6 and 20 characters long'
    hash = pwd_ctxt.hash(password)
    user = User(username=username, hashed_password=hash)
    user.save()


async def login(username: str, password: str):
    user = await User.get(username=username)
    if pwd_ctxt.verify(password, user.hashed_password):
        pass


async def list_users():
    return [
        {
            'id': str(user.id),
            'username': user.username,
            'hashed_password': user.hashed_password
        }
        for user in User.objects
    ]
