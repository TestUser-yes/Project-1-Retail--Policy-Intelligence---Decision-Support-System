#!/usr/bin/env python
"""
System Health Check Script
Verifies all dependencies and services before running the backend
"""

import sys
import os
from pathlib import Path

print("\n" + "=" * 60)
print("RETAIL POLICY SYSTEM - DEPENDENCY CHECK")
print("=" * 60 + "\n")

checks = {
    "✅": [],
    "⚠️": [],
    "❌": []
}

# Check 1: Python Version
try:
    if sys.version_info >= (3, 8):
        checks["✅"].append(f"Python version: {sys.version.split()[0]}")
    else:
        checks["❌"].append(f"Python {sys.version.split()[0]} (requires 3.8+)")
except Exception as e:
    checks["❌"].append(f"Python check failed: {e}")

# Check 2: Environment Variables
try:
    from app.core.config import settings
    checks["✅"].append("Configuration loaded successfully")
    print(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"  OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
    print(f"  OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
except Exception as e:
    checks["❌"].append(f"Configuration error: {e}")

# Check 3: FastAPI
try:
    import fastapi
    checks["✅"].append(f"FastAPI: {fastapi.__version__}")
except ImportError:
    checks["❌"].append("FastAPI not installed: pip install fastapi")

# Check 4: SQLAlchemy
try:
    import sqlalchemy
    checks["✅"].append(f"SQLAlchemy: {sqlalchemy.__version__}")
except ImportError:
    checks["❌"].append("SQLAlchemy not installed: pip install sqlalchemy")

# Check 5: PostgreSQL Connection
try:
    from app.database.session import SessionLocal
    db = SessionLocal()
    result = db.execute("SELECT 1")
    db.close()
    checks["✅"].append("PostgreSQL connection: OK")
except Exception as e:
    checks["⚠️"].append(f"PostgreSQL connection failed: {e}")
    checks["⚠️"].append("  → Make sure PostgreSQL is running")

# Check 6: Ollama Connection
try:
    import requests
    from app.core.config import settings
    response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
    if response.status_code == 200:
        checks["✅"].append(f"Ollama connection: OK")
    else:
        checks["⚠️"].append(f"Ollama returned status {response.status_code}")
except Exception as e:
    checks["⚠️"].append(f"Ollama connection failed: {e}")
    checks["⚠️"].append("  → Make sure Ollama is running: ollama serve")

# Check 7: LangChain
try:
    from langchain_community.embeddings import OllamaEmbeddings
    checks["✅"].append("LangChain: OK")
except ImportError:
    checks["⚠️"].append("LangChain not installed (embeddings may fallback)")

# Check 8: Agents
try:
    from app.agents.intent_agent import IntentAgent
    from app.agents.rag_agent import RAGAgent
    from app.agents.sql_agent import SQLAgent
    checks["✅"].append("All agents imported successfully")
except Exception as e:
    checks["❌"].append(f"Agent import failed: {e}")

# Print Results
print("\nCHECK RESULTS:")
print("-" * 60)

for status, items in checks.items():
    if items:
        print(f"\n{status}")
        for item in items:
            print(f"  {item}")

print("\n" + "=" * 60)

# Summary
ok_count = len(checks["✅"])
warn_count = len(checks["⚠️"])
err_count = len(checks["❌"])

print(f"\nSUMMARY: {ok_count} OK | {warn_count} Warnings | {err_count} Errors")

if err_count > 0:
    print("\n⚠️  ERRORS DETECTED - Fix them before running:")
    for item in checks["❌"]:
        print(f"   • {item}")
    sys.exit(1)
elif warn_count > 0:
    print("\n⚠️  WARNINGS: Some features may not work optimally")
    print("   But the system can still run with fallbacks")
else:
    print("\n✅ All systems ready!")

print("\n" + "=" * 60 + "\n")
