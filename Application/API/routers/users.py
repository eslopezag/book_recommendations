from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from models.users import User
from controllers import users
from models.miscellaneous import Token

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/signup', response_model=Token)
async def create_user(form_data: OAuth2PasswordRequestForm = Depends()):
    await users.create_user(form_data.username, form_data.password)
    return await users.login(form_data.username, form_data.password)


@router.post('/login', response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    await users.login(form_data.username, form_data.password)


@router.get('/list_users', response_class=JSONResponse)
async def list_users(user: User = Depends(users.get_current_user)):
    user_list = await users.list_users(user)
    return user_list
