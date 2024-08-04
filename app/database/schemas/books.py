from sqlalchemy import Column, String, Integer, Text, ForeignKey, Double
from sqlalchemy.orm import relationship
from app.database.schemas.base import Base

class Book(Base):
    __tablename__ = 'books'
    book_id = Column("book_id", String, primary_key=True, autoincrement=True)
    author_id = Column("author_id", Integer)
    title = Column("title", String(512))
    genre = Column("genre", String(512))
    description = Column("description", Text)
    year = Column("year", Integer)
    thumbnail = Column("thumbnail", String(512))
    author_name = Column("author_name", String)
    rating = Column("rating", Double)
    rating_count = Column("ratings_count", Integer)


