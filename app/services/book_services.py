from sqlalchemy import select, delete, insert
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.preferences import Preferences
from app.database.schemas.user import User
from app.database.schemas.author import Author

def get_book_recommendations(email: str):
    try:
        engine, session = connect_to_db()
        stmt = select(Preferences.preference).where(Preferences.email == email)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            genres = list(map(lambda x: x[0], results.fetchall()))
            if len(genres) == 0:
                return False, "User has no preferences", None
            stmt = select(Book.title).where(Book.genre.in_(genres)).limit(5)
            results = conn.execute(stmt)
            recommendations = list(map(lambda x: x[0], results.fetchall()))
            if len(recommendations) == 0:
                return False, "No recommendations found", None
            return True, "Recommendations successfully retrieved", recommendations
    except Exception as e:
        return False, e, None
    finally:
        session.close()


def retrieve_single_book(id):
    try:
        engine, session = connect_to_db()
        stmt = select(Book.book_id, Book.title, Book.genre, Book.description, Book.year, Book.author_id).where(Book.book_id == id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            output = results.fetchone()
            if output:
                book = {
                    "book_id": output[0], 
                    "title": output[1], 
                    "genre": output[2], 
                    "description": output[3], 
                    "year": output[4], 
                    "author_id": output[5]
                }
                return True, "Book retreived successfully", book
            else:
                return False, "Error ocurred", None
    except Exception as e:
        print(e)
        return False, e, None
    finally:
        session.close()    

def retrieve_books_from_db():
    try:
        engine, session = connect_to_db()
        stmt = select(Book.book_id, Book.title, Book.genre, Book.description, Book.year, Book.author_id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            books = [{"book_id": result[0], "title": result[1], "genre": result[2], "description": result[3], "year": result[4], "author_id": result[5]} for result in results.fetchall()]
        return True, "Books retreived successfully", books
    except Exception as e:
        print(e)
        return False, e, None
    finally:
        session.close()

def delete_book_from_db(book_id):
    try:
        engine, session = connect_to_db()
        with session.begin():
            stmt = delete(Book).where(Book.book_id == book_id)
            result = session.execute(stmt)
            return result.rowcount > 0, "Row deleted successfully"  # Returns True if a row was deleted, otherwise False
    except Exception as e:
        print(e)
        session.rollback()
        return False, e
    finally:
        session.close()

def add_book_to_db(book: Book):
    print(book)  #testing
    try:
        engine, session = connect_to_db()
        stmt = (
                    insert(Book)
                    .values(
                        title=book.title, 
                        genre=book.genre, 
                        description=book.description, 
                        year=book.year, author_id=book.author_id
                    )
                )
        with engine.connect() as conn:
            conn.execute(stmt)
            session.commit()
    except Exception as e:
        session.rollback()
        return False, e
    finally:
        session.close()
        return True, "Book added Successfully"
