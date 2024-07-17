
from sqlalchemy import select
from app.database.connector import connect_to_db
from app.database.Schemas.books import Book

def retrieve_single_book(id):
    try:
        engine, session = connect_to_db()
        stmt = select(Book.book_id, Book.title, Book.genre, Book.description, Book.year, Book.author_id).where(Book.book_id == id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            output = results.fetchone()
            book = {"book_id": output[0], "title": output[1], "genre": output[2], "description": output[3], "year": output[4], "author": output[5]}
        return book
    except Exception as e:
        print(e)
    finally:
        session.close()    

def retrieve_books_from_db():
    try:
        engine, session = connect_to_db()
        stmt = select(Book.book_id, Book.title, Book.genre, Book.description, Book.year, Book.author_id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            books = map(lambda result: {"book_id": result[0], "title": result[1], "genre": result[2], "description": result[3], "year": result[4], "author": result[5]}, results.fetchall()) 
        return list(books)
    except Exception as e:
        print(e)
    finally:
        session.close()

if __name__ == "__main__":
    print(retrieve_books_from_db())
    print(retrieve_single_book(2))




