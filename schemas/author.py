from pydantic import BaseModel

class Author(BaseModel):
    author_id: int
    name: str
    biography: str
