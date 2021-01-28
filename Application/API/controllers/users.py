from mongoengine import connect
import hashlib

from models.users import User


connect(db='book_rec', host='mongo', port=27017)


async def create_user(username: str, password: str):
    assert 6 <= len(password) <= 20, \
        'Password should be between 6 and 20 characters long'
    hash = hashlib.sha256(password.encode())
    user = User(username=username, hashed_password=hash.hexdigest())
    user.save()


async def login(username: str, password: str):
    hash = hashlib.sha256(password.encode())
    user = await User.get(username=username)
    if user.hashed_password == hash.hexdigest():
        pass


# async def list_users():
#     return {
#         'user_list': [
#             {
#                 'id': str(u.id),
#                 'username': u.username,
#                 'hashed_password': u.hashed_password
#             }
#             for u in User.objects
#         ]
#     }


async def list_users():
    return [
        {
            'id': str(u.id),
            'username': u.username,
            'hashed_password': u.hashed_password
        }
        for u in User.objects
    ]
