from pydantic import BaseModel

class Book(BaseModel):
    book_id: int
    title: str
    author_id: int
    genre: str
    description: str
    year: int
