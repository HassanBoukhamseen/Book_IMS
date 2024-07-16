from app.database.connector import connect_to_db
from app.database.Schemas.base import Base
from app.database.Schemas.user import User

def create_tables():
    engine, _ = connect_to_db()
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()