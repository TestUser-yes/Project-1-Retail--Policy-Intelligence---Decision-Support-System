#!/usr/bin/env python
"""System health check - verifies all dependencies and services before running backend."""

import sys
import os
from pathlib import Path

print("\n" + "=" * 60)
print("SYSTEM HEALTH CHECK - PRE-DEPLOYMENT VERIFICATION")
print("=" * 60 + "\n")

checks = {
    "PASS": [],
    "WARN": [],
    "FAIL": []
}

# Check 1: Python Version
try:
    if sys.version_info >= (3, 8):
        checks["PASS"].append("Python version: {}".format(sys.version.split()[0]))
    else:
        checks["FAIL"].append("Python {} (requires 3.8+)".format(sys.version.split()[0]))
except Exception as e:
    checks["FAIL"].append("Python check failed: {}".format(e))

# Check 2: Environment Variables
try:
    from app.core.config import settings
    checks["PASS"].append("Configuration loaded successfully")
    print("  DATABASE_URL: {}...".format(settings.DATABASE_URL[:50]))
    print("  OLLAMA_BASE_URL: {}".format(settings.OLLAMA_BASE_URL))
except Exception as e:
    checks["FAIL"].append("Configuration error: {}".format(e))

# Check 3: FastAPI
try:
    import fastapi
    checks["PASS"].append("FastAPI: {}".format(fastapi.__version__))
except ImportError:
    checks["FAIL"].append("FastAPI not installed: pip install fastapi")

# Check 4: SQLAlchemy
try:
    import sqlalchemy
    checks["PASS"].append("SQLAlchemy: {}".format(sqlalchemy.__version__))
except ImportError:
    checks["FAIL"].append("SQLAlchemy not installed: pip install sqlalchemy")

# Check 5: PostgreSQL Connection
try:
    from app.database.session import SessionLocal
    db = SessionLocal()
    db.execute("SELECT 1")
    db.close()
    checks["PASS"].append("PostgreSQL connection: OK")
except Exception as e:
    checks["WARN"].append("PostgreSQL connection failed: {}".format(e))
    checks["WARN"].append("  - Ensure PostgreSQL is running")

# Check 6: Ollama Connection
try:
    import requests
    from app.core.config import settings
    response = requests.get("{}/api/tags".format(settings.OLLAMA_BASE_URL), timeout=5)
    if response.status_code == 200:
        checks["PASS"].append("Ollama connection: OK")
    else:
        checks["WARN"].append("Ollama returned status {}".format(response.status_code))
except Exception as e:
    checks["WARN"].append("Ollama connection failed: {}".format(e))
    checks["WARN"].append("  - Ensure Ollama is running: ollama serve")

# Check 7: LangChain
try:
    from langchain_community.embeddings import OllamaEmbeddings
    checks["PASS"].append("LangChain: OK")
except ImportError:
    checks["WARN"].append("LangChain not fully installed")

# Check 8: Agents
try:
    from app.agents.intent_agent import IntentAgent
    from app.agents.rag_agent import RAGAgent
    from app.agents.sql_agent import SQLAgent
    checks["PASS"].append("All agents imported successfully")
except Exception as e:
    checks["FAIL"].append("Agent import failed: {}".format(e))

# Print Results
print("\nCHECK RESULTS:")
print("-" * 60)

for status, items in checks.items():
    if items:
        status_label = "[{}]".format(status)
        print("\n{}".format(status_label))
        for item in items:
            print("  {}".format(item))

print("\n" + "=" * 60)

# Summary
ok_count = len(checks["PASS"])
warn_count = len(checks["WARN"])
err_count = len(checks["FAIL"])

print("\nSUMMARY: {} Pass | {} Warnings | {} Failures".format(ok_count, warn_count, err_count))

if err_count > 0:
    print("\nFAILURES DETECTED - Fix them before running:")
    for item in checks["FAIL"]:
        print("  - {}".format(item))
    sys.exit(1)
elif warn_count > 0:
    print("\nWARNINGS: Some features may have issues")
    print("System can still run with fallbacks")
else:
    print("\nAll systems ready for deployment")

print("\n" + "=" * 60 + "\n")
