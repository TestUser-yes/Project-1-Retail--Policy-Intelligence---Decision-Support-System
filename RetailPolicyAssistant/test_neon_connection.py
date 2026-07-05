"""Test Neon PostgreSQL connection and pgvector setup."""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not found in .env file")
    print("Follow the steps in NEON_SETUP_GUIDE.md")
    sys.exit(1)

if "[USER]" in DATABASE_URL or "[PASSWORD]" in DATABASE_URL:
    print("[ERROR] DATABASE_URL contains placeholder values")
    print("Replace [USER], [PASSWORD], [HOST], [DBNAME] with your Neon credentials")
    print(f"Current value: {DATABASE_URL}")
    sys.exit(1)

host = DATABASE_URL.split('@')[1].split(':')[0] if '@' in DATABASE_URL else 'Neon'
print(f"[TEST] Testing connection to: {host}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Test basic connection
        result = conn.execute(text("SELECT 1"))
        print("[OK] Database connection successful!")

        # Test pgvector
        try:
            result = conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("[OK] pgvector extension is available!")
        except Exception as e:
            print(f"[WARN] pgvector check: {e}")

        # Test Neon-specific features
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"[INFO] PostgreSQL: {version.split(',')[0]}")

        print("\n[SUCCESS] Everything looks good! Your project is ready to use Neon PostgreSQL.")

except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check DATABASE_URL in .env is correct")
    print("2. Verify Neon project is active at console.neon.tech")
    print("3. Ensure internet connection is working")
    sys.exit(1)
