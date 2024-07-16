from sqlalchemy import create_engine
import psycopg2
import random

dialect = "postgresql"
driver = "psycopg2"
username = "postgres"
password = "password" # Change to your own password
host = "127.0.0.1"
port = "5432"
database_name = "test" # Change to your own database name

conn = psycopg2.connect(
    dbname=database_name,
    user=username,
    password=password,
    host=host,
    port=port
)

print(conn)

engine = create_engine(f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database_name}")

print(engine)

cur = conn.cursor()

cur.execute("""
DROP TABLE IF EXISTS employees;
""")

cur.execute("""
DROP TABLE IF EXISTS users;
""")

cur.execute("""
DROP TABLE IF EXISTS books;
""")

cur.execute("""
DROP TABLE IF EXISTS authors;
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(100) PRIMARY KEY,
    fname VARCHAR(50),
    lname VARCHAR(50),
    hashed_pw VARCHAR(100),
    ROLE INT
);
""")

emails = [f"email_{i}@gmail.com" for i in range(30)]
fname = [f"fname_{i}" for i in range(30)]
lname = [f"lname_{i}" for i in range(30)]
hashed_pw =  [hash(f"password_{i}") for i in range(30)]
role = [0]*15 + [1]*15
users_inserts = list(zip(emails, fname, lname, hashed_pw, role))

cur.executemany(
    "INSERT INTO users (email, fname, lname, hashed_pw, role) VALUES (%s, %s, %s, %s,%s)",
    users_inserts
)

cur.execute("""
CREATE TABLE IF NOT EXISTS authors (
    author_id INT PRIMARY KEY,
    name VARCHAR(100),
    biography VARCHAR(500)
)
""")
author_id = [str(i) for i in range(30)]
name = [f"name_{i}" for i in range(30)]
biography = [f"some_biography_{i}" for i in range(30)]
authors_inserts = list(zip(author_id, name, biography))
cur.executemany(
    "INSERT INTO authors (author_id, name, biography) VALUES (%s, %s, %s)",
    authors_inserts
)

cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INT PRIMARY KEY,
    author_id INT,
    title VARCHAR(150),
    genre VARCHAR(30),
    description VARCHAR(500),
    year INT,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
)
""")
book_id = [str(i) for i in range(30)]
author_id = [str(i) for i in range(30)]
title = [f"title_{i}" for i in range(30)]
genre = [f"title_{i}" for i in range(30)]
description = [f"some_description_{i}" for i in range(30)]
year = [i for i in range(1990, 2020)]
books_inserts = list(zip(book_id, author_id, title, genre, description, year))

cur.executemany(
    "INSERT INTO books (book_id, author_id, title, genre, description, year) VALUES (%s, %s, %s, %s, %s, %s)",
    books_inserts
)

conn.commit()

def fetch_from_database(db_name):
    print("\t\n"+"*"*20, f"{db_name}", "*"*20+"\t\n")
    cur.execute(f"SELECT * FROM {db_name}")
    rows = cur.fetchall()
    for row in rows:
        print(row)

preferences = [[f"pref_{i}" for i in range(random.randint(3, 7))] for _ in range(30)]
cur.execute(f"SELECT * FROM users")
rows = cur.fetchall()

for i, row in enumerate(rows):
    email = row[0]
    cur.execute(f"DROP TABLE IF EXISTS preferences_{i};")
    cur.execute(f'''
            CREATE TABLE IF NOT EXISTS preferences_{i} (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100),
                book_title VARCHAR(255),
                FOREIGN KEY (email) REFERENCES users(email)
            )
        '''
    )
    book_list = preferences[i]
    for book in book_list:
        cur.execute(f'''
            INSERT INTO preferences_{i} (email, book_title)
            VALUES (%s, %s)
        ''', (email, book))

fetch_from_database("users")
fetch_from_database("authors")
fetch_from_database("books")
fetch_from_database("preferences_29")

# cur.execute('''
# SELECT book_title 
# FROM preferences_29
# WHERE preferences_29.email = (SELECT email FROM users WHERE users.fname = %s);
# ''', ('fname_29',))
# rows = cur.fetchall()
# print(rows)

cur.close()
conn.close()