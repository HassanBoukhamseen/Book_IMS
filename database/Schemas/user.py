from sqlalchemy import Column, String, Integer
from book_ims.database.Schemas.base import Base

class User(Base):
    __tablename__ = 'users'
    email = Column('email', String(100), primary_key=True)
    fname = Column('fname', String(50))
    lname = Column('lname', String(50))
    hashed_pw = Column('hashed_pw', String(100))
    role = Column('role', Integer)