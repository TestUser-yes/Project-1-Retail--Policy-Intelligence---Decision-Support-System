# COMPLETE TESTING GUIDE - ALL ENDPOINTS
## Step-by-Step Testing Instructions with Every Request Body

**Server URL**: `http://localhost:8002` (adjust port as needed)

---

## QUICK START - Get Token First

```bash
# Step 1: Always do this FIRST to get authentication token
curl http://localhost:8002/token

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# Save token to variable:
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

# SECTION 1: PUBLIC ENDPOINTS (No Authentication Required)

## ENDPOINT 1: Health Check
**Path**: `/health`  
**Method**: GET  
**Authentication**: ❌ NOT Required  
**Purpose**: Verify system health status

### Request:
```bash
curl http://localhost:8002/health
```

### Expected Response (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "system": "Retail Policy AI",
  "agents": "active",
  "db": "connected",
  "timestamp": "2026-07-03"
}
```

**What to Verify**:
- ✅ status = "healthy"
- ✅ agents = "active"
- ✅ db = "connected"

---

## ENDPOINT 2: Get Authentication Token
**Path**: `/token`  
**Method**: GET  
**Authentication**: ❌ NOT Required  
**Purpose**: Get demo token for all authenticated endpoints

### Request:
```bash
curl http://localhost:8002/token
```

### Expected Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGVtby11c2VyIiwidXNlcm5hbWUiOiJkZW1vIiwiZW1haWwiOiJkZW1vQHJldGFpbHBvbGljeS5sb2NhbCIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzgzNzY1MDg1fQ.sxnhcmVN0bOvx0FR5isiPZABAePBG3rGGhIIbAIeHHI",
  "token_type": "bearer"
}
```

**How to Use Token**:
```bash
TOKEN="<access_token from response>"
# Use in all authenticated requests:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/ask ...
```

**Save Token for All Tests**:
```bash
# Linux/Mac:
export TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')

# Windows PowerShell:
$TOKEN = (curl http://localhost:8002/token | ConvertFrom-Json).access_token
```

---

## ENDPOINT 3: Dashboard Metrics
**Path**: `/api/dashboard`  
**Method**: GET  
**Authentication**: ❌ NOT Required  
**Purpose**: Get aggregated dashboard metrics and real-time analytics

### Request:
```bash
curl http://localhost:8002/api/dashboard
```

### Expected Response (200 OK):
```json
{
  "totalQueries": 42,
  "avgLatency": 3.2,
  "escalationRate": 0.15,
  "budgetUsed": 0.35,
  "budgetUsdLimit": 100.0,
  "budgetUsdUsed": 35.0,
  "budgetRemaining": 65.0,
  "activeUsers": 5,
  "successRate": 0.92,
  
  "queryByRoute": {
    "rag": 25,
    "sql": 10,
    "hybrid": 7
  },
  
  "queryByRisk": {
    "low": 30,
    "medium": 10,
    "high": 2
  },
  
  "topPolicies": [
    {
      "policy": "Data Retention Policy",
      "count": 15
    }
  ],
  
  "topIntents": [
    {
      "intent": "policy_info",
      "count": 28
    }
  ],
  
  "recentQueries": [...],
  "hourlyTrends": [...],
  "vendorStats": {...},
  "sloMetrics": {...}
}
```

**What to Verify**:
- ✅ totalQueries > 0
- ✅ avgLatency is reasonable (< 10 seconds)
- ✅ escalationRate between 0-1
- ✅ budgetUsdUsed <= budgetUsdLimit

---

## ENDPOINT 4: Observability Metrics
**Path**: `/api/observability`  
**Method**: GET  
**Authentication**: ❌ NOT Required  
**Purpose**: Get detailed observability and SLO metrics

### Request:
```bash
curl http://localhost:8002/api/observability
```

### Expected Response (200 OK):
```json
{
  "timestamp": "2026-07-11T09:05:29.846760",
  
  "summary": {
    "total_queries": 42,
    "queries_24h": 12,
    "avg_confidence": 0.87,
    "escalation_rate": 0.15,
    "slo_compliance_rate": 0.88
  },
  
  "risk_distribution": {
    "low": 30,
    "medium": 10,
    "high": 2
  },
  
  "route_distribution": {
    "rag": 25,
    "sql": 10,
    "hybrid": 7
  },
  
  "slo_metrics": {
    "latency_target_ms": 2000,
    "latency_hard_limit_ms": 2400,
    "confidence_min": 0.70,
    "breaches_total": 5,
    "compliance_percent": 88.0
  },
  
  "hourly_trends": [...],
  "recent_queries": [...],
  "langfuse_traces": [...],
  
  "multi_agent_summary": {
    "total_retrievals": 25,
    "agents_used": ["semantic_retrieval_agent", "keyword_retrieval_agent", "ranking_agent"],
    "retrieval_methods": {
      "multi_agent": 18,
      "semantic": 5,
      "fallback": 2
    }
  }
}
```

**What to Verify**:
- ✅ slo_compliance_rate >= 0.8 (80% compliant)
- ✅ multi_agent retrievals tracked correctly
- ✅ All routes present in distribution

---

## ENDPOINT 5: Multi-Agent Demo
**Path**: `/api/observability/demo-agents`  
**Method**: GET  
**Authentication**: ❌ NOT Required  
**Purpose**: Educational endpoint showing multi-agent routing with example queries

### Request:
```bash
curl http://localhost:8002/api/observability/demo-agents
```

### Expected Response (200 OK):
```json
{
  "title": "Multi-Agent Query Routing Demo",
  
  "description": "Shows how queries are routed to different agents based on intent",
  
  "agents": [
    {
      "name": "RAG Agent",
      "type": "retrieval",
      "description": "Retrieves from PDF documents using multi-agent retrieval",
      "methods": ["semantic_similarity", "keyword_matching", "ranking_fusion"],
      "example_queries": [
        "What is the data retention policy?",
        "Tell me about GDPR requirements"
      ]
    },
    {
      "name": "SQL Agent",
      "type": "database",
      "description": "Queries database for structured data",
      "example_queries": [
        "How many vendors are approved?",
        "List all active policies"
      ]
    },
    {
      "name": "Hybrid Agent",
      "type": "combined",
      "description": "Combines RAG + SQL for comprehensive answers",
      "example_queries": [
        "What is our vendor policy and how many vendors do we have?"
      ]
    }
  ],
  
  "intent_detection": {
    "rag": "policy_info, requirements, procedures",
    "sql": "counting, listing, statistics",
    "hybrid": "combined questions"
  },
  
  "how_to_test": "Send queries to /ask endpoint..."
}
```

**What to Verify**:
- ✅ All agent types listed
- ✅ Example queries provided for each agent

---

# SECTION 2: AUTHENTICATED ENDPOINTS

### Prerequisites for All Authenticated Tests:
```bash
# Get token first
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')

# All authenticated requests use:
-H "Authorization: Bearer $TOKEN"
-H "Content-Type: application/json"
```

---

## ENDPOINT 6: Ask a Policy Question
**Path**: `/ask`  
**Method**: POST  
**Authentication**: ✅ REQUIRED  
**Purpose**: Main endpoint - ask any policy question with full orchestration

### Request Headers:
```bash
-H "Content-Type: application/json"
-H "Authorization: Bearer $TOKEN"
```

### Request Body Schema:
```json
{
  "query": "string (required, 3-10000 chars)",
  "conversation_id": "string (optional, UUID format, auto-generated if empty)"
}
```

### Test Cases:

#### TEST 6.1: Simple Policy Question
```bash
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What is the data retention policy?"
  }'
```

**Expected Response (200 OK or 202 Accepted)**:
```json
{
  "query": "What is the data retention policy?",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  
  "intent": {
    "intent": "rag",
    "reason": "Query classified as rag"
  },
  
  "route": "rag",
  
  "result": {
    "result": "Data retention policy requires..."
  },
  
  "risk": {
    "risk_level": "low",
    "reason": "Routine policy query"
  },
  
  "escalate": false,
  "escalation_reason": "",
  
  "latency_seconds": 4.5,
  "cost_usd": 0.01,
  "budget_remaining_usd": 99.99,
  "budget_percent_used": 0.01,
  
  "slo_metrics": {
    "latency_ms": 4500.0,
    "target_latency_ms": 2000.0,
    "slo_status": "fail",
    "slo_breached": true,
    "enforcement_action": "warning",
    "enforcement_reason": "Latency SLO target exceeded"
  },
  
  "validation_passed": true,
  "confidence_score": 0.92,
  
  "sources": [
    {
      "document": "Data_Retention_and_Archival_Policy.pdf",
      "page": 1,
      "section": "Retention Requirements"
    }
  ],
  
  "sql_validation": "Valid SQL generated",
  "recommendation": "Review with compliance officer before implementation",
  
  "agents_used": ["rag_agent"],
  "agent_details": [
    {
      "agent_name": "RAG Agent",
      "status": "success",
      "latency_ms": 4450.0,
      "confidence": 0.92,
      "data_source": "PDF Documents"
    }
  ],
  
  "retrieval_method": "multi_agent",
  "retrieval_agents": [
    "semantic_retrieval_agent",
    "keyword_retrieval_agent",
    "ranking_agent"
  ],
  
  "retrieval_pipeline": {
    "semantic_agent": {
      "agent": "semantic_retrieval_agent",
      "method": "embedding_similarity",
      "documents_retrieved": 6,
      "latency_ms": 245.3
    },
    "keyword_agent": {
      "agent": "keyword_retrieval_agent",
      "method": "keyword_matching",
      "keywords": ["data", "retention", "policy"],
      "documents_retrieved": 6,
      "latency_ms": 189.7
    },
    "ranking_agent": {
      "agent": "ranking_agent",
      "method": "multi_agent_fusion",
      "semantic_weight": 0.6,
      "keyword_weight": 0.4,
      "documents_fused": 10,
      "final_documents": 6,
      "consensus_boost_applied": true,
      "total_agents": 3,
      "latency_ms": 120.5
    }
  }
}
```

**What to Verify**:
- ✅ HTTP status 200 or 202
- ✅ result.result contains answer text
- ✅ confidence_score > 0 (0-1 range)
- ✅ route is "rag", "sql", or "hybrid"
- ✅ retrieval_method is "multi_agent", "semantic", "fallback", or "sql"
- ✅ retrieval_agents array has 3 agents
- ✅ retrieval_pipeline has semantic_agent, keyword_agent, ranking_agent
- ✅ sources array populated (if documents found)
- ✅ escalate is boolean

---

#### TEST 6.2: Question with Existing Conversation ID
```bash
CONV_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"query\": \"Tell me about GDPR requirements\",
    \"conversation_id\": \"$CONV_ID\"
  }"
```

**Expected Response**: Same structure as TEST 6.1

**What to Verify**:
- ✅ conversation_id matches the one provided
- ✅ Query is added to conversation history

---

#### TEST 6.3: SQL Query
```bash
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "How many vendors are approved?"
  }'
```

**Expected Response**:
```json
{
  "route": "sql",  // ← Should be SQL
  "agents_used": ["sql_agent"],
  "retrieval_method": "sql",
  "retrieval_agents": [],
  "retrieval_pipeline": {},
  ...
}
```

**What to Verify**:
- ✅ route = "sql"
- ✅ retrieval_method = "sql"
- ✅ retrieval_agents is empty []
- ✅ retrieval_pipeline is empty {}

---

#### TEST 6.4: High-Risk Query
```bash
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What are our compliance requirements for GDPR and how many vendors do we work with?"
  }'
```

**Expected Response**:
```json
{
  "route": "hybrid",  // ← Might be HYBRID
  "risk": {
    "risk_level": "high",
    "reason": "Query flagged for potential compliance risk"
  },
  "escalate": true,
  "escalation_reason": "Query flagged as high-risk - requires compliance review",
  ...
}
```

**What to Verify**:
- ✅ escalate = true for high-risk queries
- ✅ risk_level in ["low", "medium", "high"]
- ✅ escalation_reason is populated

---

#### TEST 6.5: Invalid Query (Too Short)
```bash
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "hi"
  }'
```

**Expected Response (400 Bad Request)**:
```json
{
  "detail": "Query validation failed: ..."
}
```

**What to Verify**:
- ✅ HTTP status 400
- ✅ Error message about validation

---

#### TEST 6.6: Missing Authentication Token
```bash
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the data retention policy?"
  }'
```

**Expected Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**What to Verify**:
- ✅ HTTP status 401
- ✅ Error about authentication

---

## ENDPOINT 7: Get Conversation History
**Path**: `/conversations/{conversation_id}/history`  
**Method**: GET  
**Authentication**: ✅ REQUIRED  
**Purpose**: Retrieve message history for a specific conversation

### Request:
```bash
CONV_ID="123e4567-e89b-12d3-a456-426614174000"

curl http://localhost:8002/conversations/$CONV_ID/history \
  -H "Authorization: Bearer $TOKEN"
```

### Expected Response (200 OK):
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  
  "messages": [
    {
      "role": "user",
      "content": "What is the data retention policy?"
    },
    {
      "role": "assistant",
      "content": "Data retention policy requires..."
    },
    {
      "role": "user",
      "content": "Tell me about GDPR requirements"
    },
    {
      "role": "assistant",
      "content": "GDPR compliance requires..."
    }
  ]
}
```

**What to Verify**:
- ✅ conversation_id matches request
- ✅ messages array contains alternating user/assistant
- ✅ Message content is accurate

---

## ENDPOINT 8: Ingest PDF Document
**Path**: `/api/ingestion/ingest`  
**Method**: POST  
**Authentication**: ✅ REQUIRED  
**Purpose**: Upload and index a PDF document into vector database

### Prerequisites:
- Have a PDF file ready to upload

### Request:
```bash
# Using curl with file upload
curl -X POST http://localhost:8002/api/ingestion/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf"
```

### Example Files:
```bash
# Available in project:
/path/to/project/Documents/Data_Retention_and_Archival_Policy.pdf
/path/to/project/Documents/GDPR_Selected_Articles.pdf
/path/to/project/Documents/Information_Security_Access_Control_Policy.pdf
```

### Request Using Available File:
```bash
curl -X POST http://localhost:8002/api/ingestion/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/c/Users/Anagha.e/project/RetailPolicy_Intelligence_Decision_Support_System/RetailPolicyAssistant/Documents/Data_Retention_and_Archival_Policy.pdf"
```

### Expected Response (200 OK):
```json
{
  "filename": "Data_Retention_and_Archival_Policy.pdf",
  "document_name": "Data_Retention_and_Archival_Policy",
  "chunks_created": 12,
  "total_pages": 5,
  "status": "indexed",
  "timestamp": "2026-07-11T09:05:29.846760"
}
```

**What to Verify**:
- ✅ HTTP status 200
- ✅ filename matches uploaded file
- ✅ chunks_created > 0 (split into chunks)
- ✅ total_pages > 0
- ✅ status = "indexed"

---

## ENDPOINT 9: Retrieve Documents with Multi-Agent
**Path**: `/api/ingestion/retrieve`  
**Method**: POST  
**Authentication**: ✅ REQUIRED  
**Purpose**: Direct document retrieval using multi-agent system (fast, for testing)

### Request Headers:
```bash
-H "Content-Type: application/json"
-H "Authorization: Bearer $TOKEN"
```

### Request Body Schema:
```json
{
  "query": "string (required, 1-1000 chars)",
  "k": "integer (optional, default=6, range 1-20)"
}
```

### Request Examples:

#### TEST 9.1: Basic Retrieval
```bash
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "data retention policy",
    "k": 6
  }'
```

**Expected Response (200 OK)**:
```json
{
  "query": "data retention policy",
  
  "chunks": [
    {
      "content": "1. Retention Requirements\n   - Customer records retention: 7 years post-transaction\n   - Email data retention: 3 years for business purposes...",
      "metadata": {
        "id": 1,
        "document_name": "Data_Retention_and_Archival_Policy.pdf",
        "page_number": 1,
        "section": "Retention Requirements",
        "chunk_number": 0
      }
    },
    {
      "content": "2. Data Classification\n   - Personal data classification standards: PII must be identified...",
      "metadata": {
        "id": 2,
        "document_name": "Data_Retention_and_Archival_Policy.pdf",
        "page_number": 2,
        "section": "Data Classification",
        "chunk_number": 1
      }
    }
  ],
  
  "count": 2,
  "timestamp": "2026-07-11T09:05:29.846760",
  
  "retrieval_method": "multi_agent",
  "retrieval_agents": [
    "semantic_retrieval_agent",
    "keyword_retrieval_agent",
    "ranking_agent"
  ],
  
  "retrieval_pipeline": {
    "semantic_agent": {
      "method": "embedding_similarity",
      "documents_retrieved": 6,
      "latency_ms": 245.3
    },
    "keyword_agent": {
      "method": "keyword_matching",
      "keywords": ["data", "retention", "policy"],
      "documents_retrieved": 6,
      "latency_ms": 189.7
    },
    "ranking_agent": {
      "method": "multi_agent_fusion",
      "semantic_weight": 0.6,
      "keyword_weight": 0.4,
      "documents_fused": 10,
      "final_documents": 2,
      "consensus_boost_applied": true,
      "total_agents": 3,
      "latency_ms": 120.5
    }
  }
}
```

**What to Verify**:
- ✅ HTTP status 200
- ✅ chunks array populated with documents
- ✅ count = actual number of chunks returned
- ✅ Each chunk has content and metadata
- ✅ retrieval_method = "multi_agent"
- ✅ retrieval_agents array has 3 agents
- ✅ retrieval_pipeline shows semantic_agent, keyword_agent, ranking_agent

---

#### TEST 9.2: Retrieve with Different k Value
```bash
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "access control",
    "k": 3
  }'
```

**Expected Response**: Same format but with count <= 3

**What to Verify**:
- ✅ count <= k (requested limit)

---

#### TEST 9.3: Query with No Matching Documents
```bash
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "xyz abc 123 nonsense",
    "k": 5
  }'
```

**Expected Response**:
```json
{
  "query": "xyz abc 123 nonsense",
  "chunks": [],
  "count": 0,
  "timestamp": "2026-07-11T09:05:29.846760",
  "retrieval_method": "multi_agent",
  "retrieval_agents": [...],
  "retrieval_pipeline": {...}
}
```

**What to Verify**:
- ✅ count = 0
- ✅ chunks is empty array
- ✅ retrieval_pipeline still shows execution details

---

#### TEST 9.4: Invalid k Value (Too High)
```bash
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "retention policy",
    "k": 25
  }'
```

**Expected Response (422 Unprocessable Entity)**:
```json
{
  "detail": [
    {
      "loc": ["body", "k"],
      "msg": "ensure this value is less than or equal to 20",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 20}
    }
  ]
}
```

**What to Verify**:
- ✅ HTTP status 422
- ✅ Error about k limit (max 20)

---

# SECTION 3: TESTING WORKFLOW

## Complete Testing Flow (Step by Step)

### Step 1: Verify System Health
```bash
curl http://localhost:8002/health
# Expected: status="healthy", agents="active", db="connected"
```

### Step 2: Get Authentication Token
```bash
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')
echo $TOKEN
```

### Step 3: Check Dashboard
```bash
curl http://localhost:8002/api/dashboard | jq .
```

### Step 4: Check Observability
```bash
curl http://localhost:8002/api/observability | jq '.multi_agent_summary'
```

### Step 5: View Multi-Agent Demo
```bash
curl http://localhost:8002/api/observability/demo-agents | jq .
```

### Step 6: Ingest a Document
```bash
curl -X POST http://localhost:8002/api/ingestion/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/c/Users/Anagha.e/project/RetailPolicy_Intelligence_Decision_Support_System/RetailPolicyAssistant/Documents/Data_Retention_and_Archival_Policy.pdf" \
  | jq .
```

### Step 7: Test Direct Retrieval
```bash
curl -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "data retention", "k": 3}' \
  | jq .retrieval_pipeline
```

### Step 8: Ask a Policy Question
```bash
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "What is the data retention policy?"}' \
  | jq '.result, .retrieval_method, .retrieval_agents'
```

### Step 9: Ask SQL Question
```bash
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "How many vendors are approved?"}' \
  | jq '.route, .retrieval_method'
```

### Step 10: Get Conversation History
```bash
CONV_ID=$(curl -s -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "test"}' | jq -r '.conversation_id')

curl http://localhost:8002/conversations/$CONV_ID/history \
  -H "Authorization: Bearer $TOKEN" \
  | jq .messages
```

---

# SECTION 4: EXPECTED HTTP STATUS CODES

| Endpoint | Success | Authentication Error | Validation Error | Not Found |
|----------|---------|---------------------|------------------|-----------|
| /health | 200 | N/A | N/A | N/A |
| /token | 200 | N/A | N/A | N/A |
| /ask | 200, 202 | 401 | 400, 422 | N/A |
| /conversations/{id}/history | 200 | 401 | N/A | 404 |
| /api/ingestion/ingest | 200 | 401 | 400, 422 | N/A |
| /api/ingestion/retrieve | 200 | 401 | 400, 422 | N/A |
| /api/dashboard | 200 | N/A | N/A | N/A |
| /api/observability | 200 | N/A | N/A | N/A |
| /api/observability/demo-agents | 200 | N/A | N/A | N/A |

---

# SECTION 5: MULTI-AGENT RETRIEVAL VERIFICATION

## How to Verify Multi-Agent is Working

### 1. Check in /ask Response
```bash
curl -s -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "data retention"}' | jq '{
    retrieval_method: .retrieval_method,
    retrieval_agents: .retrieval_agents,
    total_agents: .retrieval_pipeline.total_agents,
    semantic_latency: .retrieval_pipeline.semantic_agent.latency_ms,
    keyword_latency: .retrieval_pipeline.keyword_agent.latency_ms,
    ranking_latency: .retrieval_pipeline.ranking_agent.latency_ms
  }'
```

**Expected Output**:
```json
{
  "retrieval_method": "multi_agent",
  "retrieval_agents": [
    "semantic_retrieval_agent",
    "keyword_retrieval_agent",
    "ranking_agent"
  ],
  "total_agents": 3,
  "semantic_latency": 245.3,
  "keyword_latency": 189.7,
  "ranking_latency": 120.5
}
```

### 2. Check in /api/ingestion/retrieve Response
```bash
curl -s -X POST http://localhost:8002/api/ingestion/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "access control", "k": 3}' | jq '{
    retrieval_method: .retrieval_method,
    retrieval_agents: .retrieval_agents,
    semantic_agent: .retrieval_pipeline.semantic_agent,
    keyword_agent: .retrieval_pipeline.keyword_agent,
    ranking_agent: .retrieval_pipeline.ranking_agent
  }'
```

---

# SECTION 6: TROUBLESHOOTING

## Issue: Token Expired or Invalid
```bash
# Solution: Get new token
TOKEN=$(curl -s http://localhost:8002/token | jq -r '.access_token')
```

## Issue: No Documents Retrieved
```bash
# Verify documents are ingested:
curl http://localhost:8002/api/observability | jq '.multi_agent_summary'

# If multi_agent_summary shows 0 total_retrievals:
# 1. Upload documents via /api/ingestion/ingest
# 2. Wait for indexing to complete
# 3. Try retrieval again
```

## Issue: 422 Latency SLO Error
```bash
# First query is slow (loading models) - this is normal
# Try again: models are cached, response should be faster

# Or check if query is too complex - try simpler query
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "retention"}'
```

## Issue: 429 Rate Limited
```bash
# Wait a minute and try again
# Check rate limit headers in response:
curl -i -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "test"}'
# Look for: X-RateLimit-Remaining header
```

---

# SECTION 7: COMPLETE TEST CHECKLIST

- [ ] /health returns healthy
- [ ] /token returns valid access_token
- [ ] /ask with valid query returns 200/202
- [ ] /ask response contains retrieval_method, retrieval_agents, retrieval_pipeline
- [ ] /ask response shows multi-agent with 3 agents
- [ ] /conversations/{id}/history returns messages
- [ ] /api/ingestion/ingest uploads and indexes PDF
- [ ] /api/ingestion/retrieve returns documents
- [ ] /api/ingestion/retrieve shows multi-agent pipeline
- [ ] /api/dashboard returns metrics
- [ ] /api/observability returns SLO metrics
- [ ] /api/observability/demo-agents returns agent descriptions
- [ ] Multi-agent fusion working (semantic + keyword + ranking)
- [ ] Retrieval pipeline latencies showing correctly
- [ ] Consensus boost being applied
- [ ] All authentication required on /ask endpoint
- [ ] All invalid queries returning 400/422 errors

---

**Complete Testing Project Verified ✅**

