from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import *  # This is now okay due to __all__ defining explicit exports
from contextlib import contextmanager



# Load the database URL from the app's configuration
from config import Config
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Initialize the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initializes the database by creating all tables.

    This function uses the `Base` metadata to create all tables
    defined in the models.
    """
    
    Base.metadata.create_all(bind=engine)

def commit_session(session):
    """
    Commits a SQLAlchemy session and handles errors.
    """
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

@contextmanager
def get_db_session():
    """
    Provides a context-managed session.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()