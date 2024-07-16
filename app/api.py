from app.services.author_retrievals import retrieve_single_author, retrieve_authors_from_db
from app.schemas.login_info import Login
from app.services.user_retrievals import retrieve_single_user
from app.services.authenticate_user import authenticate_user
from app.schemas.session import SessionData
from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi import FastAPI, Request

app = FastAPI()
backend = InMemoryBackend[UUID, SessionData]()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/books")
def get_books():
    return {"ALl": "Books"}

@app.get("/books/{book_id}")
def get_book():
    return {"Specific": "Book by ID"}

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
def add_user():
    return {"add": "user"}

#Still need 
@app.post("/users/login")
async def auth_user(login_data: Login):
    session = uuid4()
    auth = authenticate_user(login_data.username, login_data.password)
    if auth:
        user_info = retrieve_single_user(login_data.username)
    print(user_info)
    data = SessionData(
        fname=user_info["fname"],
        lname=user_info["lname"],
        email=user_info["åemail"],
        role=user_info["role"]
    )
    await backend.create(session, data)
    return user_info

@app.get("/users/me")
def get_user():
    return {"retreive": "authed user"}

@app.put("/users/me")
def update_user():
    return {"update": "authed user"}

@app.get("/recommendations")
def get_recommendations():
    return {"retreive": "recommendations for authed user prefs"}

@app.get("/healthcheck")
def health_check():
    return True



