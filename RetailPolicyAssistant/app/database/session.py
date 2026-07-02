"""
Database session configuration.

Creates the SQLAlchemy Engine and Session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.models.base import Base
from app.core import settings

# Create the SQLAlchemy engine
Base = declarative_base()
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,          # Change to True while debugging SQL queries
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    FastAPI dependency that provides
    a database session per request.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
