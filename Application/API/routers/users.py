from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from controllers import users

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/signup')
async def create_user(username: str = Form(...), password: str = Form(...)):
    await users.create_user(username, password)


@router.post('/login')
async def login(username: str = Form(...), password: str = Form(...)):
    await users.login(username, password)


@router.get('/list_users', response_class=JSONResponse)
async def list_users():
    user_list = await users.list_users()
    return user_list
