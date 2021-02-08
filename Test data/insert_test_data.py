"""
This script inserts the `test data in `reviews_to_insert.csv` to the database
through the API by signing up users (with random usernames provided by the
Random User API) and registering their book reviews.

To run this script, the mongoDB container must have its 27017 port exposed and
mapped to the host's own 27017 port. This is necessary because the database is
used to keep track of the users that have been already processed.
"""

import requests
import pandas as pd
import sys
from mongoengine import connect, Document, IntField, ObjectIdField
from mongoengine.errors import NotUniqueError

# Import the User document class from the models:
sys.path.insert(1, '../Application/API/models/')
from users import User

# Connect to the `book_rec` database:
connect('book_rec', host='localhost', port=27017)


# Define a mongoDB collection that stores information about the map from users
# in `reviews_to_insert.csv` to users in the users collection:
class UserMap(Document):
    # user_id in the test data:
    test_user_id = IntField(required=True, unique=True)
    # user_id in mongoDB:
    mongo_user_id = ObjectIdField(required=True, unique=True)

    @classmethod
    def find_one(cls, **kwargs):
        """
        Fetches an object in the collection uniquely identified by `kwargs` or
        returns None if said object doesn't exist.
        """

        res = cls.objects.filter(**kwargs)
        if len(res) == 0:
            return None
        elif len(res) == 1:
            return res[0]
        else:
            raise NotUniqueError(
                'The specified query corresponds to more than one object.')


# Load test data:
reviews = pd.read_csv('./reviews_to_insert.csv')

users = reviews['user_id'].unique()
length = len(users)

for i, u in enumerate(users):
    # Don't process this user if it has already been processed:
    if UserMap.find_one(test_user_id=u):
        continue

    print(f'Registering reviews for user {i + 1} of {length}...')

    # Define user credentials (randon username and fixed password):
    username = requests.get('https://randomuser.me/api/') \
        .json()['results'][0]['login']['username']
    password = 'password'

    # Sign the user up and get their authentication token:
    res = requests.post(
        'http://localhost:3000/users/signup',
        data={'username': username, 'password': 'password'}
    )
    token = res.json()['access_token']

    # Find the user's id in mongoDB:
    mongo_id = User.objects.filter(username=username)[0].id

    # Register the user in the usermaps collection:
    umap = UserMap(test_user_id=u, mongo_user_id=mongo_id)
    umap.save()

    # Get reviews for this user:
    revs = reviews[reviews['user_id'] == u]

    for review in revs.itertuples(index=False):
        review.isbn_10
        review.rating

        res = requests.post(
            'http://localhost:3000/books/register-review',
            data={'isbn_10': review.isbn_10, 'rating': review.rating},
            headers={'Authorization': f'Bearer {token}'}
        )
