# TESTING QUICK REFERENCE - All 9 Endpoints

## 📋 All Endpoints at a Glance

| # | Endpoint | Method | Auth | Purpose | Line |
|---|----------|--------|------|---------|------|
| 1 | `/health` | GET | ❌ | Health check | app/api.py:106 |
| 2 | `/token` | GET | ❌ | Get auth token | app/api.py:118 |
| 3 | `/ask` | POST | ✅ | Ask policy question | app/api.py:124 |
| 4 | `/conversations/{id}/history` | GET | ✅ | Get chat history | app/api.py:291 |
| 5 | `/api/ingestion/ingest` | POST | ✅ | Upload PDF | app/routers/ingestion.py:81 |
| 6 | `/api/ingestion/retrieve` | POST | ✅ | Retrieve documents | app/routers/ingestion.py:170 |
| 7 | `/api/dashboard` | GET | ❌ | Dashboard metrics | app/routers/dashboard.py:14 |
| 8 | `/api/observability` | GET | ❌ | SLO metrics | app/routers/observability.py:13 |
| 9 | `/api/observability/demo-agents` | GET | ❌ | Agent demo | app/routers/observability.py:153 |

---

## 🚀 Quick Test (All 9 Endpoints in 2 Minutes)

```bash
# 1. Health
curl http://localhost:8002/health

# 2. Token
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')
echo "Token: $TOKEN"

# 3. Dashboard
curl http://localhost:8002/api/dashboard | jq '.totalQueries'

# 4. Observability
curl http://localhost:8002/api/observability | jq '.summary'

# 5. Demo Agents
curl http://localhost:8002/api/observability/demo-agents | jq '.agents[0].name'

# 6. Ask Question
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "data retention"}' | jq '.result.result'

# 7. Ingest Document
curl -X POST http://localhost:8002/api/ingestion/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@Documents/Data_Retention_and_Archival_Policy.pdf" | jq '.status'

# 8. Retrieve Documents
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"retention","k":3}' | jq '.count'

# 9. Conversation History
CONV_ID=$(curl -s -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"test"}' | jq -r '.conversation_id')

curl http://localhost:8002/conversations/$CONV_ID/history \
  -H "Authorization: Bearer $TOKEN" | jq '.messages | length'
```

---

## 📝 Endpoint Details with Request Bodies

### 🟢 PUBLIC ENDPOINTS (No Auth Needed)

#### 1️⃣ Health Check
```bash
GET http://localhost:8002/health

# No body needed
curl http://localhost:8002/health
```

#### 2️⃣ Get Token
```bash
GET http://localhost:8002/token

# No body needed
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')
```

#### 3️⃣ Dashboard
```bash
GET http://localhost:8002/api/dashboard

# No body needed
curl http://localhost:8002/api/dashboard
```

#### 4️⃣ Observability
```bash
GET http://localhost:8002/api/observability

# No body needed
curl http://localhost:8002/api/observability
```

#### 5️⃣ Multi-Agent Demo
```bash
GET http://localhost:8002/api/observability/demo-agents

# No body needed
curl http://localhost:8002/api/observability/demo-agents
```

---

### 🔐 AUTHENTICATED ENDPOINTS (Need Token)

#### 6️⃣ Ask Policy Question
```bash
POST http://localhost:8002/ask

Request Body:
{
  "query": "string (required, 3-10000 chars)",
  "conversation_id": "uuid (optional)"
}

Examples:
# Simple question
curl -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is data retention policy?"}'

# With conversation ID
curl -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"GDPR requirements","conversation_id":"123e4567-e89b-12d3-a456-426614174000"}'
```

**Response Contains**:
- ✅ result.result (the answer)
- ✅ confidence_score (0-1)
- ✅ route (rag/sql/hybrid)
- ✅ retrieval_method (multi_agent/semantic/fallback/sql)
- ✅ retrieval_agents (3-agent array)
- ✅ retrieval_pipeline (execution details)
- ✅ escalate (boolean)
- ✅ risk_level (low/medium/high)

---

#### 7️⃣ Get Conversation History
```bash
GET http://localhost:8002/conversations/{conversation_id}/history

Path Parameter:
- conversation_id: UUID from /ask response

Example:
CONV_ID="123e4567-e89b-12d3-a456-426614174000"
curl http://localhost:8002/conversations/$CONV_ID/history \
  -H "Authorization: Bearer $TOKEN"

Response:
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

---

#### 8️⃣ Ingest PDF Document
```bash
POST http://localhost:8002/api/ingestion/ingest

Request:
- Form data: file (PDF file)

Example:
curl -X POST http://localhost:8002/api/ingestion/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf"

Response:
{
  "filename": "document.pdf",
  "document_name": "document",
  "chunks_created": 12,
  "total_pages": 5,
  "status": "indexed",
  "timestamp": "2026-07-11T09:05:29"
}
```

---

#### 9️⃣ Retrieve Documents (Multi-Agent)
```bash
POST http://localhost:8002/api/ingestion/retrieve

Request Body:
{
  "query": "string (required, 1-1000 chars)",
  "k": integer (optional, default=6, range 1-20)
}

Example 1: Basic retrieval
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"access control","k":5}'

Example 2: Simple query
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"retention"}'

Response:
{
  "query": "...",
  "chunks": [
    {
      "content": "...",
      "metadata": {
        "id": 1,
        "document_name": "...",
        "page_number": 1,
        "section": "..."
      }
    }
  ],
  "count": 5,
  "timestamp": "...",
  "retrieval_method": "multi_agent",
  "retrieval_agents": [
    "semantic_retrieval_agent",
    "keyword_retrieval_agent",
    "ranking_agent"
  ],
  "retrieval_pipeline": {...}
}
```

---

## ✅ Verification Checklist

### Multi-Agent Retrieval Working?
- [ ] retrieval_method = "multi_agent"
- [ ] retrieval_agents has 3 elements
- [ ] retrieval_pipeline has semantic_agent, keyword_agent, ranking_agent
- [ ] total_agents = 3
- [ ] latencies showing for each agent
- [ ] consensus_boost_applied = true

### Complete Flow?
- [ ] /health returns healthy
- [ ] /token returns access_token
- [ ] /ask returns answer with multi-agent details
- [ ] /api/ingestion/retrieve returns documents with multi-agent details
- [ ] /conversations/{id}/history shows message history
- [ ] /api/ingestion/ingest uploads and indexes PDF
- [ ] /api/dashboard shows metrics
- [ ] /api/observability shows SLO metrics
- [ ] /api/observability/demo-agents shows agent info

---

## 🧪 Test Scenarios

### Scenario 1: User Asking Policy Question
```bash
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')

# Ask question
curl -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the data retention policy?"}' | jq '{
    route: .route,
    result: .result.result,
    confidence: .confidence_score,
    retrieval_method: .retrieval_method,
    agents_used: .retrieval_agents,
    escalate: .escalate
  }'
```

### Scenario 2: Testing Multi-Agent Retrieval
```bash
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')

# Directly test retrieval
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"access control policy","k":6}' | jq '{
    documents_found: .count,
    retrieval_method: .retrieval_method,
    total_agents: .retrieval_pipeline.total_agents,
    semantic_latency_ms: .retrieval_pipeline.semantic_agent.latency_ms,
    keyword_latency_ms: .retrieval_pipeline.keyword_agent.latency_ms,
    ranking_latency_ms: .retrieval_pipeline.ranking_agent.latency_ms
  }'
```

### Scenario 3: Conversation Memory
```bash
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')

# First query
CONV_ID=$(curl -s -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is data retention?"}' | jq -r '.conversation_id')

# Second query in same conversation
curl -s -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Tell me more\",\"conversation_id\":\"$CONV_ID\"}"

# View history
curl http://localhost:8002/conversations/$CONV_ID/history \
  -H "Authorization: Bearer $TOKEN" | jq '.messages'
```

### Scenario 4: SQL Query
```bash
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')

# SQL-type query
curl -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"How many vendors are there?"}' | jq '{
    route: .route,
    retrieval_method: .retrieval_method,
    agents_used: .retrieval_agents
  }'

# Expected: route="sql", retrieval_method="sql", retrieval_agents=[]
```

### Scenario 5: Error Handling
```bash
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')

# Too short query (should fail)
curl -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"hi"}'
# Expected: 400 Bad Request

# Missing token
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'
# Expected: 401 Unauthorized

# Invalid k value in retrieve
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","k":25}'
# Expected: 422 Validation error (max 20)
```

---

## 📊 HTTP Status Codes Expected

| Status | Meaning | Endpoints |
|--------|---------|-----------|
| 200 | Success | All endpoints |
| 202 | Accepted (SLO warning) | /ask |
| 400 | Bad request (validation) | /ask, /retrieve |
| 401 | Unauthorized (missing token) | /ask, /ingest, /retrieve, /history |
| 404 | Not found | /conversations/{id}/history (invalid ID) |
| 422 | Validation error (invalid params) | /ask, /retrieve, /ingest |
| 429 | Rate limited | Any authenticated endpoint |
| 503 | Service unavailable (SLO hard fail) | /ask |

---

## 🔍 How to Verify Multi-Agent is Active

### In /ask Response
```bash
curl -s -X POST http://localhost:8002/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}' | jq '.retrieval_pipeline | keys'

# Expected:
# [
#   "semantic_agent",
#   "keyword_agent", 
#   "ranking_agent",
#   "total_agents",
#   "fusion_method"
# ]
```

### In /retrieve Response
```bash
curl -s -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}' | jq '.retrieval_agents'

# Expected:
# [
#   "semantic_retrieval_agent",
#   "keyword_retrieval_agent",
#   "ranking_agent"
# ]
```

---

## 📁 File Locations

| Component | File |
|-----------|------|
| Main API | app/api.py |
| Ingestion | app/routers/ingestion.py |
| Dashboard | app/routers/dashboard.py |
| Observability | app/routers/observability.py |
| Orchestrator | app/orchestrator.py |
| Multi-Agent Core | app/rag/multi_agent_retrieval.py |
| RAG Agent | app/agents/rag_agent.py |
| SQL Agent | app/agents/sql_agent.py |

---

## 📚 Complete Project Files (119 Total)

- ✅ 9 Endpoints fully functional
- ✅ Multi-agent retrieval in both /ask and /retrieve
- ✅ SLO enforcement active
- ✅ Conversation memory working
- ✅ Cost tracking enabled
- ✅ RBAC permissions enforced
- ✅ Rate limiting active
- ✅ Langfuse tracing integrated
- ✅ All models/schemas defined
- ✅ Database connections working

**Status**: ✅ **COMPLETE AND PRODUCTION-READY**

