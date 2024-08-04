from sqlalchemy import select, delete, insert
from app.database.connector import connect_to_db
from app.database.schemas.user_likes_books import UserLikesBooks
from app.database.schemas.books import Book

def add_like_to_book(email: str, book_id: str):
    try:
        engine, session = connect_to_db()
        stmt = insert(UserLikesBooks).values(email=email, book_id=book_id)
        with session.begin():
            session.execute(stmt)
            session.commit()
        return True, "Like added successfully"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def remove_like_from_book(email: str, book_id: str):
    try:
        engine, session = connect_to_db()
        with session.begin():
            stmt = delete(UserLikesBooks).where(UserLikesBooks.email == email, UserLikesBooks.book_id == book_id)
            result = session.execute(stmt)
            session.commit()
            if result.rowcount > 0:
                return True, "Like removed successfully"
            else:
                return False, "Like not found"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def get_user_liked_books(email: str):
    try:
        engine, session = connect_to_db()
        stmt = select(UserLikesBooks.book_id).where(UserLikesBooks.email == email)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            liked_books = [result[0] for result in results.fetchall()]

        if not liked_books:
            return False, "No liked books found", None

        stmt = select(Book.book_id, Book.title, Book.author_name, Book.genre, Book.description, Book.year, Book.thumbnail, Book.rating).where(Book.book_id.in_(liked_books))
        with engine.connect() as conn:
            results = conn.execute(stmt)
            books = [{"book_id": result[0], "title": result[1], "author_name": result[2], "genre": result[3], "description": result[4], "year": result[5], "thumbnail": result[6], "rating": result[7]} for result in results.fetchall()]
        
        return True, "Liked books retrieved successfully", books
    except Exception as e:
        return False, str(e), None
    finally:
        session.close()
