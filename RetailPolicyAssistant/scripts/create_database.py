from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_DIR = ROOT / "database" / "database"
DB_PATH = DB_DIR / "retail_policy.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


def create_database() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        cursor = conn.cursor()

        cursor.executemany(
            "INSERT INTO vendors (vendor_id, name, risk_level, status, country) VALUES (?, ?, ?, ?, ?)",
            [
                (1, "Acme Supplies", "medium", "approved", "USA"),
                (2, "Global Export Ltd", "high", "pending approval", "India"),
                (3, "RetailPro Partners", "low", "active", "USA"),
            ],
        )

        cursor.executemany(
            "INSERT INTO audit_logs (log_id, vendor_id, event, timestamp) VALUES (?, ?, ?, ?)",
            [
                (1, 1, "Invoice mismatch detected", "2026-06-01T10:00:00Z"),
                (2, 2, "Supplier compliance review scheduled", "2026-06-05T13:00:00Z"),
                (3, 3, "Unexpected audit access pattern", "2026-06-10T09:15:00Z"),
            ],
        )

        cursor.executemany(
            "INSERT INTO retention_records (record_id, data_type, retention_period, legal_hold) VALUES (?, ?, ?, ?)",
            [
                (1, "customer data", "7 years", 0),
                (2, "financial records", "10 years", 1),
                (3, "supplier contracts", "6 years", 0),
            ],
        )

        cursor.executemany(
            "INSERT INTO compliance_reviews (review_id, vendor_id, status, findings) VALUES (?, ?, ?, ?)",
            [
                (1, 1, "passed", "No findings."),
                (2, 2, "pending", "Review for restricted jurisdiction."),
                (3, 3, "failed", "Missing audit evidence."),
            ],
        )

        conn.commit()

    print(f"Created SQLite database at {DB_PATH}")


if __name__ == "__main__":
    create_database()
