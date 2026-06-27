"""
Simple PostgreSQL connection test.
"""

from sqlalchemy import text

from app.database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database();"))
        database_name = result.scalar()

        print("=" * 50)
        print("✅ Database connection successful!")
        print(f"Connected to database: {database_name}")
        print("=" * 50)

except Exception as error:
    print("=" * 50)
    print("❌ Database connection failed!")
    print(error)
    print("=" * 50)
