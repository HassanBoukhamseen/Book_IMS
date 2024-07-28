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
from datetime import UTC
import pandas as pd



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

book_data = pd.read_csv("app/utils/books.csv")
for column in book_data.columns:
    if column in ['title', 'subtitle', 'authors', 'categories', 'description', 'thumbnail']:
        book_data[column] = book_data[column].fillna("Unknown")
book_data["ratings_count"] = book_data["ratings_count"].fillna(book_data["ratings_count"].mean())
book_data["num_pages"] = book_data["num_pages"].fillna(book_data["num_pages"].mean())
book_data["average_rating"] = book_data["average_rating"].fillna(book_data["average_rating"].mean())
book_data["published_year"] = book_data["published_year"].fillna(book_data["published_year"].mean())

names = book_data.authors.apply(lambda x: str(x)).unique().tolist()

biographies = [f"some_biography_{i}" for i in range(len(names))]
authors = [Author(name=name, biography=biography) for name, biography in zip(names, biographies)]

session.add_all(authors)
session.commit()

author_ids = [author.author_id for author in authors]
author_name_id_mapping = {name:author_id for name, author_id in zip(names, author_ids)}

book_id = book_data.isbn10
titles = book_data.title
subtitle = book_data.subtitle
genres = book_data.categories
thumbnail = book_data.thumbnail
descriptions = book_data.description
authors = book_data.authors
years = book_data.published_year
average_rating = book_data.average_rating
num_pages = book_data.num_pages
ratings_count = book_data.ratings_count

book_entries = zip(
    book_id, 
    titles,
    subtitle,
    genres,
    thumbnail, 
    descriptions, 
    authors,
    years,
    average_rating,
    num_pages,
    ratings_count
)

books = [
    Book(
            book_id=book_id,
            author_id=author_name_id_mapping[author],
            title=title, 
            author_name=author,
            subtitle=subtitle,
            thumbnail=thumbnail,
            genre=genre,
            description=description,        
            year=year,
            rating=average_rating,
            num_pages=num_pages,
            ratings_count=ratings_count
        ) \
        for book_id, title, subtitle, genre, thumbnail, description, author, year, average_rating, num_pages, ratings_count \
        in book_entries]
session.add_all(books)
session.commit()

request_logs = [
    RequestLog(endpoint="/books", method="GET", request_body=None, timestamp=datetime.now(UTC)),
    RequestLog(endpoint="/authors", method="GET", request_body=None, timestamp=datetime.now(UTC)),
    RequestLog(endpoint="/books/1", method="GET", request_body=None, timestamp=datetime.now(UTC)),
    RequestLog(endpoint="/authors/1", method="GET", request_body=None, timestamp=datetime.now(UTC)),
    RequestLog(endpoint="/books", method="POST", request_body='{"title": "New Book", "author_id": 1, "genre": "genre_0", "description": "A new book", "year": 2021}', timestamp=datetime.now(UTC))
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

# fetch_from_database("users")
fetch_from_database("authors")
fetch_from_database("books")
# fetch_from_database("preferences")

session.close()
