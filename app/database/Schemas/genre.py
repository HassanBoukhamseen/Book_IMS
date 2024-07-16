from sqlalchemy import Column, Integer, String
from app.database.Schemas.base import Base
# Under test
class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)