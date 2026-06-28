from __future__ import annotations

from app.database.session import SessionLocal
from sqlalchemy import text


# LEGACY: keep for now until the repository-based SQL flow is migrated.
def answer_sql(query: str):
    """
    Safe SQL execution layer (prototype-safe version)
    """

    db = SessionLocal()

    try:
        # VERY SAFE: we do NOT execute raw user SQL
        # instead we map intent → predefined queries

        if "vendor" in query.lower():
            sql = "SELECT * FROM vendors LIMIT 5"

        elif "audit" in query.lower():
            sql = "SELECT * FROM audit_logs LIMIT 5"

        elif "compliance" in query.lower():
            sql = "SELECT * FROM compliance_reviews LIMIT 5"

        else:
            return "No matching SQL pattern found."

        result = db.execute(text(sql)).fetchall()

        return str([dict(row._mapping) for row in result])

    except Exception as e:
        return f"SQL Error: {str(e)}"

    finally:
        db.close()


def answer_from_database(question: str):
    return answer_sql(question)
