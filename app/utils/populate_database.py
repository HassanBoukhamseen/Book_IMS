from sqlalchemy import MetaData, text
from app.database.schemas.base import engine, session, Base
from app.database.schemas.user import User
from app.database.schemas.author import Author
from app.database.schemas.books import Book
from app.database.schemas.preferences import Preferences
from app.utils.hash import deterministic_hash
import random
from app.database.schemas.logs import RequestLog
from datetime import datetime


metadata = MetaData()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

emails = [f"email_{i}@gmail.com" for i in range(30)]
fnames = [f"fname_{i}" for i in range(30)]
lnames = [f"lname_{i}" for i in range(30)]
hashed_pws = [deterministic_hash(f"password_{i}") for i in range(30)]
roles = [0]*15 + [1]*15

users_inserts = [User(email=email, fname=fname, lname=lname, hashed_pw=hashed_pw, role=role) for email, fname, lname, hashed_pw, role in zip(emails, fnames, lnames, hashed_pws, roles)]
session.add_all(users_inserts)

author_ids = [i for i in range(1, 31)]
names = [f"name_{i}" for i in range(30)]
biographies = [f"some_biography_{i}" for i in range(30)]

authors = [Author(name=name, biography=biography) for name, biography in zip(names, biographies)]
session.add_all(authors)

titles = [f"title_{i}" for i in range(30)]
genres = [f"genre_{i}" for i in range(30)]
descriptions = [f"some_description_{i}" for i in range(30)]
years = [i for i in range(1990, 2020)]

books = [Book(author_id=author_id, title=title, genre=genre, description=description, year=year) for author_id, title, genre, description, year in zip(author_ids, titles, genres, descriptions, years)]
session.add_all(books)

request_logs = [
    RequestLog(endpoint="/books", method="GET", request_body=None, timestamp=datetime.utcnow()),
    RequestLog(endpoint="/authors", method="GET", request_body=None, timestamp=datetime.utcnow()),
    RequestLog(endpoint="/books/1", method="GET", request_body=None, timestamp=datetime.utcnow()),
    RequestLog(endpoint="/authors/1", method="GET", request_body=None, timestamp=datetime.utcnow()),
    RequestLog(endpoint="/books", method="POST", request_body='{"title": "New Book", "author_id": 1, "genre": "genre_0", "description": "A new book", "year": 2021}', timestamp=datetime.utcnow())
]
session.add_all(request_logs)

session.commit()

preferences = [list(set([f"genre_{random.randint(0, 29)}" for _ in range(random.randint(2, 7))])) for _ in range(30)]

for i, user in enumerate(users_inserts):
    email = users_inserts[i].email
    preferenc_inserts = [Preferences(email=email, preference=preference) for preference in preferences[i]]
    session.add_all(preferenc_inserts)

session.commit()
def fetch_from_database(table_name):
    print("\t\n" + "*" * 20, f"{table_name}", "*" * 20 + "\t\n")
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT * FROM {table_name}"))
        for row in result:
            print(row)

fetch_from_database("users")
fetch_from_database("authors")
fetch_from_database("books")
fetch_from_database("preferences")

session.close()
