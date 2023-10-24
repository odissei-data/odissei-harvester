import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_DB_URL = os.environ['POSTGRES_DB_URL']

engine = create_engine(POSTGRES_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    This function creates a database session,
    yield it to the get_db function, rollback the transaction
    if there's an exception and then finally closes the session.

    Yields:
        db: scoped database session
    """

    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
    finally:
        db.close()
