from sqlalchemy import select
from app.database.connector import connect_to_db
from app.database.Schemas.user import User
from app.utils.hash import deterministic_hash

def authenticate_user(email, password):
    try:
        engine, session = connect_to_db()
        stmt = select(User.hashed_pw).where(User.email == email)
        with engine.connect() as conn:
            results = conn.execute(statement=stmt)
            output = results.fetchone()
            if output is None:
                return False, "User not registered"
            else:
                print(output[0], deterministic_hash(password))
                if output[0] == deterministic_hash(password):
                    return True, "Login successful"
                else:
                    return False, "Wrong password"
    except Exception as e:
        print(e)
    finally:
        session.close()

if __name__ == "__main__":
    print(authenticate_user(
        email="email_200@gmail.com",
        password="password_1"
    ))
