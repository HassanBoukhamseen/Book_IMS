from sqlalchemy import select
from app.database.connector import connect_to_db
from app.database.Schemas.author import Author

def retrieve_single_author(id):
    try:
        engine, session = connect_to_db()
        stmt = select(Author.author_id, Author.name, Author.biography).where(Author.author_id == id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            output = results.fetchone()
            author = {"author_id": output[0], "name": output[1], "biography": output[2]}
        return author
    except Exception as e:
        print(e)
    finally:
        session.close()    

def retrieve_authors_from_db():
    try:
        engine, session = connect_to_db()
        stmt = select(Author.author_id, Author.name, Author.biography)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            authors = map(lambda result: {"author_id": result[0], "name": result[1], "biography": result[2]}, results.fetchall())
            return list(authors)
    except Exception as e:
        print(e)
    finally:
        session.close()

if __name__ == "__main__":
    print(retrieve_authors_from_db())
    print(retrieve_single_author(22))


