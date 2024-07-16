from sqlalchemy import select
from app.database.connector import connect_to_db
from app.database.Schemas.books import Book
from app.database.Schemas.preferences import Preferences
# Under test
# may need schema includes a table to track books the user has read.?
# app/database/Schemas/user_books.py
# from sqlalchemy import Column, String, Integer, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database.Schemas.base import Base

# class UserBooks(Base):
#     __tablename__ = 'user_books'
#     id = Column(Integer, primary_key=True, index=True)
#     user_email = Column(String, ForeignKey('users.email'))
#     book_id = Column(Integer, ForeignKey('books.book_id'))
#     book = relationship("Book")
#     user = relationship("User")


# app/services/book_recommendations.py
from sqlalchemy import select, func
from app.database.connector import connect_to_db
from app.database.Schemas.books import Book
from app.database.Schemas.preferences import Preferences
# from app.database.Schemas.user_books import UserBooks
import logging

'''
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_book_recommendations(email: str):
    try:
        engine, session = connect_to_db()
        logger.info(f"Connecting to the database to retrieve book recommendations for: {email}")

        # Get the genres of the books the user has read
        read_books_stmt = select(Book.genre).join(UserBooks, UserBooks.book_id == Book.book_id).where(UserBooks.user_email == email)
        read_genres = session.execute(read_books_stmt).scalars().all()

        if not read_genres:
            logger.info("User has not read any books")
            return []

        # Get the top 3 most read genres
        top_genres = session.query(Book.genre, func.count(Book.genre).label('count')).join(UserBooks, UserBooks.book_id == Book.book_id).where(UserBooks.user_email == email).group_by(Book.genre).order_by(func.count(Book.genre).desc()).limit(3).all()
        top_genres = [genre for genre, count in top_genres]

        # Query to get books that match the user's top genres and have not been read by the user
        books_stmt = select(Book).where(Book.genre.in_(top_genres), Book.book_id.notin_(select(UserBooks.book_id).where(UserBooks.user_email == email)))
        books = session.execute(books_stmt).scalars().all()

        if books:
            book_list = [
                {
                    "book_id": book.book_id,
                    "title": book.title,
                    "genre": book.genre,
                    "description": book.description,
                    "year": book.year,
                    "author_id": book.author_id
                } for book in books
            ]
            logger.info(f"Books found: {book_list}")
            return book_list
        else:
            logger.info("No books found")
            return []
    except Exception as e:
        logger.error(f"Error retrieving books: {e}")
        return []
    finally:
        session.close()
'''
