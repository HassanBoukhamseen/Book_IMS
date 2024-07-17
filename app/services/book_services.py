from sqlalchemy import select, delete, insert
from app.database.connector import connect_to_db
from app.database.Schemas.books import Book

# get a book
def retrieve_single_book(id):
    try:
        engine, session = connect_to_db()
        stmt = select(Book.book_id, Book.title, Book.genre, Book.description, Book.year, Book.author_id).where(Book.book_id == id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            output = results.fetchone()
            if output:
                book = {"book_id": output[0], "title": output[1], "genre": output[2], "description": output[3], "year": output[4], "author_id": output[5]}
                return book
            else:
                return None
    except Exception as e:
        print(e)
        return None
    finally:
        session.close()    

# get all books
def retrieve_books_from_db():
    try:
        engine, session = connect_to_db()
        stmt = select(Book.book_id, Book.title, Book.genre, Book.description, Book.year, Book.author_id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            books = [{"book_id": result[0], "title": result[1], "genre": result[2], "description": result[3], "year": result[4], "author_id": result[5]} for result in results.fetchall()]
        return books
    except Exception as e:
        print(e)
        return []
    finally:
        session.close()

# delete a book 
def delete_book(book_id):
    try:
        engine, session = connect_to_db()
        with session.begin():
            stmt = delete(Book).where(Book.book_id == book_id)
            result = session.execute(stmt)
            return result.rowcount > 0  # Returns True if a row was deleted, otherwise False
    except Exception as e:
        print(e)
        session.rollback()
        return False
    finally:
        session.close()

# add a book
def add_book_to_db(book: Book):
    print(book)  #testing
    try:
        engine, session = connect_to_db()
        with session.begin():
            stmt = insert(Book).values(title=book.title, genre=book.genre, description=book.description, year=book.year, author_id=book.author_id)
            result = session.execute(stmt)
            session.commit()
            return result.inserted_primary_key[0]  # Returns the id of the new book
    except Exception as e:
        print(e)
        session.rollback()
        return None
    finally:
        session.close()

# if __name__ == "__main__":
#     print("hi")
#     # Uncomment below lines for testing
#     # print(retrieve_books_from_db())
#     print(retrieve_single_book(29))
#     print(delete_book(29))