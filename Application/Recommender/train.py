from mongoengine import connect

from models.books import Book
from models.users import User


connect(db='book_rec', host='mongo', port=27017)
