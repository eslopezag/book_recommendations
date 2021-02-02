from mongoengine import (Document, StringField,
                         IntField, EmbeddedDocument, EmbeddedDocumentListField)


class Book_Review(EmbeddedDocument):
    """
    Defines the document type used to store book reviews in the review field of
    user documents.
    """

    ol_work_id = StringField(required=True, min_length=3)
    isbn_10 = StringField(required=True, min_length=10, max_length=10)
    rating = IntField(required=True, min_value=0, max_value=10)


class User(Document):
    username = StringField(required=True,
                           min_length=3,
                           max_length=20,
                           unique=True
                           )
    hashed_password = StringField(required=True, min_length=60, max_length=60)
    reviews = EmbeddedDocumentListField(Book_Review)
    permissions = StringField(
        required=True,
        choices=['admin', 'standard'],
        default='standard')
