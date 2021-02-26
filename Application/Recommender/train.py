import numpy as np
from mongoengine import connect

from models.books import Book
from models.users import User


def train_recommender(threshold):
    max_delta = float('inf')  # max change in embeddings

    while max_delta > threshold:
        max_delta = float('-inf')  # reset max_delta

        # Update user embeddings:
        for user in User.objects:

            rated_books = {
                book.id: book.embedding for book in
                Book.objects(
                    ol_work_id__in={rev.ol_work_id for rev in user.reviews})
            }

            # Regressor matrix:
            M = np.array(
                [rated_books[rev.ol_work_id] for rev in user.reviews]
            )

            # Ratings:
            ratings = np.array([rev.rating for rev in user.reviews])

            new_embedding = np.linalg.lstsq(M, ratings, rcond=None)[0]

            max_delta = max(
                max_delta,
                np.max(np.abs(user.embedding - new_embedding))
            )

            user.embedding = new_embedding.tolist()
            user.save()

        # Update book embeddings:
        for book in Book.objects:

            user_ratings = {
                user.id: user.embedding for user in
                User.objects(id__in={rev.user_id for rev in book.reviews})
            }

            # Regressor matrix:
            M = np.array(
                [user_ratings[rev.user_id] for rev in book.reviews]
            )

            # Ratings:
            ratings = np.array([rev.rating for rev in book.reviews])

            new_embedding = np.linalg.lstsq(M, ratings, rcond=None)[0]

            max_delta = max(
                max_delta,
                np.max(np.abs(book.embedding - new_embedding))
            )

            book.embedding = new_embedding.tolist()
            book.save()


if __name__ == '__main__':

    connect(db='book_rec', host='mongo', port=27017)

    train_recommender(0.001)
