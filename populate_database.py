from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text, Table, MetaData, inspect, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import random

Base = declarative_base()
metadata = MetaData()

class User(Base):
    __tablename__ = 'users'
    email = Column('email', String(100), primary_key=True)
    fname = Column('fname', String(50))
    lname = Column('lname', String(50))
    hashed_pw = Column('hashed_pw', String(100))
    role = Column('role', Integer)

class Author(Base):
    __tablename__ = 'authors'
    author_id = Column('author_id', Integer, primary_key=True)
    name = Column('name', String(100))
    biography = Column('biography', Text)

class Book(Base):
    __tablename__ = 'books'
    book_id = Column("book_id", Integer, primary_key=True)
    author_id = Column("author_id", Integer, ForeignKey('authors.author_id'))
    title = Column("title", String(150))
    genre = Column("genre", String(30))
    description = Column("description", Text)
    year = Column("year", Integer)
    author = relationship("Author")


class Preferences(Base):
    __tablename__ = 'preferences'
    email = Column("email", String(100), ForeignKey('users.email'), primary_key=True)
    preference = Column("preference", String(30), primary_key=True)
    user = relationship("User")

DATABASE_URL = "postgresql+psycopg2://postgres:password@127.0.0.1:5432/test" # change the url password and database name
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

emails = [f"email_{i}@gmail.com" for i in range(30)]
fnames = [f"fname_{i}" for i in range(30)]
lnames = [f"lname_{i}" for i in range(30)]
hashed_pws = [hash(f"password_{i}") for i in range(30)]
roles = [0]*15 + [1]*15

users_inserts = [User(email=email, fname=fname, lname=lname, hashed_pw=hashed_pw, role=role) for email, fname, lname, hashed_pw, role in zip(emails, fnames, lnames, hashed_pws, roles)]
session.add_all(users_inserts)

author_ids = [i for i in range(30)]
names = [f"name_{i}" for i in range(30)]
biographies = [f"some_biography_{i}" for i in range(30)]

authors = [Author(author_id=author_id, name=name, biography=biography) for author_id, name, biography in zip(author_ids, names, biographies)]
session.add_all(authors)

book_ids = [i for i in range(30)]
titles = [f"title_{i}" for i in range(30)]
genres = [f"genre_{i}" for i in range(30)]
descriptions = [f"some_description_{i}" for i in range(30)]
years = [i for i in range(1990, 2020)]

books = [Book(book_id=book_id, author_id=author_id, title=title, genre=genre, description=description, year=year) for book_id, author_id, title, genre, description, year in zip(book_ids, author_ids, titles, genres, descriptions, years)]
session.add_all(books)

session.commit()

preferences = [[f"pref_{i}" for i in range(random.randint(3, 7))] for _ in range(30)]

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
