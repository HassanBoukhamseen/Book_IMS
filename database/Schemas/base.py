from sqlalchemy.ext.declarative import declarative_base
from book_ims.database.connector import connect_to_db

engine, session = connect_to_db()
Base = declarative_base()

