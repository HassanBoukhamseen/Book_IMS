from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import timedelta

from sse_starlette.sse import EventSourceResponse
import uvicorn
import asyncio

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
    register_user,
    retrieve_all_users,
    delete_user
)
from app.services.book_services import (
    get_book_recommendations,
    retrieve_single_book, 
    retrieve_books_from_db, 
    add_book_to_db, 
    delete_book_from_db,
    edit_book_info
)
from app.services.like_services import (
    add_like_to_book,
    remove_like_from_book,
    get_user_liked_books
)
from app.services.token_services import create_access_token
from app.schemas.login_info import Login
from app.schemas.author import Author, AuthorUpdateCurrent
from app.schemas.book import BookUpdateCurrent, Book
from app.schemas.user import User, UserUpdateCurrent
from app.schemas.like import LikeCreate, LikeResponse
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils.get_current_user import get_current_user
from app.utils.chatbot import get_response, get_combined_query
from app.utils.recommendations import get_recommended_books

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=403, detail="Invalid Authorization")
    return {"Hello": "World"}

@app.get("/books")
def get_books(
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    per_page: int = 18,
    search: str = Query(None),
    sort_by: str = Query(None)
):
    success, message, books = retrieve_books_from_db(page, per_page, search, sort_by)
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return {"message": message, "books": books, "page": page, "per_page": per_page}


@app.get("/books/{book_id}")
def get_book(book_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    success, message, book = retrieve_single_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message, "book": book}

@app.post("/books")
def add_book(book: Book, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message, book_id = add_book_to_db(book)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book_id": book_id}


@app.put("/books/{book_id}")
def update_book(book_id: int, new_book: BookUpdateCurrent, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message = edit_book_info(book_id, new_book)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book_id": book_id}

@app.delete("/books/{book_id}")
def delete_book_route(book_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message = delete_book_from_db(book_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book": book_id}


@app.get("/authors")
def get_authors(current_user: Annotated[dict, Depends(get_current_user)]):
    return retrieve_authors_from_db()

@app.get("/authors/{author_id}")
def get_author(author_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    success, message, author = retrieve_single_author(author_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author": author}

@app.post("/authors")
def add_author(author: Author, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message, author_id = add_author_to_database(author)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author_id": author_id}

@app.put("/authors/{author_id}")
def update_author(author_id: int, new_author: AuthorUpdateCurrent, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message = edit_author_info(author_id, new_author)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author_id": author_id}

@app.delete("/authors/{author_id}")
def delete_author(author_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Not Authorized")
    success, message = delete_author_from_db(author_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author_id": author_id}

@app.post("/users/register")
def add_user(user: User):
    try:
        success, message = register_user(user)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        return {"message": message, "user": user.email}
    except DataError as e:
        raise HTTPException(status_code=400, detail="Invalid data provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/users/login")
async def auth_user(login_data: Login):
    try:
        auth, message = authenticate_user(login_data.username, login_data.password)
        if not auth:
            raise HTTPException(status_code=401, detail=message)
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
    except DataError as e:
        raise HTTPException(status_code=400, detail="Invalid data provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/me")
def get_user(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"user": current_user}

@app.put("/users/me")
async def update_user(user_update: UserUpdateCurrent, current_user: Annotated[dict, Depends(get_current_user)]):
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

@app.get("/users")
def get_all_users(current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:  
        raise HTTPException(status_code=403, detail="Not authorized to view all users")

    success, message, users = retrieve_all_users()
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return {"message": message, "users": users}

@app.delete("/users/{email}")
def delete_user_route(email: str, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != 1:  
        raise HTTPException(status_code=403, detail="Not authorized to delete users")
    success, message = delete_user(email)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return {"message": message}

@app.get("/recommendations")
def get_recommendations(current_user: Annotated[dict, Depends(get_current_user)]):
    email = current_user["email"]
    success, message, book_recommendations = get_book_recommendations(email)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book_recommendations": book_recommendations}

@app.post("/like")
def like_book(like: LikeCreate, current_user: Annotated[dict, Depends(get_current_user)]):
    print(f"debuggin..Received payload: {like}")  
    if not like.book_id:
        raise HTTPException(status_code=400, detail="Book ID is required")
    success, message = add_like_to_book(current_user["email"], like.book_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": "Book liked successfully", "book_id": like.book_id}




@app.delete("/unlike/{book_id}")
def unlike_book(book_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    success, message = remove_like_from_book(current_user["email"], book_id)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": "Book unliked successfully"}

@app.get("/likes")
def get_liked_books(current_user: Annotated[dict, Depends(get_current_user)]):
    success, message, liked_books = get_user_liked_books(current_user["email"])
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": "Liked books retrieved successfully", "books": liked_books}

@app.get("/healthcheck")
def health_check():
    return {"status": "healthy"}


# Chatbot and Recommendations Endpoints TODO: grab actual session
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
