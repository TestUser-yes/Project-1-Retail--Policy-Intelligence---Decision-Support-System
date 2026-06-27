-- Database schema for compliance and policy data

CREATE TABLE vendors (
    vendor_id INTEGER PRIMARY KEY,
    name TEXT,
    risk_level TEXT,
    status TEXT,
    country TEXT
);

CREATE TABLE audit_logs (
    log_id INTEGER PRIMARY KEY,
    vendor_id INTEGER,
    event TEXT,
    timestamp TEXT
);

CREATE TABLE retention_records (
    record_id INTEGER PRIMARY KEY,
    data_type TEXT,
    retention_period TEXT,
    legal_hold BOOLEAN
);

CREATE TABLE compliance_reviews (
    review_id INTEGER PRIMARY KEY,
    vendor_id INTEGER,
    status TEXT,
    findings TEXT
);
