from app.services.author_services import (
    retrieve_single_author, 
    retrieve_authors_from_db, 
    add_author_to_database,
    edit_author_info,
    delete_author_from_db
)
from app.services.user_services import (
    retrieve_single_user, 
    authenticate_user, 
    edit_user_info, 
    register_user
)
from app.services.book_services import (
    get_book_recommendations,
    retrieve_single_book, 
    retrieve_books_from_db, 
    add_book_to_db, 
    delete_book_from_db,
    edit_book_info
)
from app.services.token_services import create_access_token

from app.schemas.login_info import Login
from app.schemas.author import Author, AuthorUpdateCurrent
from app.schemas.book import BookUpdateCurrent
from app.schemas.user import User, UserUpdateCurrent
from app.schemas.book import Book

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils.get_current_user import get_current_user

from fastapi import Depends, FastAPI, HTTPException, Request
from typing import Annotated
from datetime import timedelta
import uvicorn
from sse_starlette.sse import EventSourceResponse

#min
from fastapi.responses import StreamingResponse


app = FastAPI()

@app.get("/")
def read_root(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    return {"Hello": "World"}

@app.get("/books")
def get_books(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    success, message, books = retrieve_books_from_db()
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return {"message": message, "books": books}

@app.get("/books/{book_id}")
def get_book(book_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    success, message, book = retrieve_single_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message, "book": book}

#@ADMIN ONLY
@app.post("/books")
def add_book(book: Book, current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user or current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message, book_id = add_book_to_db(book)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book_id": book_id}

#@ADMIN ONLY
@app.put("/books/{book_id}")
def update_book(book_id:int, new_book:BookUpdateCurrent, current_user: dict = Depends(get_current_user)):
    if not current_user or current_user["role"] != 1:
        return HTTPException(status_code=403, detail="Not autherized")
    success, message = edit_book_info(book_id, new_book)
    if not success:
        return HTTPException(status_code=400, detail=message)               
    return {"message": message, "book_id": book_id}


#@ADMIN ONLY
@app.delete("/books/{book_id}")
def delete_book_route(book_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message = delete_book_from_db(book_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book": book_id}

# HERE YOU WORK
@app.get("/authors")
def get_authors(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    return retrieve_authors_from_db()

@app.get("/authors/{author_id}")
def get_author(author_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    success, message, author = retrieve_single_author(author_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author": author}

#@ADMIN ONLY
@app.post("/authors")
def add_author(author: Author, current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user or current_user["role"] != 1:
        return HTTPException(status_code=403, detail="Not autherized")
    success, message, author_id = add_author_to_database(author)
    if not success:
        return HTTPException(status_code=400, detail=message)           
    return {"message": message, "author_id": author_id}

#@ADMIN ONLY
@app.put("/authors/{author_id}")
def update_author(author_id:int, new_author:AuthorUpdateCurrent, current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user or current_user["role"] != 1:
        return HTTPException(status_code=403, detail="Not autherized")
    success, message = edit_author_info(author_id, new_author)
    if not success:
        return HTTPException(status_code=400, detail=message)               
    return {"message": message, "author_id": author_id}

#@ADMIN ONLY
@app.delete("/authors/{author_id}")
def delete_author(author_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user or current_user["role"] != 1:
        return HTTPException(status_code=403, detail="Not autherized")
    success, message = delete_author_from_db(author_id)
    if not success:
        return HTTPException(status_code=400, detail=message)               
    return {"message": message, "author_id": author_id}

@app.post("/users/register")
def add_user(user: User):
    success, message = register_user(user)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "user": user.email}

@app.post("/users/login")
async def auth_user(login_data: Login):
    auth, message = authenticate_user(login_data.username, login_data.password)
    if not auth:
        return HTTPException(status_code=401, detail=message)
    success, message, user_info = retrieve_single_user(login_data.username)
    if not success:
        raise HTTPException(status_code=400, detail=message)

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
def get_user(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    return {"user": current_user}

@app.put("/users/me")
async def update_user(user_update: UserUpdateCurrent, current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    email = current_user["email"]
    success, message = edit_user_info(email, user_update)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    success, message, user = retrieve_single_user(email)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
    return {"message": message, "token": access_token}

@app.get("/recommendations")
def get_recommendations(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        return HTTPException(status_code=403, detail="Invalid Authorization")
    email = current_user["email"]
    success, message, book_recommendations = get_book_recommendations(email)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book_recommendations": book_recommendations}

@app.get("/healthcheck")
def health_check():
    return True




from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.utils.chatbot import get_response, get_combined_query
from app.utils.recommendations import get_recommended_books
import asyncio

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "1"

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    user_input = chat_request.message
    session_id = chat_request.session_id
    combined = get_combined_query(user_input)
    async def response_streamer():
        tokens = get_response(combined, session_id)
        for token in tokens:
            yield token
            await asyncio.sleep(0.01)

    return StreamingResponse(response_streamer(), media_type="text/plain")

@app.post("/booksretrievals")
def booksretrievals(chat_request: ChatRequest):
    user_input = chat_request.message
    books = get_recommended_books(user_input)
    return books




