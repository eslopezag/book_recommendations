from mongoengine import connect
import requests
import re

from models.books import Book


connect(db='book_rec', host='mongo', port=27017)


async def register_book(isbn_10: str):
    """
    Registers a book in the database by using the ISBN 10 to get the book's
    information from Open Library's ISBN API

    Args:
        isbn_10 (str): the book's ISBN 10.

    ----------------------------------------------------------

    Returns:
        None
    """

    res = requests.get(f'https://openlibrary.org/isbn/{isbn_10}.json').json()
    ol_work_id = re.findall(
        r'/works/([\w|\d]+)', res['works'][0]['key'])[0]
    title = res['title']
    book = Book(ol_work_id, isbn_10, title)
    book.save()
