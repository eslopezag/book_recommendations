# Book Recommendations

This is a self-educational project to practice some abilities and technologies such as MongoDB, Docker, Docker Compose, and FastAPI. The objective is to create an application to recommend books to users with a backend and a database residing in different Docker containers. The backend consists in an API built with [FastAPI](https://fastapi.tiangolo.com/) whose endpoints are described next.

## API Endpoints

- `/users/signup` (POST): allows registering new users into the database.

- `/users/admin-signup` (POST): allows registering new users with administrative privileges into the database.

- `/users/login` (POST): provides authentication via OAuth 2.0 bearer tokens.

- `/users/me` (GET): fetches information about the current user.

- `/users/list-users` (GET): fetches information about all users in the database. Only an admin user can get a successful response from this endpoint.

- `/books/register-review` (POST): allows users to register the rating they give to a book. The user must provide the book's ISBN 10 and the backend uses the [Open Library API](https://openlibrary.org/dev/docs/api/books) to retrieve more information about the specific work if it doesn't already exist in the database.

- `/books/list-books` (GET): fetches information about all books in the database. Only an admin user can get a successful response from this endpoint.

## Database Schema

The application's database corresponds to an instance of mongoDB running in a different container from the API. The collections in this database conform to the following document types:

- Users collection fields:
    * username (str): username identifying the user
    * hashed_password (str): bcrypt-hashed user's password
    * reviews (EmbeddedDocumentList): list of embedded documents describing book ratings with the following fields:
        + ol_work_id (str): book's Open Library work ID
        + rating (int): book rating between 0 and 10
    * permissions (str): string identifying the user as an admin ("admin") or standard ("standard") user

- Books collection fields"
    * ol_work_id (str): book's Open Library work ID
    * isbn_10_list (list[str]): list of ISBN 10 identifiers associated with the book
    * title (str): book's title
    * reviews (EmbeddedDocumentList): list of embedded documents describing ratings given by users to the book with the following fields:
        + user_id (ObjectId): mongo ID of the user who gave the rating
        + rating (int): book rating between 0 and 10
