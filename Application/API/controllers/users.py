from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from mongoengine import connect
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from configparser import ConfigParser

from models.users import User

# Read the secret configuration file and obtain the secret key and the
# algorithm to sign the JSON web tokens and their expiration time:
config = ConfigParser()
config.read('/secrets/config.cfg')

JWT_SECRET = config['JWT']['SECRET_KEY']
JWT_ALGORITHM = config['JWT']['ALGORITHM']
JWT_EXPIRE_MINS = config['JWT']['EXPIRE_MINUTES']

HASHED_MASTER_PASSWORD = config['ADMIN']['HASHED_MASTER_PASSWORD']

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

connect(db='book_rec', host='mongo', port=27017)

pwd_ctxt = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
    bcrypt__rounds=13
)


async def create_access_token(
    data: dict,
    expire_delta: Optional[timedelta] = int(JWT_EXPIRE_MINS)
):
    expire = datetime.utcnow() + timedelta(minutes=expire_delta)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Define the invalid credentials exception:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to decode the authentication token:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Try to find the given user_id in the users collection:
    user = User.objects.filter(id=user_id)
    if len(user) != 1:
        raise credentials_exception
    return user[0]


async def create_user(username: str, password: str):
    assert 3 <= len(username) <= 20, \
        'Username should be between 3 and 20 characters long'
    assert 6 <= len(password) <= 20, \
        'Password should be between 6 and 20 characters long'
    hash = pwd_ctxt.hash(password)
    user = User(username=username, hashed_password=hash)
    user.save()


async def create_admin(username: str, password: str, master_password: str):
    """
    Creates a user with "admin" privileges. The user is required to provide the
    backend's master password to be created as an admin.

    Args:
        username (str): username that will identify the user.

        password (str): user's password.

        master_password (str): backend's master password.

    ---------------------------------------------------------------------------

    Returns:
        None
    """

    # Define the invalid credentials exception:
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect master password"
        )

    assert 3 <= len(username) <= 20, \
        'Username should be between 3 and 20 characters long'
    assert 6 <= len(password) <= 20, \
        'Password should be between 6 and 20 characters long'

    # Verify user's password and get access token:
    if pwd_ctxt.verify(master_password, HASHED_MASTER_PASSWORD):
        hash = pwd_ctxt.hash(password)
        user = User(
            username=username,
            hashed_password=hash,
            permissions='admin'
        )
        user.save()
    else:
        raise credentials_exception


async def login(username: str, password: str):
    # Define the invalid credentials exception:
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look for user in the database:
    user = User.objects.filter(username=username)

    if len(user) != 1:
        raise credentials_exception

    user = user[0]

    # Verify user's password and get access token:
    if pwd_ctxt.verify(password, user.hashed_password):
        access_token = await create_access_token({'sub': str(user.id)})
    else:
        raise credentials_exception

    return {"access_token": access_token, "token_type": "bearer"}


async def user_info(user: User):
    info = {
                'id': str(user.id),
                'username': user.username,
            }

    return info


async def list_users(user: User):
    """
    Fetches a list of all the users provided the requesting user has admin
    permissions.

    Args:
        user (User): user object as specified through the users model.

    -----------------------------------------------------------------------

    Returns:
        user_list (List[dict]): list of user objects.
    """

    if user.permissions == 'admin':

        user_list = [
            {
                'id': str(user.id),
                'username': user.username,
                'hashed_password': user.hashed_password
            }
            for user in User.objects
        ]

        return user_list

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user does not have permissions to make this request",
            headers={"WWW-Authenticate": "Bearer"},
        )
