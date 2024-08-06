from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    book_id: Optional[str] = None
    title: str
    author_name: str  
    genre: str
    description: str
    year: int

class BookUpdateCurrent(BaseModel):
    title: Optional[str] = None
    author_name: Optional[str] = None  
    genre: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None