from mongoengine import Document, StringField, EmbeddedDocument


class User(Document):
    username = StringField(required=True, max_length=20, unique=True)
    password = StringField(required=True, min_length=6, max_length=20)
    reviews = EmbeddedDocument()
