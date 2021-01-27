from fastapi import APIRouter, Form

from controllers import users

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/signup')
async def create_user(username: str = Form(...), password: str = Form(...)):
    users.create_user(username, password)


@router.post('/login')
async def login(username: str = Form(...), password: str = Form(...)):
    users.login(username, password)
