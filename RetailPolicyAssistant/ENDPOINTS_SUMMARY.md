# API Endpoints Summary - Complete Reference

## Quick Overview: 8 Total Endpoints

| # | Method | Path | Auth | Purpose |
|---|--------|------|------|---------|
| 1 | GET | `/health` | No | System health |
| 2 | GET | `/token` | No | Get demo token |
| 3 | POST | `/ask` | Yes | Main query (RAG/SQL/Hybrid) |
| 4 | GET | `/conversations/{id}/history` | Yes | Get conversation memory |
| 5 | GET | `/api/dashboard` | No | Dashboard metrics |
| 6 | GET | `/api/observability` | Yes | Trace/metrics |
| 7 | **POST** | **`/api/ingestion/ingest`** | **Yes** | **[NEW] Upload & index PDF** |
| 8 | **POST** | **`/api/ingestion/retrieve`** | **Yes** | **[NEW] Search documents** |

---

## Detailed Endpoint Reference

### 1️⃣ Health Check Endpoint

```http
GET /health
```

**Purpose:** Verify system is running

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "system": "Retail Policy AI",
  "agents": "active",
  "db": "connected",
  "timestamp": "2026-07-10"
}
```

**Use:** Health monitoring, deployment checks

---

### 2️⃣ Get Demo Token

```http
GET /token
```

**Purpose:** Get temporary authentication token for testing

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Use:** Get token for testing other endpoints

---

### 3️⃣ Main Query Endpoint (Core Functionality)

```http
POST /ask
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the data retention policy?",
  "conversation_id": "conv-123"  // optional, auto-generated if empty
}
```

**Processing Flow:**
1. ✅ Authenticate user (JWT)
2. ✅ Check permission (ASK_POLICY_QUESTION)
3. ✅ Validate query (3-10000 chars)
4. ✅ Rate limit check
5. ✅ Get/create conversation memory
6. ✅ Orchestrator.run():
   - Detect intent (SQL/RAG/Hybrid)
   - Route to appropriate agent:
     - **SQL Agent**: Text-to-SQL query generation
     - **RAG Agent**: PDF document retrieval + LLM
     - **Hybrid**: Combined approach
   - Risk assessment (low/medium/high)
   - Escalation check
   - SLO tracking
7. ✅ Save query to audit log
8. ✅ Add response to conversation memory
9. ✅ Log to observability (Langfuse)

**Response:**
```json
{
  "query": "What is the data retention policy?",
  "conversation_id": "conv-123",
  "intent": {
    "intent": "rag",
    "reason": "Query classified as policy question"
  },
  "route": "rag",
  "result": {
    "result": "Data retention policy specifies..."
  },
  "risk": {
    "risk_level": "low",
    "reason": "Routine policy query"
  },
  "escalate": false,
  "escalation_reason": "",
  "latency_seconds": 1.234,
  "cost_usd": 0.0,
  "budget_remaining_usd": 0.0,
  "budget_percent_used": 0.0,
  "slo_metrics": {
    "latency_ms": 1234.0,
    "target_latency_ms": 2000.0,
    "slo_status": "pass"
  },
  "validation_passed": true,
  "confidence_score": 0.92,
  "sources": [
    {
      "document": "Data_Retention_Policy.pdf",
      "page": 2,
      "section": "1. Introduction"
    }
  ],
  "sql_validation": "",
  "recommendation": ""
}
```

**Error Responses:**
- `400`: Invalid query format or content
- `401`: Not authenticated
- `403`: Permission denied
- `429`: Rate limit exceeded
- `500`: Server error

---

### 4️⃣ Get Conversation History

```http
GET /conversations/{conversation_id}/history
Authorization: Bearer <token>
```

**Purpose:** Retrieve conversation memory for a user

**Response:**
```json
{
  "conversation_id": "conv-123",
  "messages": [
    {
      "role": "user",
      "content": "What is the data retention policy?"
    },
    {
      "role": "assistant",
      "content": "Data retention policy specifies..."
    },
    {
      "role": "user",
      "content": "Tell me more about retention periods"
    },
    {
      "role": "assistant",
      "content": "Retention periods are typically..."
    }
  ]
}
```

**Use:** Retrieve conversation history, context for follow-up questions

---

### 5️⃣ Dashboard Metrics

```http
GET /api/dashboard
```

**Purpose:** Get aggregated system metrics for dashboard

**Response:**
```json
{
  "total_queries": 145,
  "recent_queries": [...],
  "risk_distribution": {
    "high": 12,
    "medium": 34,
    "low": 99
  },
  "route_distribution": {
    "rag": 89,
    "sql": 34,
    "hybrid": 22
  },
  "escalation_rate": 8.3,
  "avg_latency_ms": 1250,
  "top_intents": {
    "policy_question": 95,
    "compliance_check": 34,
    "vendor_info": 16
  }
}
```

---

### 6️⃣ Observability Metrics

```http
GET /api/observability
Authorization: Bearer <token>
```

**Purpose:** Get detailed traces, metrics, and performance data

**Response:**
```json
{
  "trace_id": "trace-abc123",
  "spans": [
    {
      "name": "ask_query",
      "duration_ms": 1234,
      "status": "success"
    },
    {
      "name": "rag_pipeline",
      "duration_ms": 1100,
      "status": "success"
    }
  ],
  "metrics": {
    "total_tokens": 1500,
    "embedding_tokens": 100,
    "completion_tokens": 1400
  },
  "latency_stats": {
    "p50_ms": 1000,
    "p95_ms": 1800,
    "p99_ms": 2500
  }
}
```

---

### 7️⃣ Document Ingestion (NEW)

```http
POST /api/ingestion/ingest
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <PDF file>
```

**Purpose:** Upload PDF document for indexing (Phase 1)

**Processing Flow:**
1. ✅ Authenticate + check permission
2. ✅ Validate file is PDF
3. ✅ Load with PyPDFLoader
4. ✅ Split with RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
5. ✅ Generate embeddings (OpenAI/Ollama/fallback)
6. ✅ Store in policy_documents table with pgvector
7. ✅ Return ingestion result

**Response:**
```json
{
  "filename": "Data_Retention_Policy.pdf",
  "document_name": "Data_Retention_Policy.pdf",
  "chunks_created": 45,
  "total_pages": 12,
  "status": "indexed",
  "timestamp": "2026-07-10T15:30:45.123456"
}
```

**Use:** Add new policy documents to system knowledge base

**Example cURL:**
```bash
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@Documents/Data_Retention_Policy.pdf" \
  http://localhost:8000/api/ingestion/ingest | jq
```

---

### 8️⃣ Document Retrieval (NEW)

```http
POST /api/ingestion/retrieve
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the data retention period?",
  "k": 6
}
```

**Purpose:** Search for relevant document chunks (Phase 2)

**Processing Flow:**
1. ✅ Authenticate + check permission
2. ✅ Embed query
3. ✅ Vector similarity search (pgvector)
4. ✅ Return top-k chunks with metadata

**Response:**
```json
{
  "query": "What is the data retention period?",
  "chunks": [
    {
      "content": "Data retention period is 7 years for customer records...",
      "metadata": {
        "id": 1,
        "document_name": "Data_Retention_Policy.pdf",
        "page_number": 2,
        "section": "3. Retention Periods",
        "chunk_number": 5
      }
    },
    {
      "content": "Archives older than retention period are deleted...",
      "metadata": {
        "id": 2,
        "document_name": "Data_Retention_Policy.pdf",
        "page_number": 3,
        "section": "4. Archive Management",
        "chunk_number": 8
      }
    }
  ],
  "count": 2,
  "timestamp": "2026-07-10T15:35:22.654321"
}
```

**Use:** Debug/test retrieval, inspect document chunks

**Example cURL:**
```bash
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the data retention period?","k":3}' \
  http://localhost:8000/api/ingestion/retrieve | jq
```

---

## Authentication & Rate Limits

### Getting a Token

```bash
# Get token (no auth needed)
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')

# Use token in subsequent requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/ingestion/retrieve
```

### Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/ask` | 60 | Per hour per user |
| `/api/ingestion/ingest` | 20 | Per hour per user |
| `/api/ingestion/retrieve` | 100 | Per hour per user |
| `/conversations/{id}/history` | 60 | Per hour per user |

### Permissions

| Permission | Endpoints |
|-----------|-----------|
| `ASK_POLICY_QUESTION` | `/ask`, `/api/ingestion/ingest`, `/api/ingestion/retrieve` |
| `VIEW_QUERY_HISTORY` | `/conversations/{id}/history` |
| `ADMIN_ACCESS` | All endpoints |

---

## Database Integration

### What Gets Stored

**From /ask endpoint:**
- Query text
- Detected intent (rag/sql/hybrid)
- Route taken
- Risk level assessment
- Latency (milliseconds)
- Response text
- Conversation history

**From /api/ingestion/ingest:**
- PDF filename
- Chunk text
- Chunk embeddings (1536-dim vector)
- Page number
- Section metadata
- Created timestamp

**From /api/ingestion/retrieve:**
- Query text
- Chunks retrieved
- Timestamp

---

## Query Routing Decision Tree

```
User Query (/ask)
  ├─ "SELECT * FROM...?" / SQL keywords
  │  └─ SQL Agent → Text-to-SQL → Database → Result
  │
  ├─ Policy / Retention / Compliance / Security / ...
  │  └─ RAG Agent → Vector Search → PDF Chunks → LLM → Answer
  │
  └─ Everything else
     └─ Hybrid Agent → Both approaches → Best result
```

---

## Example: End-to-End Workflow

### Step 1: Upload Policy Document

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@policy.pdf" \
  http://localhost:8000/api/ingestion/ingest

# Response:
# {
#   "chunks_created": 45,
#   "status": "indexed"
# }
```

### Step 2: Query About the Policy

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the data retention policy?"}' \
  http://localhost:8000/ask

# Response:
# {
#   "result": {
#     "result": "Data retention period is 7 years..."
#   },
#   "sources": [
#     {"document": "policy.pdf", "page": 2}
#   ],
#   "confidence_score": 0.92
# }
```

### Step 3: Check Conversation History

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/conversations/{conv-id}/history

# Response:
# {
#   "messages": [
#     {"role": "user", "content": "What is the data retention policy?"},
#     {"role": "assistant", "content": "Data retention period is 7 years..."}
#   ]
# }
```

### Step 4: Debug Retrieval

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "retention period"}' \
  http://localhost:8000/api/ingestion/retrieve

# Response:
# {
#   "chunks": [
#     {"content": "...", "metadata": {...}},
#     {"content": "...", "metadata": {...}}
#   ]
# }
```

---

## Status Summary

✅ **All 8 Endpoints Functional**
✅ **Authentication Working**
✅ **Rate Limiting Active**
✅ **Database Integration Complete**
✅ **Observability Enabled**
✅ **Error Handling Comprehensive**

**Ready for Production Deployment** ✅
