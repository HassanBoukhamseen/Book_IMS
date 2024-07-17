from fastapi import FastAPI, Body, Depends, HTTPException
import uvicorn
from app.schemas.book import Book
from app.schemas.user import User
from app.schemas.login_info import Login
from app.services.jwt_handler import get_current_user, signJWT, create_access_token
from app.services.jwt_bearer import jwtBearer
from app.services.book_retrievals import retrieve_books_from_db, retrieve_single_book, update_book_in_db, delete_book_from_db
from app.services.author_retrievals import retrieve_authors_from_db, retrieve_single_author
from app.services.user_retrievals import retrieve_single_user
from app.services.user_registration import register_user
from app.services.authenticate_user import authenticate_user
from app.services.book_recommendations import get_book_recommendations
from datetime import timedelta
from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend
from app.schemas.session import SessionData

app = FastAPI()
backend = InMemoryBackend[UUID, SessionData]()

@app.get("/", tags=["Smart Library"])
async def read_root():
    return {"Hello": "World"}

@app.get("/books", tags=["Books"])
def get_books():
    return retrieve_books_from_db()

@app.get("/books/{id}", tags=["Book by ID"])
def get_book(id: int):
    book = retrieve_single_book(id)
    if book:
        return book
    raise HTTPException(status_code=404, detail="Book with this ID does not exist!")

@app.post("/books", dependencies=[Depends(jwtBearer(required_role="admin"))], tags=["Add New Book"])
def add_book(book: Book):
    # Implement the logic to add a book to the database
    return {"info": "Book Added!"}

@app.put("/books/{book_id}", dependencies=[Depends(jwtBearer(required_role="admin"))], tags=["Update Book"])
def update_book(book_id: int, new_data: dict):
    updated_book = update_book_in_db(book_id, new_data)
    if updated_book:
        return updated_book
    else:
        raise HTTPException(status_code=404, detail="Book not found or update failed")

@app.delete("/books/{book_id}", dependencies=[Depends(jwtBearer(required_role="admin"))], tags=["Delete Book"])
def delete_book(book_id: int):
    deleted_book = delete_book_from_db(book_id)
    if deleted_book:
        return deleted_book
    else:
        raise HTTPException(status_code=404, detail="Book not found or delete failed")

@app.get("/authors", tags=["Authors"])
def get_authors():
    return retrieve_authors_from_db()

@app.get("/authors/{author_id}", tags=["Author by ID"])
def get_author(author_id: int):
    return retrieve_single_author(author_id)

@app.post("/authors", dependencies=[Depends(jwtBearer(required_role="admin"))], tags=["Add New Author"])
def add_author():
    # Implement the logic to add an author to the database
    return {"info": "Author Added!"}

@app.put("/authors/{author_id}", dependencies=[Depends(jwtBearer(required_role="admin"))], tags=["Update Author"])
def update_author():
    # Implement the logic to update an author in the database
    return {"info": "Author Updated!"}

@app.delete("/authors/{author_id}", dependencies=[Depends(jwtBearer(required_role="admin"))], tags=["Delete Author"])
def delete_author():
    # Implement the logic to delete an author from the database
    return {"info": "Author Deleted!"}

@app.post("/users/register", tags=["Users"])
def add_user(user: User = Body(default=None)):
    success, message = register_user(user)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return signJWT(user.email, user.role)

@app.post("/users/login", tags=["Users"])
async def auth_user(login_data: Login):
    auth, message = authenticate_user(login_data.username, login_data.password)
    if auth:
        user_info = retrieve_single_user(login_data.username)
        access_token_expires = timedelta(minutes=15)
        access_token = create_access_token(
            data={"sub": user_info["email"], "role": user_info["role"]}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": user_info
        }
    else:
        raise HTTPException(status_code=401, detail=message)

@app.get("/users/me", dependencies=[Depends(jwtBearer())], tags=["Users"])
def get_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", dependencies=[Depends(jwtBearer())], tags=["Users"])
def update_user(new_data: dict, current_user: User = Depends(get_current_user)):
    # Implement the logic to update user info in the database
    return {"info": "User Updated!"}

@app.get("/recommendations", dependencies=[Depends(jwtBearer())], tags=["Recommendations"])
def get_recommendations(email: str):
    book_recommendations = get_book_recommendations(email)
    if not book_recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")
    return book_recommendations

@app.get("/healthcheck", tags=["Health Check"])
def health_check():
    return True

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
