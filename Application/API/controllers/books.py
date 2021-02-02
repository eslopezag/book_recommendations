from mongoengine import connect
from typing import Optional
import requests
import re

from models.books import Book, User_Review
from models.users import Book_Review


connect(db='book_rec', host='mongo', port=27017)


async def register_book(
    isbn_10: str,
    review: Optional[dict] = None
):
    """
    Registers a book in the database by using the ISBN 10 to get the book's
    information from Open Library's ISBN API and returns the book's Open
    library work ID. This function should only be called if the given book is
    not already present in the database. If the optional review parameter is
    passed, the review is registered in both the users and books collections.

    Args:
        isbn_10 (str): the book's ISBN 10.

        review (dict): optional user review to be registered along with the
                       book. It must be a dictionary with keys `user` (a `User`
                       document as used by the database) and `rating` (an
                       integer between 0 and 10).

    ----------------------------------------------------------

    Returns:
        None
    """

    res = requests.get(f'https://openlibrary.org/isbn/{isbn_10}.json').json()
    ol_work_id = re.findall(
        r'/works/([\w|\d]+)', res['works'][0]['key'])[0]
    title = res['title']

    if not review:
        # If a review wasn't provided:
        book = Book(ol_work_id=ol_work_id, isbn_10=isbn_10, title=title)
    else:
        # If a review was provided:
        user = review['user']

        book = Book(ol_work_id=ol_work_id,
                    isbn_10=isbn_10,
                    title=title,
                    reviews=[
                        User_Review(
                            user_id=user.id,
                            rating=review['rating']
                        )
                    ])

        user.reviews.append(Book_Review(ol_work_id=book.ol_work_id,
                                        isbn_10=isbn_10,
                                        rating=review['rating']))
        user.save()

    book.save()


async def register_review(
    isbn_10: str,
    review: dict
):
    """
    Registers a book review in the database for both the users and books
    collections.

    Args:
        isbn_10 (str): the book's ISBN 10.

        review (dict): user review to be registered. It must be a dictionary
                       with keys `user` (a `User` document as used by the
                       database) and `rating` (an integer between 0 and 10).

    ----------------------------------------------------------

    Returns:
        None
    """

    # Try to retrieve the book from the database:
    book = Book.objects.filter(isbn_10=isbn_10)

    if not book:
        # If the book is not in the database:
        await register_book(isbn_10, review)
    else:
        # If the book is in the database:
        book = book[0]

        user = review['user']
        user.reviews.append(Book_Review(ol_work_id=book.ol_work_id,
                                        isbn_10=isbn_10,
                                        rating=review['rating']))
        user.save()

        book.reviews.append(User_Review(user_id=user.id,
                                        rating=review['rating']))
        book.save()
