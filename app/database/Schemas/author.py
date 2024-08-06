from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from app.database.schemas.base import Base

class Author(Base):
    __tablename__ = 'authors'
    author_id = Column('author_id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    biography = Column('biography', Text)

    books = relationship("Book", back_populates="author")