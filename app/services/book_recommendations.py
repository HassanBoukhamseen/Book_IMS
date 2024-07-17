from sqlalchemy import select
from app.database.connector import connect_to_db
from app.database.Schemas.books import Book
from app.database.Schemas.preferences import Preferences
from app.database.Schemas.user import User
from app.database.Schemas.author import Author

def get_book_recommendations(email: str):
    try:
        engine, session = connect_to_db()
        stmt = select(Preferences.preference).where(Preferences.email == email)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            genres = list(map(lambda x: x[0], results.fetchall()))
            if len(genres) == 0:
                return False
            stmt = select(Book.title).where(Book.genre.in_(genres)).limit(5)
            results = conn.execute(stmt)
            recommendations = list(map(lambda x: x[0], results.fetchall()))
            if len(recommendations) == 0:
                return False
            return recommendations
    except Exception as e:
        return e
    finally:
        session.close()

if __name__ == "__main__":
    print(get_book_recommendations("email_0@gmail.com"))
