import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.database.schemas.books import Book
from app.database.connector import connect_to_db

# Function to update the thumbnail column sequentially from a new CSV
def update_thumbnails_from_csv_sequentially(csv_file_path):
    # Read the new CSV file
    df = pd.read_csv(csv_file_path)

    # Connect to the database
    engine, session = connect_to_db()

    try:
        # Fetch all book records ordered by their primary key (or any other order)
        books = session.query(Book).order_by(Book.book_id).all()

        if len(books) != len(df):
            print("The number of records in the CSV does not match the number of books in the database.")
            return

        # Update each book record with the corresponding thumbnail from the CSV
        for book, (_, row) in zip(books, df.iterrows()):
            book.thumbnail = row['thumbnail']
            session.add(book)
        
        # Commit all the updates
        session.commit()
        print("Thumbnails updated successfully.")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")

    finally:
        session.close()

# Main execution
if __name__ == "__main__":
    csv_file_path = 'books.csv'
    update_thumbnails_from_csv_sequentially(csv_file_path)  # Update the thumbnails from the new CSV
