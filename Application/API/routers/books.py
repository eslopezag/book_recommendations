from fastapi import APIRouter, Form, Depends

from controllers import books
from controllers.users import get_current_user
from models.users import User


router = APIRouter(prefix='/books', tags=['books'])


@router.post('/register-review')
async def register_review(
    isbn_10: str = Form(..., min_length=10, max_length=10),
    rating: int = Form(..., ge=0, le=10),
    user: User = Depends(get_current_user)
):
    review = {'user': user, 'rating': rating}
    await books.register_review(isbn_10, review)


@router.get('/list-books')
async def list_books(user: User = Depends(get_current_user)):
    return await books.list_books(user)
