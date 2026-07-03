# Project Cleanup & Reorganization Plan

**Date:** 2026-07-03  
**Status:** Analysis Complete - Ready for Implementation

---

## 📊 Current Project Issues

### 1. Duplicate Modules (CRITICAL)
```
❌ RAG Duplication:
   - Root: rag/ingest.py, rag/retriever.py
   - app: app/rag/ingest.py, app/rag/retriever.py
   Action: DELETE root /rag folder (app/rag is authoritative)

❌ Database Duplication:
   - app/database/ (base.py, session.py)
   - app/db/ (deps.py)
   - Root: db_init.py, create_database.py
   Action: CONSOLIDATE to app/database/

❌ LLM Module:
   - app/llm/ (folder structure)
   - app/llm.py (root level)
   Action: CONSOLIDATE to app/llm/

❌ SQL Module:
   - app/sql/ (folder structure)
   - app/sql.py (root level)
   Action: CONSOLIDATE to app/sql/

❌ API Location:
   - api/ (root folder - empty)
   - app/api/ (folder structure)
   - app/api.py (root level)
   Action: CONSOLIDATE to app/api/
```

### 2. Empty/Unused Directories
```
❌ Completely Empty:
   - api/api/
   - app/api/
   - app/schemas/
   - app/services/
   - app/utils/
   - app/workflows/
   - embeddings/
   - logs/
   - policies/

⚠️  Mostly Empty (only cache files):
   - __pycache__/
   - .pytest_cache/
   - venv/ (should be in .gitignore)
```

### 3. Orphaned Root-Level Files
```
❌ Utility Scripts (Should be in scripts/):
   - check_system.py → scripts/check_system.py
   - create_database.py → scripts/setup_database.py
   - ingest_documents.py → scripts/ingest_documents.py
   - run_evaluation.py → scripts/run_evaluation.py
   - test_rag.py → tests/test_rag_integration.py

❌ Duplicate/Old Folders:
   - /api/ (root) - unused
   - /rag/ (root) - duplicate of app/rag/
   - /database/ (root) - duplicate of app/database/
   - /observability/ (root) - duplicate of app/observability/
   - /workflows/ (root) - empty
```

### 4. Confusing Multiple Locations
```
Configuration:
   - app/core/config.py ✅ Keep

Logging:
   - app/core/logging.py
   - app/observability/logger.py
   Action: CONSOLIDATE (choose one)

Database Session:
   - app/database/session.py
   - app/db/deps.py
   Action: CONSOLIDATE
```

---

## ✅ Proposed Clean Structure

```
RetailPolicyAssistant/
├── app/                          # ✅ Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI entry point
│   ├── orchestrator.py           # Main orchestration logic
│   │
│   ├── agents/                   # ✅ All 6 agents
│   │   ├── __init__.py
│   │   ├── base.py               # Base agent class
│   │   ├── intent_agent.py
│   │   ├── rag_agent.py
│   │   ├── sql_agent.py
│   │   ├── hybrid_agent.py
│   │   ├── risk_agent.py
│   │   └── escalation_agent.py
│   │
│   ├── api/                      # ✅ API routes (consolidated)
│   │   ├── __init__.py
│   │   ├── endpoints.py          # All endpoints
│   │   └── schemas.py            # Request/response schemas
│   │
│   ├── core/                     # ✅ Core utilities
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration
│   │   ├── logging.py            # Logging setup
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── cost_tracking.py      # Cost tracking
│   │
│   ├── database/                 # ✅ Database (consolidated)
│   │   ├── __init__.py
│   │   ├── base.py               # Base models
│   │   ├── session.py            # DB session
│   │   └── dependencies.py       # DB dependencies
│   │
│   ├── models/                   # ✅ SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── policy.py
│   │   ├── vendor.py
│   │   ├── audit.py
│   │   ├── ai_queries.py
│   │   ├── ai_response.py
│   │   ├── compliance.py
│   │   ├── evaluation.py
│   │   └── retention.py
│   │
│   ├── rag/                      # ✅ RAG (consolidated)
│   │   ├── __init__.py
│   │   ├── pipeline.py           # Main RAG pipeline
│   │   ├── retriever.py          # Document retrieval
│   │   ├── ingest.py             # Document ingestion
│   │   ├── loader.py             # Document loading
│   │   ├── splitter.py           # Text splitting
│   │   ├── context.py            # Context building
│   │   └── answer.py             # Answer generation
│   │
│   ├── sql/                      # ✅ SQL (consolidated)
│   │   ├── __init__.py
│   │   └── queries.py            # SQL queries
│   │
│   ├── llm/                      # ✅ LLM (consolidated)
│   │   ├── __init__.py
│   │   ├── base.py               # Base LLM class
│   │   ├── ollama_llm.py         # Ollama implementation
│   │   └── service.py            # LLM service
│   │
│   ├── embeddings.py             # ✅ Embeddings configuration
│   ├── indexer.py                # ✅ Indexing
│   ├── prompts.py                # ✅ Prompt templates
│   ├── router.py                 # ✅ Route selection logic
│   ├── session.py                # ✅ Session management
│   ├── rag.py                    # ✅ RAG convenience module
│   ├── sql.py                    # ✅ SQL convenience module
│   ├── llm.py                    # ✅ LLM convenience module
│   │
│   ├── repositories/             # ✅ Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── policy_repo.py
│   │   ├── vendor_repo.py
│   │   ├── audit_repo.py
│   │   ├── compliance_repo.py
│   │   ├── evaluation_repo.py
│   │   └── ai_repo.py
│   │
│   ├── evaluation/               # ✅ Evaluation metrics
│   │   ├── __init__.py
│   │   ├── evaluator.py
│   │   ├── metrics.py
│   │   ├── answer_metric.py
│   │   ├── route_metric.py
│   │   ├── risk_metric.py
│   │   ├── latency_metric.py
│   │   ├── escalation_metric.py
│   │   ├── slos.py
│   │   └── utils.py
│   │
│   └── observability/            # ✅ Logging & metrics
│       ├── __init__.py
│       ├── logger.py             # Advanced logging
│       └── metrics.py            # Metrics collection
│
├── tests/                        # ✅ Test suite (73 tests)
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_agents.py
│   ├── test_models.py
│   ├── test_orchestrator.py
│   ├── test_api.py
│   ├── test_vector_store_model.py
│   └── load_test.py
│
├── scripts/                      # ✅ Utility scripts
│   ├── __init__.py
│   ├── setup_database.py         # Database setup (formerly create_database.py)
│   ├── ingest_documents.py       # Document ingestion
│   ├── run_evaluation.py         # Run evaluations
│   ├── check_system.py           # System verification
│   └── test_connection.py        # Connection testing
│
├── data/                         # ✅ Data directory
│   └── chunks.json               # Cached chunks
│
├── docs/                         # ✅ Documentation
│   └── architecture_audit.md
│
├── evaluation/                   # ✅ Evaluation data
│   └── golden_queries.csv
│
├── frontend/                     # ✅ React frontend
│   ├── src/
│   ├── package.json
│   └── ...
│
├── .env                          # Configuration
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore (should include venv/)
├── main.py                       # Alternative entry point
└── pytest.ini                    # Pytest configuration
```

---

## 🗑️ Files & Folders to DELETE

### Complete Removal (Unused)
```
❌ api/                           # Root API folder (empty)
❌ rag/                           # Root RAG folder (duplicate)
❌ database/                      # Root database folder (duplicate)
❌ observability/                 # Root observability folder (duplicate)
❌ workflows/                     # Empty workflows folder
❌ embeddings/                    # Empty embeddings folder
❌ logs/                          # Empty logs folder
❌ policies/                      # Empty policies folder
❌ Documents/                     # If empty
❌ __pycache__/                   # Cache (auto-generated)
❌ .pytest_cache/                 # Cache (auto-generated)
```

### Consolidate/Move
```
→ app/api.py → app/api/endpoints.py
→ app/llm.py → Consolidate into app/llm/
→ app/sql.py → Consolidate into app/sql/
→ app/rag.py → Consolidate into app/rag/

→ Root: check_system.py → scripts/check_system.py
→ Root: create_database.py → scripts/setup_database.py
→ Root: ingest_documents.py → scripts/ingest_documents.py
→ Root: run_evaluation.py → scripts/run_evaluation.py
→ Root: test_rag.py → tests/test_rag_integration.py
```

### Update Imports
```
app/api.py         → app/api/endpoints.py
app/llm.py         → app/llm/__init__.py (re-export)
app/sql.py         → app/sql/__init__.py (re-export)
app/rag.py         → app/rag/__init__.py (re-export)

All imports updated to use new paths
```

---

## 📋 Implementation Steps

1. **Backup Current State**
   - Git commit current state
   - Create backup branch

2. **Delete Empty Directories**
   - Remove: api/, workflows/, embeddings/, logs/, policies/
   - Remove: unused root-level directories

3. **Consolidate Duplicate Modules**
   - Move root RAG files to app/rag/
   - Consolidate app/db/ into app/database/
   - Consolidate app/llm.py into app/llm/
   - Consolidate app/sql.py into app/sql/

4. **Move Root Scripts to scripts/**
   - check_system.py
   - create_database.py
   - ingest_documents.py
   - run_evaluation.py
   - test_rag.py

5. **Update All Imports**
   - Test imports still work
   - Update in main.py
   - Update in tests/

6. **Verify Functionality**
   - Run: python -m pytest tests/ -v
   - Run: python -m app.main (or appropriate entry point)
   - Check: All imports working

7. **Update Documentation**
   - Update README
   - Update ARCHITECTURE.md
   - Update file references in docs

8. **Git Commit**
   - Commit with detailed message
   - Document cleanup rationale

---

## 📊 Project Stats After Cleanup

```
Before:
├── Directories: 18 (many empty/duplicate)
├── Python Files: 95+
├── Issues: 10+ (duplicates, confusion, empty dirs)

After:
├── Directories: 12 (organized, no duplicates)
├── Python Files: 80+ (consolidated)
├── Issues: 0 (clean structure)
├── Clarity: Maximum
└── Maintainability: High
```

---

## ✅ Quality Checklist

- [ ] All empty directories deleted
- [ ] No duplicate modules remain
- [ ] All imports updated and tested
- [ ] Scripts moved to scripts/ folder
- [ ] Root level cleanup complete
- [ ] 73 tests still passing
- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] Documentation updated
- [ ] Git history preserved

---

## 🎯 Final Clean Structure Benefits

1. **Clarity** - No confusion about where code should go
2. **Maintainability** - Clear organization and hierarchy
3. **Scalability** - Easy to add new features
4. **Testing** - Clear test structure
5. **Documentation** - Self-documenting file structure
6. **Performance** - No import confusion
7. **Quality** - Professional project layout

---

**Status:** ✅ Plan Complete - Ready for Implementation
