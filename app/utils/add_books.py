import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete, text
from app.database.schemas.books import Book
from app.database.schemas.author import Author
from app.database.connector import connect_to_db

# Function to delete all rows in books and authors tables and reset sequences
def reset_database():
    engine, session = connect_to_db()
    try:
        session.execute(delete(Book))
        session.execute(delete(Author))
        session.execute(text("ALTER SEQUENCE books_book_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE authors_author_id_seq RESTART WITH 1"))
        session.commit()
        print("All rows deleted and sequences reset successfully in books and authors tables.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while resetting the database: {e}")
    finally:
        session.close()

# Function to get or create an author
def get_or_create_author(session, author_name, biography=None):
    author = session.query(Author).filter_by(name=author_name).first()
    if not author:
        author = Author(name=author_name, biography=biography)
        session.add(author)
        session.commit()
        session.refresh(author)
    return author

# Function to add books and authors from the CSV
def add_books_from_csv(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Connect to the database
    engine, session = connect_to_db()

    try:
        for index, row in df.iterrows():
            # Get or create the author
            author_name = row['authors']
            biography = None  # Update this line if you have a biography in your dataset
            author = get_or_create_author(session, author_name, biography)
            
            # Create a new book entry
            book = Book(
                title=row['title'],
                genre=row['categories'],
                description=row['description'],
                year=row['published_year'],
                author_id=author.author_id
            )
            
            # Add the book to the session
            session.add(book)
        
        # Commit all the additions
        session.commit()
        print("Books and authors added successfully.")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")

    finally:
        session.close()

# Main execution
if __name__ == "__main__":
    csv_file_path = 'new_books.csv'
    reset_database()  # Delete all existing rows and reset sequences
    add_books_from_csv(csv_file_path)  # Then add new rows from the CSV
