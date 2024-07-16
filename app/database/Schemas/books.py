from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.Schemas.base import Base


class Book(Base):
    __tablename__ = 'books'
    book_id = Column("book_id", Integer, primary_key=True)
    author_id = Column("author_id", Integer, ForeignKey('authors.author_id'))
    title = Column("title", String(150))
    genre = Column("genre", String(30))
    description = Column("description", Text)
    year = Column("year", Integer)
    author = relationship("Author")
