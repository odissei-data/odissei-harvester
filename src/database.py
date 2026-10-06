import os

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_DB_URL = os.environ.get('POSTGRES_DB_URL', 'postgresql://user:password@localhost/dbname')

engine = create_engine(POSTGRES_DB_URL)
# A fresh connection per readiness check: a pooled connection on a dead
# network waits for TCP timeouts, a new one fails after connect_timeout.
ready_engine = create_engine(POSTGRES_DB_URL, poolclass=NullPool,
                             connect_args={'connect_timeout': 2})
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
