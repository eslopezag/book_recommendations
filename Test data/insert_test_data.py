"""
This script inserts
"""

import requests
import pandas as pd

reviews = pd.read_csv('./reviews_to_insert.csv')
users = reviews['user_id'].unique()

for u in users:

    # Define user credentials (randon username and fixed password):
    useranme = requests.get('https://randomuser.me/api/') \
        .json()['results'][0]['login']['username']
    password = 'password'

    # Get user's authentication token:
    res = requests.get()

    # Get reviews for this user:
    revs = reviews[reviews['user_id'] == u]

    for review in revs.itertuples(index=False):
        review.isbn_10
        review.rating
