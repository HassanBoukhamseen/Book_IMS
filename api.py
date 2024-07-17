from app.services.author_retrievals import retrieve_single_author, retrieve_authors_from_db
from app.services.book_retrievals import retrieve_single_book, retrieve_books_from_db
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
from app.services.user_registration import register_user
from fastapi import Depends, FastAPI, HTTPException, Request, logger
from datetime import timedelta

app = FastAPI()
backend = InMemoryBackend[UUID, SessionData]()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/books")
def get_books():
    return retrieve_books_from_db()

@app.get("/books/{book_id}")
def get_book(book_id: int):
    return retrieve_single_book(book_id)

#@ADMIN ONLY
@app.post("/books")
def add_book():
    return {"add": "new book"}

#@ADMIN ONLY
@app.put("/books/{book_id}")
def update_book():
    return {"update": "existing book"}

#@ADMIN ONLY
@app.delete("/books/{book_id}")
def delete_book():
    return {"delete": "book"}

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

    return {"add ": "new auhtor"}

#@ADMIN ONLY
@app.put("/authors/{author_id}")
def update_author():
    return {"add ": "new auhtor"}

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
        data={"sub": user_info["email"]}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": user_info
    }

@app.get("/users/me")
def get_user():
    return {"retreive": "authed user"}

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



