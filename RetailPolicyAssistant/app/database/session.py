"""
Database session configuration.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from pgvector.sqlalchemy import Vector
from app.core import settings
from app.models.base import Base

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,  # Neon requires this
)

# Enable pgvector on connection
@event.listens_for(engine, "connect")
def enable_pgvector(dbapi_conn, connection_record):
    """Enable pgvector extension on each connection."""
    with dbapi_conn.cursor() as cursor:
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            dbapi_conn.commit()
        except Exception:
            dbapi_conn.rollback()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()