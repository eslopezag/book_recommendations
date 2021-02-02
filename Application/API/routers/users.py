from fastapi import APIRouter, Depends, Form
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


@router.post('/admin-signup', response_model=Token)
async def create_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    master_password: str = Form(..., min_length=6)
):
    await users.create_admin(
        form_data.username,
        form_data.password,
        master_password
    )
    return await users.login(form_data.username, form_data.password)


@router.post('/login', response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = await users.login(form_data.username, form_data.password)
    return token


@router.get('/me', response_class=JSONResponse)
async def user_info(user: User = Depends(users.get_current_user)):
    info = await users.user_info(user)
    return info


@router.get('/list-users', response_class=JSONResponse)
async def list_users(user: User = Depends(users.get_current_user)):
    user_list = await users.list_users(user)
    return user_list
