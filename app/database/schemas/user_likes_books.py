from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserLikesBooks(Base):
    __tablename__ = 'user_likes_books'

    like_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, ForeignKey('users.email', ondelete='CASCADE'))
    book_id = Column(String, ForeignKey('books.book_id', ondelete='CASCADE'))
    liked_at = Column(TIMESTAMP, default=datetime.utcnow)
