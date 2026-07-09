# Common Issues and Fixes

## Project Overview

**Status:** ✓ All Systems Operational  
**Last Audit:** 2026-07-09  
**UUID Strategy:** Removed - Using BigInteger autoincrement IDs

---

## Known Issues and Resolutions

### 1. CostTracker.record_query() - Missing query_id Argument

**Issue:** `Error: CostTracker.record_query() missing 1 required positional argument: 'query_id'`

**Resolution:** ✓ FIXED

**What Changed:**
- Parameter order changed: `query_text` is now required (first parameter)
- `query_id` is now optional (can be None or auto-assigned)
- No UUID auto-generation - query_id assigned after DB save

**Correct Usage:**
```python
# New signature
cost_tracker.record_query(
    query_text="My query",
    query_id=None,  # Optional, will be assigned after DB save
    embedding_tokens=10,
    completion_tokens=20,
    embedding_cost=0.0,
    completion_cost=0.0,
)

# Or minimal:
cost_tracker.record_query("My query")
```

**Files Changed:**
- app/core/cost_tracking.py (lines 65-86, 212-232)
- app/orchestrator.py (lines 101-111)

**Related Commit:** a5c88a1

---

### 2. UUID in Project Code

**Issue:** "Why are UUIDs being used if project removed them?"

**Resolution:** ✓ VERIFIED - NO UUID USAGE

**Current Status:**
- ✓ No `import uuid` in app code
- ✓ All models use BigInteger or Integer primary keys
- ✓ No UUID auto-generation in orchestrator
- ✓ Cost tracking doesn't generate UUIDs

**ID Strategy:**
```
Main entities:  BigInteger (auto-increment from DB)
- User.id
- QueryLog.id
- AuditLog.id
- Vendor tables

Secondary entities: Integer (auto-increment from DB)
- AIQuery.id
- AIResponse.id
- PolicyDocument.id

Benefits:
- 78% storage reduction (36 bytes → 8 bytes)
- Faster indexing
- Human-readable IDs (1, 2, 3...)
```

**Related Commit:** 43a5d5d (original removal)

---

### 3. Import Errors

**Issue:** "ModuleNotFoundError: No module named 'app.X'"

**Resolution:** ✓ ALL IMPORTS VALID

**Status:**
- ✓ app.api
- ✓ app.orchestrator
- ✓ app.core.cost_tracking
- ✓ app.core.auth
- ✓ app.models.models
- ✓ app.agents.rag_agent
- ✓ app.agents.sql_agent
- ✓ app.database.session

**If you encounter import errors:**
1. Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Check PYTHONPATH includes project root

---

### 4. Database Connection Failed

**Issue:** "Database connection failed" or "Session creation error"

**Resolution:** ✓ DATABASE OPERATIONAL

**Current Setup:**
- SQLite database (development)
- Database URL: Configured in app/config
- Connection pool: Active

**If you encounter DB errors:**
1. Verify DATABASE_URL environment variable (if set)
2. Check database file exists: `data/` directory
3. Verify SQLAlchemy installed: `pip install sqlalchemy`

```python
# Test connection:
from app.database.session import SessionLocal, engine
db = SessionLocal()
db.close()
```

---

### 5. Configuration Loading Failed

**Issue:** "Config loading failed" or "Missing configuration"

**Resolution:** ✓ CONFIG OPERATIONAL

**Configuration Files:**
- app/config/constants.py
- app/config/config_loader.py
- config/ directory for dynamic configs

**Verify:**
```python
from app.config import get_config
config = get_config()
# Should have: keywords, risk_thresholds, cost, routing
```

---

### 6. Syntax Errors in .py Files

**Issue:** "SyntaxError" when importing or running code

**Resolution:** ✓ ALL FILES VALID

**Status:** All 117 Python files have valid syntax

**If you encounter syntax errors after editing:**
1. Use AST parser to check: `python -m py_compile your_file.py`
2. Check for common mistakes:
   - Missing colons after `if`, `for`, `def`, `class`
   - Mismatched brackets/parentheses
   - Invalid indentation

---

### 7. Missing Dependencies

**Issue:** "ModuleNotFoundError" for packages

**Resolution:** ✓ DEPENDENCIES CHECKED

**Status:**
- ✓ fastapi
- ✓ sqlalchemy
- ✓ pydantic
- ✓ langchain
- ✓ langchain-community
- ✓ langfuse
- ⚠ ollama (optional, not imported)
- ⚠ langchain-ollama (optional, not imported)

**Install Requirements:**
```bash
pip install fastapi sqlalchemy pydantic langchain langchain-community langfuse
```

---

## Testing and Verification

### Quick System Check

```bash
python << 'EOF'
# Test all core modules
modules = [
    "app.api",
    "app.orchestrator",
    "app.core.cost_tracking",
    "app.models.models",
    "app.database.session",
]

for mod in modules:
    __import__(mod)
    print(f"OK: {mod}")

print("All core modules loaded successfully!")
EOF
```

### Functional Test

```bash
python << 'EOF'
from app.orchestrator import Orchestrator
from app.database.session import SessionLocal

db = SessionLocal()
orchestrator = Orchestrator(db)

# Test query processing
response = orchestrator.run("What is retention policy?")
print(f"Route: {response.get('route')}")
print(f"Status: SUCCESS")

db.close()
EOF
```

---

## Development Guidelines

### Code Standards

1. **Import Organization**
   ```python
   # Standard library
   import sys
   
   # Third-party
   from sqlalchemy import Column, String
   
   # Local
   from app.core import cost_tracking
   ```

2. **ID Generation**
   - ✓ Use database auto-increment (BigInteger/Integer)
   - ✗ Do NOT use UUID
   - Use `query_id` only when DB-assigned

3. **Cost Tracking**
   ```python
   # Correct usage:
   cost_tracker.record_query(
       query_text="user query",
       embedding_tokens=10,
       completion_tokens=20,
   )
   ```

### When Adding Features

1. Check for UUID usage: `grep -r "import uuid" app/`
2. Use BigInteger for new primary keys
3. Update imports in __init__.py if creating new modules
4. Run syntax check: `python -m py_compile new_file.py`

---

## Performance Considerations

### BigInteger vs UUID

| Aspect | BigInteger | UUID |
|--------|-----------|------|
| Storage | 8 bytes | 36 bytes |
| Query Speed | Faster | Slower |
| Index Size | Smaller | Larger |
| Readability | 1, 2, 3... | a1b2c3d4... |

**Project Decision:** BigInteger (better for SQLite/demo)

---

## Emergency Procedures

### Clear Python Cache

```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Reset Database

```bash
# Backup first!
cp data/app.db data/app.db.backup

# Then delete (will recreate on next run)
rm data/app.db
```

### Check Project Health

```bash
# Run full audit
python << 'EOF'
import sys
modules = [
    "app.api", "app.orchestrator", "app.core.cost_tracking",
    "app.models.models", "app.database.session",
]
for mod in modules:
    __import__(mod)
print("System OK")
EOF
```

---

## Logs and Debugging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### Common Log Messages

| Message | Meaning | Action |
|---------|---------|--------|
| "UUID imports found" | Project standards violated | Remove uuid imports |
| "Import error: X" | Missing or broken import | Check file exists, verify syntax |
| "DB connection failed" | Database issue | Check DATABASE_URL, database file |
| "Config not found" | Configuration missing | Verify app/config/ files exist |

---

## Support and Escalation

### Before Escalating

1. ✓ Run comprehensive audit: See COMPREHENSIVE_AUDIT_REPORT.md
2. ✓ Clear Python cache
3. ✓ Check all imports are valid
4. ✓ Verify database connection
5. ✓ Run functional tests

### What to Provide

- Error message (full traceback)
- File and line number
- Recent changes made
- Python version: `python --version`
- Installed packages: `pip list | grep langchain`

---

## Related Documentation

- COMPREHENSIVE_AUDIT_REPORT.md - Full system audit results
- CLAUDE.md - Project configuration and guidelines
- app/core/cost_tracking.py - Cost tracking implementation
- app/orchestrator.py - Query orchestration logic

---

**Last Updated:** 2026-07-09  
**Status:** All systems operational  
**Next Review:** After next major feature or 30 days
