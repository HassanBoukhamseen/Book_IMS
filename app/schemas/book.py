from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    book_id: Optional[str] = None
    title: str
    author_id: int
    genre: str
    description: str
    year: int

class BookUpdateCurrent(BaseModel):
    title: Optional[str] = None
    author_id: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None