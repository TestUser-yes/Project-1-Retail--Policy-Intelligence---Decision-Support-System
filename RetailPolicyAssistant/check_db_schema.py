"""Check what tables actually exist in the Neon database."""

import os
from dotenv import load_dotenv
from sqlalchemy import inspect, text

load_dotenv()

from app.database.session import engine

if __name__ == "__main__":
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"[INFO] Tables in Neon database: {len(tables)}")
        for table in sorted(tables):
            print(f"  - {table}")

        if "policy_documents" in tables:
            print("\n[OK] policy_documents table EXISTS")
            columns = inspector.get_columns("policy_documents")
            print("Columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("\n[ERROR] policy_documents table DOES NOT EXIST")
            print("Need to create it manually or fix the init script")

    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
        import traceback
        traceback.print_exc()
