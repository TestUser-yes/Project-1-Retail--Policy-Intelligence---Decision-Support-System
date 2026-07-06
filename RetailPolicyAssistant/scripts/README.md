# Scripts - Essential Utilities

This folder contains only **essential, non-redundant utility scripts** for the Retail Policy Intelligence system.

---

## Available Scripts

### 1. **init_db.py** - Database Initialization
- **Purpose:** Create database schema from SQLAlchemy models
- **When to use:** First time setup, after major model changes
- **Command:** `python scripts/init_db.py`
- **Output:** All tables created in Neon PostgreSQL

### 2. **seed_policies.py** - Load Sample Data
- **Purpose:** Populate database with sample policy documents
- **When to use:** After database initialization
- **Command:** `python scripts/seed_policies.py`
- **Output:** Sample policies with embeddings loaded

### 3. **check_system.py** - Pre-Deployment Health Check
- **Purpose:** Verify all dependencies and services before running backend
- **When to use:** Before starting the backend
- **Command:** `python scripts/check_system.py`
- **Output:** System readiness report with any issues identified
- **Checks:**
  - Python version (3.8+)
  - Configuration loading
  - FastAPI installation
  - SQLAlchemy installation
  - PostgreSQL connection
  - Ollama connection
  - LangChain installation
  - Agent imports

### 4. **test_golden_set.py** - Evaluation Framework
- **Purpose:** Run golden set evaluation against test queries
- **When to use:** Quality assurance and testing
- **Command:** `python scripts/test_golden_set.py`
- **Output:** Evaluation metrics and results

### 5. **run_evaluation.py** - Run Evaluations
- **Purpose:** Execute comprehensive system evaluations
- **When to use:** Performance testing and benchmarking
- **Command:** `python scripts/run_evaluation.py`
- **Output:** Detailed evaluation report

---

## Quick Start

### First Time Setup
```bash
# 1. Initialize database
python scripts/init_db.py

# 2. Load sample data
python scripts/seed_policies.py

# 3. Check system
python scripts/check_system.py

# 4. Start backend
python -m uvicorn app.main:app --reload --port 8000
```

### Before Each Session
```bash
# Verify all systems are ready
python scripts/check_system.py
```

### Running Tests
```bash
# Run golden set evaluation
python scripts/test_golden_set.py

# Run full evaluation
python scripts/run_evaluation.py
```

---

## Removed Scripts

The following redundant scripts have been removed for clarity:

- **create_database.py** - Replaced by init_db.py
- **create_policy_table.py** - Replaced by init_db.py
- **recreate_policy_table.py** - Replaced by init_db.py
- **reinit_db.py** - Replaced by init_db.py
- **check_db_schema.py** - Functionality covered by check_system.py
- **verify_db.py** - Functionality covered by check_system.py
- **test_connection.py** - Functionality covered by check_system.py
- **test_neon_connection.py** - Functionality covered by check_system.py
- **index_documents_from_pdfs.py** - Incomplete/stub
- **index_policies.py** - Redundant
- **ingest_documents.py** - Duplicate functionality

---

## Code Quality Standards

All scripts follow professional standards:
- No emojis in code (non-professional)
- Clean, readable output formatting
- Proper error handling
- Comprehensive logging
- Enterprise-grade quality

---

## Script Status

- init_db.py - Production ready
- seed_policies.py - Production ready
- check_system.py - Production ready (emoji-free)
- test_golden_set.py - Production ready
- run_evaluation.py - Production ready

---

**All scripts are essential and non-redundant.**
