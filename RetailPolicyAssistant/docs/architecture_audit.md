# Architecture Audit

## Status Legend

- ✅ Keep
- 🔄 Refactor
- ❌ Remove
- 🆕 New

---

## app/

| File | Purpose | Status | Notes |
|------|----------|--------|-------|
| api.py | | | |
| classifier.py | Classifies user queries into RAG, SQL, or Hybrid and assigns a basic risk level | 🔄 Refactor | Move to app/services/classifier_service.py. Replace keyword matching with LLM-based intent classification later. |
| database.py | | | |
| llm.py | | | |
| prompts.py | | | |
| rag.py | Retrieves relevant policy content from chunks.json using keyword matching and returns answers with source citations | 🔄 Refactor | Split into multiple RAG components (loader, chunker, embedding service, vector store, retriever, generator). Replace keyword search with semantic vector search using pgvector and embeddings. |
| router.py | Routes classified user queries to RAG, SQL, or Hybrid workflows and merges hybrid responses | 🔄 Refactor | Move to app/services/router_service.py. Replace direct function calls with service classes and LangGraph orchestration later. |
| sql.py | Retrieves structured compliance data from SQLite using predefined SQL queries and formats results | 🔄 Refactor | Replace SQLite access with SQLAlchemy ORM and PostgreSQL. Introduce SQL service, validation layer, and eventually an LLM-powered SQL Agent with guardrails. |
| utils.py | | | |

---

## app/api/

| File | Purpose | Status |
|------|----------|--------|

---

## app/database/

| File | Purpose | Status |
|------|----------|--------|

---

## app/core/

| File | Purpose | Status |
|------|----------|--------|

---

## app/models/

| File | Purpose | Status |
|------|----------|--------|

---

## app/services/

| File | Purpose | Status |
|------|----------|--------|

---

## app/rag/

| File | Purpose | Status |
|------|----------|--------|

---

## app/workflows/

| File | Purpose | Status |
|------|----------|--------|

---

## app/agents/

| File | Purpose | Status |
|------|----------|--------|
