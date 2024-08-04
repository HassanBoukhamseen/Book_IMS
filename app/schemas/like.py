from pydantic import BaseModel

class LikeCreate(BaseModel):
    book_id: str

class LikeResponse(BaseModel):
    like_id: int
    book_id: str
    email: str
    liked_at: str
