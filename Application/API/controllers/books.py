from mongoengine import connect
from typing import Optional
from fastapi import HTTPException, status
import requests
import re

from models.books import Book, User_Review
from models.users import User, Book_Review


connect(db='book_rec', host='mongo', port=27017)


async def get_ol_data(isbn_10: str):
    """
    Gets the book's Open Library Work ID and title for the given ISBN 10.

    Args:
        isbn_10 (str): the book's ISBN 10.

    ---------------------------------------------------------------------

    Returns:
        ol_work_id (str): the book's Open Library ID.

        title: the book's title.
    """

    # Call the Open Library ISBN API too get the book's information:
    res = requests.get(f'https://openlibrary.org/isbn/{isbn_10}.json').json()

    try:
        ol_work_id = re.findall(
            r'/works/([\w|\d]+)', res['works'][0]['key']
        )[0]
        title = res['title']
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No book associated with the given ISBN 10 was found.'
        )
    return ol_work_id, title


async def register_book(
    ol_work_id: str,
    isbn_10: str,
    title: str,
    review: Optional[dict] = None
):
    """
    Registers a book in the database. This function should only be called if
    the given book is not already present in the database. If the optional
    review parameter is passed, the review is registered in both the users and
    books collections.

    Args: ol_work_id (str): the book's Open Library ID.

        isbn_10 (str): the book's ISBN 10.

        title: the book's title.

        review (dict): optional user review to be registered along with the
                       book. It must be a dictionary with keys `user` (a `User`
                       document as used by the database) and `rating` (an
                       integer between 0 and 10).

    ----------------------------------------------------------

    Returns: None
    """

    if not review:
        # If a review wasn't provided:
        book = Book(ol_work_id=ol_work_id, isbn_10_list=[isbn_10], title=title)
    else:
        # If a review was provided:
        user = review['user']

        book = Book(ol_work_id=ol_work_id,
                    isbn_10_list=[isbn_10],
                    title=title,
                    reviews=[
                        User_Review(
                            user_id=user.id,
                            rating=review['rating']
                        )
                    ])

        user.reviews.append(Book_Review(ol_work_id=book.ol_work_id,
                                        rating=review['rating']))
        user.save()

    book.save()


async def append_review(book: Book, review: dict):
    """
    Adds a book review in the database for both the users and books collections
    assuming the given book already exists in the database.

    Args:
        book (Book): a `Book` document as used by the database.

        review (dict): user review to be registered. It must be a dictionary
                       with keys `user` (a `User` document as used by the
                       database) and `rating` (an integer between 0 and 10).

    ----------------------------------------------------------

    Returns:
        None
    """

    user = review['user']
    user.reviews.append(Book_Review(ol_work_id=book.ol_work_id,
                                    rating=review['rating']))
    user.save()

    book.reviews.append(User_Review(user_id=user.id,
                                    rating=review['rating']))
    book.save()


async def register_review(isbn_10: str, review: dict):
    """
    Registers a book review in the database for both the users and books
    collections regardless of whether the book already exists in the database
    or not.

    Args:
        isbn_10 (str): the book's ISBN 10.

        review (dict): user review to be registered. It must be a dictionary
                       with keys `user` (a `User` document as used by the
                       database) and `rating` (an integer between 0 and 10).

    ----------------------------------------------------------

    Returns:
        None
    """

    # Try to retrieve the book from the database using the given ISBN 10:
    book = Book.objects.filter(isbn_10_list__contains=isbn_10)

    if not book:
        # If the book can't be found in the database via the provided ISBN 10,
        # get the Open Library Work ID and search again:
        ol_work_id, title = await get_ol_data(isbn_10)
        book = Book.objects.filter(ol_work_id=ol_work_id)

        if not book:
            # If the book is not in the database, register it along with the
            # review:
            await register_book(ol_work_id, isbn_10, title, review)
        else:
            # If the book is in the database, add the review to the existing
            # record and update the list of ISBN 10 identifiers:
            book = book[0]
            await append_review(book, review)
            book.isbn_10_list.append('isbn_10')

    else:
        # If the book is in the database, add the review to the existing
        # record:
        await append_review(book[0], review)


def book_avg_rating(book: Book):
    """
    Returns the average rating of a book.
    """

    reviews = book.reviews
    length = len(reviews)

    return sum([rev.rating for rev in reviews])/length


async def list_books(user: User):
    """
    Fetches a list of all the books provided the requesting user has admin
    permissions.

    Args:
        user (User): user object as specified through the users model.

    -----------------------------------------------------------------------

    Returns:
        book_list (List[dict]): list of book objects.
    """

    if user.permissions == 'admin':

        book_list = [
            {
                'ol_work_id': str(book.id),
                'title': book.title,
                'avg_rating': book_avg_rating(book)
            }
            for book in Book.objects
        ]

        return book_list

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='The user does not have permissions to make this request',
            headers={'WWW-Authenticate': 'Bearer'}
        )
