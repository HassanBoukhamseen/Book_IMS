from sqlalchemy import select
from app.database.connector import connect_to_db
from app.database.Schemas.user import User
from app.utils.hash import deterministic_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_user(user_data):
    try:
        engine, session = connect_to_db()
        logger.info("Connected to the database")

        select_user_email = select(User.email).where(User.email == user_data.email)
        logger.info(f"Executing query: {select_user_email}")
        with engine.connect() as conn:
            results = conn.execute(select_user_email)
            output = results.fetchone()
            logger.info(f"Query results: {output}")
            if output is not None:
                logger.info("User already registered")
                return False, "User already registered"

        # Hash the password
        hashed_pw = deterministic_hash(user_data.password)
        logger.info(f"Hashed password: {hashed_pw}")

        # Create a new user instance
        new_user = User(
            email=user_data.email,
            fname=user_data.fname,
            lname=user_data.lname,
            hashed_pw=hashed_pw,
            role=user_data.role
        )

        session.add(new_user)
        session.commit()
        logger.info("User registered successfully")

        return True, "User registered successfully"
    
    
    except Exception as e:
        # Print and return the error message if an exception occurs
        logger.error(f"Exception occurred: {e}")
        return False, str(e)
    finally:
        # Close the session
        session.close()
        logger.info("Session closed")