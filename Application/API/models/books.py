from mongoengine import (Document, StringField, EmbeddedDocument,
                         EmbeddedDocumentListField, IntField, ObjectIdField)


class User_Review(EmbeddedDocument):
    """
    Defines the document type used to store user reviews in the review field of
    book documents.
    """

    user_id = ObjectIdField(required=True)
    rating = IntField(required=True, min_value=0, max_value=10)


class Book(Document):
    ol_work_id = StringField(
        required=True,
        min_length=3,
        primary_key=True
    )
    isbn_10 = StringField(
        required=True,
        min_length=10,
        max_length=10,
        unique=True
    )
    title = StringField(required=True)
    reviews = EmbeddedDocumentListField(User_Review)
