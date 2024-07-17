from fastapi import Depends, FastAPI, HTTPException, Request
from app.services.author_retrievals import retrieve_single_author, retrieve_authors_from_db
from app.services.book_services import retrieve_single_book, retrieve_books_from_db, add_book_to_db, delete_book as delete_book_from_db
from app.schemas.login_info import Login
from app.services.user_retrievals import retrieve_single_user
from app.services.authenticate_user import authenticate_user
from app.services.token import create_access_token, verify_token
from app.services.book_recommendations import get_book_recommendations
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.session import SessionData
from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend
from app.schemas.user import User
from app.schemas.book import Book
from app.services.user_registration import register_user
from datetime import timedelta
from app.utils.get_current_user import get_current_user
from app.middleware.request_logger import setup_middleware

app = FastAPI()
backend = InMemoryBackend[UUID, SessionData]()
setup_middleware(app)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/books")
def get_books():
    return retrieve_books_from_db()

@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = retrieve_single_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

#@ADMIN ONLY
@app.post("/books")
def add_book(book: Book, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    print(book) #testing
    book_id = add_book_to_db(book)
    if book_id is None:
        raise HTTPException(status_code=400, detail="Failed to add book")
    return {"message": "Book added successfully", "book_id": book_id}

#@ADMIN ONLY
@app.put("/books/{book_id}")
def update_book():
    return {"update": "existing book"}

#@ADMIN ONLY
@app.delete("/books/{book_id}")
def delete_book_route(book_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    deleted_book = delete_book_from_db(book_id)
    if not deleted_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

# HERE YOU WORK
@app.get("/authors")
def get_authors():
    return retrieve_authors_from_db()

@app.get("/authors/{author_id}")
def get_author(author_id: int):
    return retrieve_single_author(author_id)

#@ADMIN ONLY
@app.post("/authors")
def add_author():
    return {"add ": "new author"}

#@ADMIN ONLY
@app.put("/authors/{author_id}")
def update_author():
    return {"add ": "new author"}

#@ADMIN ONLY
@app.delete("/authors/{author_id}")
def delete_author():
    return {"delete": "author"}

@app.post("/users/register")
def add_user(user: User):
    print(f"Received user data: {user}")
    success, message = register_user(user)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Retrieve the user details after successful registration
    registered_user = retrieve_single_user(user.email)
    if not registered_user:
        raise HTTPException(status_code=404, detail="User not found after registration")
    return registered_user

#Still need JWT stuff
@app.post("/users/login")
async def auth_user(login_data: Login):
    session = uuid4()
    auth = authenticate_user(login_data.username, login_data.password)
    if auth:
        user_info = retrieve_single_user(login_data.username)
    data = SessionData(
        fname=user_info["fname"],
        lname=user_info["lname"],
        email=user_info["email"],
        role=user_info["role"]
    )
    await backend.create(session, data)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_info}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": user_info
    }

@app.get("/users/me")
def get_user():
    return {"retrieve": "authed user"}

@app.put("/users/me")
def update_user():
    return {"update": "authed user"}

@app.get("/recommendations")
def get_recommendations(email: str):
    book_recommendations = get_book_recommendations(email)
    if not book_recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")
    return book_recommendations

@app.get("/healthcheck")
def health_check():
    return True
