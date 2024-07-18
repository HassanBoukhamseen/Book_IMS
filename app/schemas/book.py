from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    book_id: Optional[int] = None
    title: str
    author_id: int
    genre: str
    description: str
    year: int
