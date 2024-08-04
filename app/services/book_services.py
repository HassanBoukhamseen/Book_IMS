from sqlalchemy import select, delete, asc, update, or_, insert, desc
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.preferences import Preferences
from app.database.schemas.user import User
from app.database.schemas.author import Author
from app.services.author_services import retrieve_single_author
from app.schemas.book import BookUpdateCurrent

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
                return True, "Book retrieved successfully", book
            else:
                return False, "Error occurred", None
    except Exception as e:
        print(e)
        return False, e, None
    finally:
        session.close()    

def retrieve_books_from_db(page: int, per_page: int, search: str = None, sort_by: str = None):
    try:
        engine, session = connect_to_db()
        query = session.query(Book)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.genre.ilike(search_term),
                    Book.author_name.ilike(search_term)
                )
            )
        
        if sort_by:
            if sort_by == 'most_trending':
                query = query.order_by(desc(Book.rating))  
            elif sort_by == 'recommended':
                query = query.order_by(desc(Book.rating))  
            elif sort_by == 'most_recent_publish_year':
                query = query.order_by(desc(Book.year))
            elif sort_by == 'earliest_publish_year':
                query = query.order_by(asc(Book.year))
            elif sort_by == 'top_rated':
                query = query.order_by(desc(Book.rating))
            elif sort_by == 'least_rated':
                query = query.order_by(asc(Book.rating))

        total_books = query.count()
        books = query.offset((page - 1) * per_page).limit(per_page).all()
        
        if not books:
            return False, "No books found", []

        return True, "Books retrieved successfully", books
    except Exception as e:
        return False, str(e), []
    finally:
        session.close()


def delete_book_from_db(book_id):
    try:
        engine, session = connect_to_db()
        with session.begin():
            stmt = delete(Book).where(Book.book_id == book_id)
            result = session.execute(stmt)
            if result.rowcount > 0:
                return True, "Book deleted successfully" 
            else:
                return False, "Book could not be deleted"
    except Exception as e:
        print(e)
        session.rollback()
        return False, e
    finally:
        session.close()

def add_book_to_db(book: Book):
    success, message, author = retrieve_single_author(book.author_id)
    if not success:
        return success, message, None
    
    to_add = Book(
        title=book.title, 
        genre=book.genre, 
        description=book.description, 
        year=book.year, 
        author_id=book.author_id
    )
    
    engine, session = connect_to_db()
    try:
        session.add(to_add)
        session.commit()
        book_id = to_add.book_id
        return True, "Book added Successfully", book_id
    except Exception as e:
        session.rollback()
        return False, e, None
    finally:
        session.close()
        
def edit_book_info(book_id: int, new_book: BookUpdateCurrent):
    success, message, book = retrieve_single_book(book_id)
    if not success:
        return success, message

    if new_book.author_id is not None:
        engine, session = connect_to_db()
        stmt = select(Author.author_id).where(Author.author_id == new_book.author_id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            output = results.fetchone()
            if not output:
                return False, "New author does not exist"
    
    updated_book_data = {
        "title": new_book.title if new_book.title is not None else book['title'],
        "author_id": new_book.author_id if new_book.author_id is not None else book['author_id'],
        "genre": new_book.genre if new_book.genre is not None else book['genre'],
        "description": new_book.description if new_book.description is not None else book['description'],
        "year": new_book.year if new_book.year is not None else book['year'],
    }

    stmt = (
        update(Book)
        .where(Book.book_id == book_id)
        .values(
            title=updated_book_data["title"],
            author_id=updated_book_data["author_id"],
            genre=updated_book_data["genre"],
            description=updated_book_data["description"],
            year=updated_book_data["year"]
        )
        .execution_options(synchronize_session="fetch")
    )

    try:
        engine, session = connect_to_db()
        with session.begin():
            session.execute(stmt)
            session.commit()
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

    return True, "Book information successfully updated"
