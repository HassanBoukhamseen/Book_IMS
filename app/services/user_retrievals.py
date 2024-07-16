from sqlalchemy import select
from app.database.connector import connect_to_db
from app.database.Schemas.user import User

def retrieve_single_user(id):
    try:
        engine, session = connect_to_db()
        stmt = select(User.email, User.fname, User.lname, User.role).where(User.email == id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            output = results.fetchone()
            user = {
                "email": output[0],
                "fname": output[1],
                "lname": output[2],
                "role": output[3],
            }
        return user
    except Exception as e:
        print(e)
    finally:
        session.close()

if __name__ == "__main__":
    print(retrieve_single_user("email_0@gmail.com"))
