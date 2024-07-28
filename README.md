# Book_IMS
Book Inventroy Management System

# Setup and Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn
- Streamlit
- Pinecone (for vector database)
- Sentence Transformers

# Run the servers (FastAPI & Streamlit)

Install Poetry
Follow the instructions to install Poetry from the official documentation.

Install Dependencies:
poetry install

Run the FastAPI Server:
fastapi dev api.py

Run the Streamlit Application
streamlit run streamlit_client.py


# APIs:

## User Management
Register User

POST /users/register
Registers a new user.
Login User

POST /users/login
Authenticates a user and returns an access token.
Get Current User

GET /users/me
Retrieves the current authenticated user's information.
Update User

PUT /users/me
Updates the current authenticated user's information.

## Book Management
Get All Books

GET /books
Retrieves a list of all books.
Get Single Book

GET /books/{book_id}
Retrieves details of a single book by ID.
Add Book

POST /books
Adds a new book to the database (Admin only).
Update Book

PUT /books/{book_id}
Updates an existing book's information (Admin only).
Delete Book

DELETE /books/{book_id}
Deletes a book from the database (Admin only).

## Author Management
Get All Authors

GET /authors
Retrieves a list of all authors.
Get Single Author

GET /authors/{author_id}
Retrieves details of a single author by ID.
Add Author

POST /authors
Adds a new author to the database (Admin only).
Update Author

PUT /authors/{author_id}
Updates an existing author's information (Admin only).
Delete Author

DELETE /authors/{author_id}
Deletes an author from the database (Admin only).
Book Recommendations
Get Book Recommendations
GET /recommendations
Retrieves book recommendations for the current user.

## Chatbot and Book Retrieval
Chat Endpoint

POST /chat
Handles user input for the chatbot and streams the response.
Books Retrieval

POST /booksretrievals
Retrieves books based on user input.
