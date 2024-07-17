from sqlalchemy import select, update, delete
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

def update_book_in_db(book_id: int, new_data: dict):
    try:
        engine, session = connect_to_db()
        stmt = (
            update(Book)
            .where(Book.book_id == book_id)
            .values(**new_data)
            .returning(Book.book_id, Book.title, Book.genre, Book.description, Book.year, Book.author_id)
        )
        with engine.connect() as conn:
            result = conn.execute(stmt)
            updated_book = result.fetchone()
        session.commit()
        if updated_book:
            book = {
                "book_id": updated_book[0],
                "title": updated_book[1],
                "genre": updated_book[2],
                "description": updated_book[3],
                "year": updated_book[4],
                "author_id": updated_book[5]
            }
            return book
        else:
            return None
    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.close()

def delete_book_from_db(book_id: int):
    try:
        engine, session = connect_to_db()
        stmt = delete(Book).where(Book.book_id == book_id).returning(Book.book_id)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            deleted_book_id = result.fetchone()
        session.commit()
        if deleted_book_id:
            return {"book_id": deleted_book_id[0]}
        else:
            return None
    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.close()






