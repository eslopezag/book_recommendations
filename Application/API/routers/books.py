from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from controllers import books


router = APIRouter(prefix='/books', tags=['books'])


@router.post('/register_review')
async def register_review(
    isbn_10: str = Form(..., min_length=10, max_length=10),
    rating: int = Form(..., ge=0, le=10)
):
    books.register_review(isbn_10)
