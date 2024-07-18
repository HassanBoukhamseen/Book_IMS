from sqlalchemy import Column, String, Integer, Text
from app.database.schemas.base import Base

class Author(Base):
    __tablename__ = 'authors'
    author_id = Column('author_id', Integer, primary_key=True)
    name = Column('name', String(100))
    biography = Column('biography', Text)