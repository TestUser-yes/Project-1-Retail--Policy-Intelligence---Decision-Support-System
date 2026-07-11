# Retail Policy Intelligence System - Complete API Contract

**Version:** 4.0 (Full Feature Implementation)  
**Last Updated:** 2026-07-12  
**Base URL:** `http://localhost:8001` (development) or deployed instance  
**Authentication:** JWT Bearer tokens or secure httpOnly cookies

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Complete Endpoint Reference](#complete-endpoint-reference)
4. [Request/Response Models](#requestresponse-models)
5. [Database Schema](#database-schema)
6. [Error Handling](#error-handling)
7. [Business Logic & Workflows](#business-logic--workflows)
8. [Multi-Agent Architecture](#multi-agent-architecture)
9. [Rate Limiting & Cost Tracking](#rate-limiting--cost-tracking)
10. [Observability & Tracing](#observability--tracing)

---

## API Overview

### System Purpose
Intelligent policy compliance system with multi-agent routing, cost tracking, memory management, role-based access control (RBAC), security guardrails, caching, and rate limiting.

### Key Features
- **Multi-Agent Routing:** RAG (PDF documents), SQL (database), or Hybrid (both)
- **Real-Time Streaming:** WebSocket support for agent execution updates
- **Cost Tracking:** Per-query cost tracking with budget management
- **Conversation Memory:** Persistent conversation history with context
- **SLO Enforcement:** Latency, confidence, and accuracy monitoring
- **Security Guardrails:** 8-layer security validation system
- **Observability:** Langfuse tracing integration for all agent executions
- **Role-Based Access Control:** Three roles (user, compliance_officer, admin)
- **Document Management:** PDF ingestion and vector search with pgvector

### Technology Stack
- **Framework:** FastAPI 0.139.0
- **Database:** PostgreSQL (Neon Cloud) with pgvector extension
- **Authentication:** JWT (HS256 algorithm)
- **Async/Concurrency:** Uvicorn with async support
- **LLM Integration:** Ollama (phi3:mini) + OpenAI support
- **Observability:** Langfuse 4.13.0
- **Vector Search:** pgvector for semantic similarity
- **Real-Time:** WebSocket connections for streaming

---

## Authentication & Authorization

### Authentication Mechanism

#### Token Types
1. **Access Token**
   - JWT with HS256 algorithm
   - Expiration: 30 minutes (default)
   - Payload: `user_id`, `username`, `email`, `role`, `exp`, `type: "access"`
   - Storage: Secure httpOnly cookies (browser) or Authorization header (API clients)

2. **Refresh Token**
   - JWT with HS256 algorithm
   - Expiration: 7 days (default)
   - Payload: `user_id`, `username`, `email`, `role`, `exp`, `type: "refresh"`
   - Storage: Secure httpOnly cookies
   - Features: Token revocation support via in-memory store

#### Authentication Flow

```
1. Client calls POST /token
   ↓
2. Server generates access_token + refresh_token (demo tokens)
   ↓
3. Server sets secure httpOnly cookies (access_token, refresh_token)
   ↓
4. Client includes token in subsequent requests via:
   - Authorization: Bearer <access_token> header, OR
   - Secure cookies (automatic in browser)
   ↓
5. Server verifies token in get_current_user dependency
```

#### Token Verification

```python
# Supports both Bearer auth and secure cookies (priority order):
1. Authorization: Bearer <token> header (for API clients)
2. access_token cookie (for browser/frontend)
```

### Authorization System (RBAC)

#### Roles & Permissions

```yaml
user:
  description: "Standard user"
  permissions:
    - ask:policy          # Ask policy questions
    - ask:vendor          # Ask vendor questions
    - ask:hybrid          # Ask hybrid questions
    - view:query_history  # View own query history

compliance_officer:
  description: "Compliance specialist with elevated permissions"
  permissions:
    - ask:policy
    - ask:vendor
    - ask:hybrid
    - view:query_history
    - view:costs          # View cost tracking
    - view:audit_log      # View audit log

admin:
  description: "System administrator with full access"
  permissions:
    - ask:policy
    - ask:vendor
    - ask:hybrid
    - view:query_history
    - view:costs
    - view:audit_log
    - admin:users         # Manage users
    - admin:roles         # Manage roles
    - admin:metrics       # View system metrics
```

#### Permission Checking

Endpoints use `require_permission()` dependency or inline `PermissionValidator.assert_permission()` checks.

```python
# In endpoint:
PermissionValidator.assert_permission(current_user, Permission.ASK_POLICY_QUESTION)
# Raises HTTPException 403 if permission denied
```

#### Demo Credentials

```yaml
Default User:
  user_id: "demo-user"
  username: "demo"
  email: "demo@retailpolicy.local"
  role: "user"

Admin User:
  user_id: "demo-admin"
  username: "admin"
  email: "admin@retailpolicy.local"
  role: "admin"
```

---

## Complete Endpoint Reference

### Authentication Endpoints

#### 1. Get Token
```
POST /token
```

**Purpose:** Get demo access and refresh tokens stored in secure httpOnly cookies

**Authentication:** None (public)

**Request:** (empty body)

**Response:** 200 OK
```json
{
  "token_type": "bearer",
  "expires_in": 1800,
  "message": "Tokens set in secure httpOnly cookies"
}
```

**Cookies Set:**
- `access_token`: JWT access token (httpOnly, Secure)
- `refresh_token`: JWT refresh token (httpOnly, Secure)

---

#### 2. Auth Status
```
GET /auth/status
```

**Purpose:** Check authentication status and verify cookies are set correctly

**Authentication:** Optional (checks for token)

**Request:** (no body)

**Response:** 200 OK (authenticated)
```json
{
  "authenticated": true,
  "user_id": "demo-user",
  "username": "demo",
  "email": "demo@retailpolicy.local",
  "role": "user",
  "message": "Authentication successful"
}
```

**Response:** 200 OK (unauthenticated)
```json
{
  "authenticated": false,
  "message": "No authentication token found in headers or cookies"
}
```

---

#### 3. Refresh Token
```
POST /token/refresh
```

**Purpose:** Get a new access token using refresh token from secure cookie

**Authentication:** Refresh token from secure cookie

**Request:** (empty body)

**Response:** 200 OK
```json
{
  "token_type": "bearer",
  "expires_in": 1800,
  "message": "Access token refreshed"
}
```

**Cookies Set:**
- `access_token`: New JWT access token (httpOnly, Secure)

---

#### 4. Logout
```
POST /logout
```

**Purpose:** Clear authentication cookies and revoke tokens

**Authentication:** Required (access token)

**Request:** (empty body)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Logged out successfully - cookies cleared"
}
```

**Cookies Cleared:**
- `access_token`
- `refresh_token`

---

### Main Query Endpoint

#### 5. Ask Policy Question
```
POST /ask
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Purpose:** Ask a policy question and get intelligent routing to RAG, SQL, or Hybrid agents

**Authentication:** Required (access token) - Permission: `ask:policy`

**Request Body:**
```json
{
  "query": "What is the data retention policy?",
  "conversation_id": "conv-123-abc"
}
```

**Request Schema:**
```python
class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=10000)
    conversation_id: str = Field(default="", description="Optional (auto-generated if empty)")
```

**Response:** 200 OK
```json
{
  "query": "What is the data retention policy?",
  "conversation_id": "conv-123-abc",
  "intent": {
    "intent": "rag",
    "reason": "Query classified as rag"
  },
  "route": "rag",
  "result": {
    "result": "According to the Data Retention Policy..."
  },
  "risk": {
    "risk_level": "low",
    "reason": "Routine policy query"
  },
  "escalate": false,
  "escalation_reason": "",
  "latency_seconds": 0.245,
  "cost_usd": 0.0012,
  "budget_remaining_usd": 99.9988,
  "budget_percent_used": 0.0012,
  "slo_metrics": {
    "latency_ms": 245.3,
    "target_latency_ms": 2000.0,
    "slo_status": "pass",
    "slo_breached": false,
    "enforcement_action": "none",
    "enforcement_reason": ""
  },
  "validation_passed": true,
  "confidence_score": 0.92,
  "sources": [
    {
      "document": "policy_documents/data_retention.pdf",
      "page": 3,
      "section": "Retention Periods"
    }
  ],
  "sql_validation": "Valid SQL generated",
  "recommendation": "Review with compliance officer before implementation",
  "agents_used": ["rag_agent"],
  "agent_details": [
    {
      "agent_name": "rag_agent",
      "status": "success",
      "latency_ms": 245.3,
      "confidence": 0.92,
      "data_source": "PDF Documents"
    }
  ],
  "retrieval_method": "multi_agent",
  "retrieval_agents": ["semantic_retrieval_agent", "ranking_agent"],
  "retrieval_pipeline": {
    "semantic_search": {
      "status": "success",
      "results": 15
    },
    "keyword_search": {
      "status": "success",
      "results": 8
    },
    "ranking": {
      "status": "success",
      "top_k": 6
    }
  }
}
```

**Response Schema:**
```python
class AskResponse(BaseModel):
    query: str
    conversation_id: str
    intent: IntentModel
    route: str  # "rag", "sql", "hybrid"
    result: ResultModel
    risk: RiskModel
    escalate: bool
    escalation_reason: str = ""
    latency_seconds: float
    cost_usd: float = 0.0
    budget_remaining_usd: float = 0.0
    budget_percent_used: float = 0.0
    slo_metrics: SLOMetricsModel
    validation_passed: bool = True
    confidence_score: float = 0.0
    sources: list = []
    sql_validation: str = ""
    recommendation: str = ""
    agents_used: list[str] = []
    agent_details: list[AgentExecutionModel] = []
    retrieval_method: str = "semantic"
    retrieval_agents: list[str] = []
    retrieval_pipeline: dict = {}
```

**Error Responses:**
- 400: Query validation failed / Empty file
- 401: Not authenticated / Invalid token
- 403: Permission denied
- 429: Rate limit exceeded
- 500: Query processing failed / Tracer flush error

**Business Logic:**
1. Check permission (`ask:policy`)
2. Validate query (guardrails layer 1-6)
3. Check rate limits (50 /ask per hour per user)
4. Get or create conversation in memory
5. Route query to appropriate agent(s):
   - **RAG Agent:** Policy keyword match → semantic search + ranking
   - **SQL Agent:** Vendor/count keywords → natural language SQL
   - **Hybrid:** Combined policy + vendor keywords → both agents
6. Record SLO metrics (latency, confidence)
7. Track cost (embedding + completion tokens)
8. Apply SLO enforcement if configured
9. Store in database for dashboard
10. Trace scores to Langfuse
11. Return comprehensive response

---

### Conversation Management

#### 6. Get Conversation History
```
GET /conversations/{conversation_id}/history
Authorization: Bearer <access_token>
```

**Purpose:** Retrieve full message history for a conversation

**Authentication:** Required (access token) - Permission: `view:query_history`

**Path Parameters:**
```
conversation_id: str - Unique conversation identifier
```

**Response:** 200 OK
```json
{
  "conversation_id": "conv-123-abc",
  "messages": [
    {
      "role": "user",
      "content": "What is the data retention policy?"
    },
    {
      "role": "assistant",
      "content": "According to the Data Retention Policy, documents should be retained for 7 years..."
    },
    {
      "role": "user",
      "content": "What about compliance with GDPR?"
    },
    {
      "role": "assistant",
      "content": "GDPR compliance requires specific retention periods..."
    }
  ]
}
```

**Access Control:**
- Owner can access own conversations
- Admin can access any conversation
- Returns 403 if access denied

**Error Responses:**
- 401: Not authenticated
- 403: Access denied (not owner or admin)
- 404: Conversation not found

---

### Document Ingestion & Retrieval

#### 7. Ingest Document (Upload PDF)
```
POST /api/ingestion/ingest
Content-Type: multipart/form-data
Authorization: Bearer <access_token>
```

**Purpose:** Upload and index a PDF document for semantic search

**Authentication:** Required (access token) - Permission: `ask:policy`

**Request:**
```
file: UploadFile (PDF file)
```

**Response:** 200 OK
```json
{
  "filename": "policy_documents.pdf",
  "document_name": "policy_documents",
  "chunks_created": 145,
  "total_pages": 23,
  "status": "indexed",
  "timestamp": "2026-07-12T14:32:15.123456"
}
```

**Request Schema:**
```python
class IngestResponse(BaseModel):
    filename: str = Field(..., description="Name of uploaded PDF file")
    document_name: str = Field(..., description="Document name in database")
    chunks_created: int = Field(..., description="Number of chunks created")
    total_pages: int = Field(..., description="Number of pages in PDF")
    status: str = Field(..., description="Ingestion status: indexed, error, etc.")
    timestamp: str = Field(..., description="ISO format timestamp")
```

**Ingestion Pipeline:**
1. Validate file type (PDF only)
2. Check file not empty
3. Save to temporary location
4. Load PDF (page count)
5. Split into chunks (1000 chars, 200 char overlap)
6. Generate embeddings (1536-dim OpenAI or Ollama)
7. Store in PostgreSQL with pgvector
8. Index by document name, page, section, chunk number
9. Return ingestion metadata

**Error Responses:**
- 400: Only PDF files supported / File is empty
- 401: Not authenticated
- 403: Permission denied
- 500: Ingestion failed

---

#### 8. Retrieve Documents
```
POST /api/ingestion/retrieve
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Purpose:** Retrieve relevant document chunks using vector similarity search

**Authentication:** Required (access token) - Permission: `ask:policy`

**Request Body:**
```json
{
  "query": "What is the encryption standard?",
  "k": 6
}
```

**Request Schema:**
```python
class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=6, ge=1, le=20, description="Top-k chunks to retrieve")
```

**Response:** 200 OK
```json
{
  "query": "What is the encryption standard?",
  "chunks": [
    {
      "content": "All data at rest must be encrypted using AES-256...",
      "metadata": {
        "id": 145,
        "document_name": "security_policy.pdf",
        "page_number": 12,
        "section": "Data Encryption",
        "chunk_number": 3
      }
    },
    {
      "content": "Data in transit must use TLS 1.3 or higher...",
      "metadata": {
        "id": 146,
        "document_name": "security_policy.pdf",
        "page_number": 13,
        "section": "Data Encryption",
        "chunk_number": 4
      }
    }
  ],
  "count": 2,
  "timestamp": "2026-07-12T14:35:22.654321",
  "retrieval_method": "multi_agent",
  "retrieval_agents": ["semantic_retrieval_agent", "keyword_retrieval_agent"],
  "retrieval_pipeline": {
    "semantic_search": {"status": "success", "results": 8},
    "keyword_search": {"status": "success", "results": 5},
    "ranking": {"status": "success", "top_k": 2}
  }
}
```

**Request Schema:**
```python
class RetrieveResponse(BaseModel):
    query: str
    chunks: list[ChunkData]
    count: int
    timestamp: str
    retrieval_method: str = "multi_agent"
    retrieval_agents: list[str] = []
    retrieval_pipeline: dict = {}
```

**Retrieval Pipeline:**
1. Embed query (1536 dimensions)
2. Multi-agent retrieval:
   - Semantic Agent: Vector similarity search (pgvector)
   - Keyword Agent: Full-text search fallback
   - Ranking Agent: Re-rank by relevance
3. Return top-k most similar chunks with metadata

**Error Responses:**
- 401: Not authenticated
- 403: Permission denied
- 500: Retrieval failed

---

### Dashboard & Analytics

#### 9. Get Dashboard Data
```
GET /api/dashboard
Authorization: Bearer <access_token>
```

**Purpose:** Get aggregated dashboard metrics and analytics from database

**Authentication:** Required (access token)

**Response:** 200 OK
```json
{
  "totalQueries": 156,
  "avgLatency": 0.24,
  "escalationRate": 8.3,
  "budgetUsed": 0.0,
  "budgetUsdLimit": 100.0,
  "budgetUsdUsed": 0.0,
  "budgetRemaining": 100.0,
  "activeUsers": 5,
  "successRate": 95.0,
  "queryByRoute": {
    "rag": 89,
    "sql": 42,
    "hybrid": 25
  },
  "queryByRisk": {
    "low": 143,
    "medium": 10,
    "high": 3
  },
  "topPolicies": [
    {"name": "Data Retention Policy", "count": 45},
    {"name": "GDPR Compliance", "count": 32},
    {"name": "Incident Response", "count": 28}
  ],
  "topIntents": [
    {"name": "Data Retention Policy", "count": 45},
    {"name": "GDPR Compliance", "count": 32},
    {"name": "Incident Response", "count": 28},
    {"name": "Security Standards", "count": 19},
    {"name": "Vendor Management", "count": 16}
  ],
  "recentQueries": [
    {
      "id": 156,
      "query": "What is the encryption standard?",
      "route": "RAG",
      "risk": "Low",
      "cost": 0.0,
      "latency": 0.245,
      "timestamp": "2026-07-12T14:35:22.123456"
    }
  ],
  "hourlyTrends": [
    {
      "time": "00:00",
      "queries": 3,
      "latency": 0.24
    },
    {
      "time": "01:00",
      "queries": 2,
      "latency": 0.21
    }
  ],
  "vendorStats": {
    "total": 10,
    "high_risk": 2
  },
  "sloMetrics": {
    "success_rate": 95.0,
    "avg_latency_ms": 240.5,
    "target_latency_ms": 2000.0,
    "escalation_count": 13
  }
}
```

**Metrics Aggregation:**
- Total queries from AIQuery table
- Risk distribution (low/medium/high count)
- Route distribution (RAG/SQL/Hybrid count)
- Recent queries (last 10)
- Hourly trends (24-hour window)
- Top intents (most frequently asked topics)
- Vendor statistics
- SLO metrics (success rate, avg latency)

**Error Responses:**
- 401: Not authenticated
- 500: Dashboard query error

---

### Observability & Monitoring

#### 10. Get Observability Metrics
```
GET /api/observability
Authorization: Bearer <access_token>
```

**Purpose:** Get SLO, latency trends, and multi-agent routing analytics

**Authentication:** Required (access token)

**Response:** 200 OK
```json
{
  "timestamp": "2026-07-12T14:40:15.123456",
  "summary": {
    "total_queries": 156,
    "queries_24h": 89,
    "avg_confidence": 0.85,
    "escalation_rate": 8.3,
    "slo_compliance_rate": 95.0
  },
  "risk_distribution": {
    "high": 3,
    "medium": 10,
    "low": 143
  },
  "route_distribution": {
    "rag": 89,
    "sql": 42,
    "hybrid": 25
  },
  "slo_metrics": {
    "success_rate": 95.0,
    "avg_latency_ms": 240.5,
    "target_latency_ms": 2000.0,
    "slo_status": "pass"
  },
  "hourly_trends": [
    {
      "time": "14:00",
      "queries": 12,
      "slo_target_ms": 2000.0,
      "avg_latency_ms": 245.3
    }
  ],
  "recent_queries": [
    {
      "id": 156,
      "query": "What is the encryption standard?",
      "route": "RAG",
      "risk": "Low",
      "latency_ms": 245.3,
      "timestamp": "2026-07-12T14:35:22.123456"
    }
  ],
  "langfuse_traces": [],
  "multi_agent_summary": {
    "rag_agent_calls": 89,
    "sql_agent_calls": 42,
    "hybrid_agent_calls": 25,
    "total_agent_calls": 156,
    "agent_routing_efficiency": {
      "single_agent_percentage": 83.3,
      "hybrid_percentage": 16.7
    }
  }
}
```

**Metrics:**
- 24-hour query statistics
- Risk and route distributions
- SLO compliance tracking
- Hourly query trends
- Multi-agent routing efficiency
- Recent query history

**Error Responses:**
- 401: Not authenticated
- 500: Observability metrics error (returns empty/fallback values)

---

#### 11. Langfuse Status
```
GET /api/observability/langfuse-status
Authorization: Bearer <access_token>
```

**Purpose:** Check Langfuse tracing status and configuration

**Authentication:** Required (access token)

**Response:** 200 OK (enabled)
```json
{
  "langfuse_enabled": true,
  "base_url": "https://cloud.langfuse.com",
  "client_initialized": true,
  "public_key_set": true,
  "secret_key_set": true,
  "status": "ready",
  "message": "Langfuse tracing is active and ready to receive traces"
}
```

**Response:** 200 OK (disabled)
```json
{
  "langfuse_enabled": false,
  "base_url": "N/A",
  "client_initialized": false,
  "public_key_set": false,
  "secret_key_set": false,
  "status": "disabled",
  "message": "Langfuse tracing is disabled - check LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env"
}
```

---

#### 12. Demo Agents Routing
```
GET /api/observability/demo-agents
Authorization: Bearer <access_token>
```

**Purpose:** Show how multi-agent routing works with example queries

**Authentication:** Required (access token)

**Response:** 200 OK
```json
{
  "title": "Multi-Agent Routing Demo",
  "description": "This endpoint demonstrates how the Retail Policy AI uses multiple agents...",
  "agents": [
    {
      "name": "RAG Agent",
      "description": "Retrieves answers from PDF policy documents using semantic search",
      "data_source": "PDF Documents",
      "triggers": [
        "What is the data retention policy?",
        "Tell me about GDPR compliance requirements",
        "Explain the incident response policy"
      ],
      "example_response": {
        "agent_name": "RAG Agent",
        "status": "success",
        "latency_ms": 245.3,
        "confidence": 0.92,
        "data_source": "PDF Documents"
      }
    },
    {
      "name": "SQL Agent",
      "description": "Queries the database using natural language to SQL translation",
      "data_source": "Database",
      "triggers": [
        "How many vendors do we have?",
        "List all vendors with high-risk compliance status",
        "Show vendors that need background verification"
      ],
      "example_response": {
        "agent_name": "SQL Agent",
        "status": "success",
        "latency_ms": 189.7,
        "confidence": 0.85,
        "data_source": "Database"
      }
    },
    {
      "name": "Hybrid Mode",
      "description": "Combines RAG and SQL agents for comprehensive answers",
      "data_source": "PDF Documents + Database",
      "triggers": [
        "Which vendors comply with our encryption policy?",
        "List vendors and their compliance status for GDPR requirements"
      ]
    }
  ],
  "intent_detection": {
    "description": "The orchestrator analyzes query keywords to determine which agent(s) to invoke",
    "keywords": {
      "policy_keywords": ["policy", "requirement", "compliance", "standard", ...],
      "vendor_keywords": ["vendor", "suppliers", "vendors", ...],
      "sql_indicators": ["how many", "count", "list", ...],
      "compliance_keywords": ["gdpr", "compliance", "ccpa", ...]
    },
    "routing_logic": {
      "priority_1": "Strong compliance keywords + vendor → HYBRID",
      "priority_2": "Compliance keywords only → RAG",
      "priority_3": "SQL indicators (no compliance) → SQL",
      ...
    }
  },
  "how_to_test": {
    "step1": "Go to /api/ask endpoint",
    "step2": "Send a query like: 'What is the data retention policy?'",
    "step3": "Response includes 'agents_used' and 'agent_details' fields",
    "step4": "View LangFuse dashboard at https://cloud.langfuse.com"
  }
}
```

---

### WebSocket Real-Time Streaming

#### 13. Query Stream WebSocket
```
WebSocket ws://localhost:8001/ws/query-stream/{token}
```

**Purpose:** Stream agent execution updates in real-time

**Authentication:** Required (access token as URL parameter)

**Connection:**
```javascript
const token = /* access token */;
const ws = new WebSocket(`ws://localhost:8001/ws/query-stream/${token}`);
```

**Client → Server Messages:**

Subscribe to updates:
```json
{
  "type": "subscribe",
  "timestamp": "2026-07-12T14:35:15.123456"
}
```

Ping (keep-alive):
```json
{
  "type": "ping"
}
```

**Server → Client Messages:**

Connection established:
```json
{
  "type": "subscribed",
  "message": "Successfully subscribed to query updates",
  "connection_id": "conn-abc-123"
}
```

Agent start:
```json
{
  "type": "agent_start",
  "agent_name": "rag_agent",
  "query": "What is the data retention policy?",
  "timestamp": "2026-07-12T14:35:15.234567"
}
```

Agent update (reasoning/progress):
```json
{
  "type": "agent_update",
  "agent_name": "rag_agent",
  "status": "retrieving",
  "message": "Searching vector database for relevant chunks",
  "progress": 0.33,
  "timestamp": "2026-07-12T14:35:15.345678"
}
```

Agent complete:
```json
{
  "type": "agent_complete",
  "agent_name": "rag_agent",
  "status": "success",
  "latency_ms": 245.3,
  "confidence": 0.92,
  "timestamp": "2026-07-12T14:35:15.456789"
}
```

Final response:
```json
{
  "type": "final_response",
  "result": {
    "query": "What is the data retention policy?",
    "conversation_id": "conv-123-abc",
    "route": "rag",
    ...
  },
  "timestamp": "2026-07-12T14:35:15.567890"
}
```

Error:
```json
{
  "type": "error",
  "error": "Query processing failed",
  "timestamp": "2026-07-12T14:35:15.678901"
}
```

Pong (keep-alive response):
```json
{
  "type": "pong",
  "timestamp": "2026-07-12T14:35:15.789012"
}
```

**Error Handling:**
- WS_1008_POLICY_VIOLATION: Invalid or expired token
- Automatic disconnect on authentication failure
- JSON parsing errors returned as error messages

---

#### 14. WebSocket Stats
```
GET /ws/stats
```

**Purpose:** Get WebSocket connection statistics

**Response:** 200 OK
```json
{
  "status": "ok",
  "connections": {
    "total_users": 3,
    "total_connections": 5
  }
}
```

---

### Health & System Endpoints

#### 15. Health Check
```
GET /health
```

**Purpose:** Check system health status

**Authentication:** None (public)

**Response:** 200 OK
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "system": "Retail Policy AI",
  "agents": "active",
  "db": "connected",
  "timestamp": "2026-07-12"
}
```

---

## Request/Response Models

### Core Request Models

#### AskRequest
```python
class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=10000)
    conversation_id: str = Field(default="", description="Optional conversation ID")
```

#### RetrieveRequest
```python
class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=6, ge=1, le=20, description="Top-k chunks")
```

#### IngestRequest
```python
class IngestRequest(BaseModel):
    pass  # File upload via multipart/form-data
```

### Core Response Models

#### IntentModel
```python
class IntentModel(BaseModel):
    intent: str              # "rag", "sql", "hybrid"
    reason: str              # Classification reason
```

#### RiskModel
```python
class RiskModel(BaseModel):
    risk_level: str          # "low", "medium", "high"
    reason: str              # Risk assessment reason
```

#### ResultModel
```python
class ResultModel(BaseModel):
    result: str              # Response text
```

#### SLOMetricsModel
```python
class SLOMetricsModel(BaseModel):
    latency_ms: float
    target_latency_ms: float
    slo_status: str                      # "pass", "warning", "fail"
    slo_breached: bool = False
    enforcement_action: str = "none"     # "none", "degrade", "reject"
    enforcement_reason: str = ""
```

#### MessageModel
```python
class MessageModel(BaseModel):
    role: str                # "user", "assistant"
    content: str             # Message text
```

#### ConversationHistoryModel
```python
class ConversationHistoryModel(BaseModel):
    conversation_id: str
    messages: list[MessageModel]
```

#### AgentExecutionModel
```python
class AgentExecutionModel(BaseModel):
    agent_name: str          # "rag_agent", "sql_agent"
    status: str              # "success", "error"
    latency_ms: float
    confidence: float        # 0.0 to 1.0
    data_source: str         # "PDF Documents", "Database"
```

#### AskResponse
```python
class AskResponse(BaseModel):
    query: str
    conversation_id: str
    intent: IntentModel
    route: str                           # "rag", "sql", "hybrid"
    result: ResultModel
    risk: RiskModel
    escalate: bool
    escalation_reason: str = ""
    latency_seconds: float
    cost_usd: float = 0.0
    budget_remaining_usd: float = 0.0
    budget_percent_used: float = 0.0
    slo_metrics: SLOMetricsModel
    validation_passed: bool = True
    confidence_score: float = 0.0
    sources: list = []                   # [{"document": "...", "page": N, ...}]
    sql_validation: str = ""
    recommendation: str = ""
    agents_used: list[str] = []
    agent_details: list[AgentExecutionModel] = []
    retrieval_method: str = "semantic"
    retrieval_agents: list[str] = []
    retrieval_pipeline: dict = {}
```

#### IngestResponse
```python
class IngestResponse(BaseModel):
    filename: str
    document_name: str
    chunks_created: int
    total_pages: int
    status: str                          # "indexed", "error", etc.
    timestamp: str
```

#### ChunkMetadata
```python
class ChunkMetadata(BaseModel):
    id: int                  # Chunk ID in database
    document_name: str       # Source document
    page_number: int         # Page in source doc
    section: str = ""        # Section heading
    chunk_number: int        # Chunk index
```

#### ChunkData
```python
class ChunkData(BaseModel):
    content: str             # Chunk text
    metadata: ChunkMetadata  # Chunk metadata
```

#### RetrieveResponse
```python
class RetrieveResponse(BaseModel):
    query: str
    chunks: list[ChunkData]
    count: int
    timestamp: str
    retrieval_method: str = "multi_agent"
    retrieval_agents: list[str] = []
    retrieval_pipeline: dict = {}
```

---

## Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### ai_queries
```sql
CREATE TABLE ai_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    result TEXT,
    intent VARCHAR(50),
    route VARCHAR(20),               -- "rag", "sql", "hybrid"
    risk_level VARCHAR(20),          -- "low", "medium", "high"
    escalated BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT DEFAULT 0.0,
    latency FLOAT,                   -- milliseconds
    cost_usd FLOAT DEFAULT 0.0,
    slo_breached BOOLEAN DEFAULT FALSE,
    enforcement_action VARCHAR(50) DEFAULT "none",
    enforcement_reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### policy_documents
```sql
CREATE TABLE policy_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_name VARCHAR(255) NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_number INTEGER NOT NULL,
    section VARCHAR(255),
    content TEXT NOT NULL,
    embedding vector(1536),          -- OpenAI embedding
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_embedding ON policy_documents USING ivfflat(embedding vector_cosine_ops);
```

#### query_logs
```sql
CREATE TABLE query_logs (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT FOREIGN KEY references users(id),
    query_text TEXT NOT NULL,
    intent VARCHAR(50),
    risk_level VARCHAR(20),
    response TEXT,
    confidence FLOAT,
    latency_ms FLOAT,
    escalated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT FOREIGN KEY references users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

#### agent_traces
```sql
CREATE TABLE agent_traces (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    query_id BIGINT FOREIGN KEY references query_logs(id),
    agent_name VARCHAR(100) NOT NULL,
    step_number INTEGER,
    status VARCHAR(20),              -- "success", "error"
    input_data JSON,
    output_data JSON,
    duration_ms FLOAT,
    confidence FLOAT,
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### compliance_reviews
```sql
CREATE TABLE compliance_reviews (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    query_id BIGINT FOREIGN KEY references query_logs(id),
    reviewer_id BIGINT FOREIGN KEY references users(id),
    compliance_status VARCHAR(20),   -- "approved", "rejected", "pending"
    notes TEXT,
    reviewed_at TIMESTAMP DEFAULT NOW()
);
```

#### retention_records
```sql
CREATE TABLE retention_records (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    document_type VARCHAR(100) NOT NULL,
    retention_days INTEGER,
    deletion_date TIMESTAMP,
    status VARCHAR(20),              -- "pending", "deleted", "archived"
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### system_config
```sql
CREATE TABLE system_config (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Query validation failed, invalid file |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Permission denied, access denied |
| 404 | Not Found | Resource not found (conversation, etc.) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error, query processing failed |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

### Common Error Scenarios

#### Query Validation Failed (400)
```json
{
  "detail": "Query validation failed: Query too short (minimum 3 characters)"
}
```

#### Not Authenticated (401)
```json
{
  "detail": "Not authenticated",
  "headers": {"WWW-Authenticate": "Bearer"}
}
```

#### Permission Denied (403)
```json
{
  "detail": "Permission denied: ask:policy"
}
```

#### Conversation Not Found (404)
```json
{
  "detail": "Conversation not found"
}
```

#### Rate Limit Exceeded (429)
```json
{
  "detail": "Rate limit exceeded. Limit: 50/hour",
  "rate_limits": {
    "ask_limit": {
      "limit": 50,
      "tokens_remaining": 0
    }
  }
}
```

#### Query Processing Failed (500)
```json
{
  "detail": "Query processing failed: Database connection timeout"
}
```

---

## Business Logic & Workflows

### Query Processing Workflow

```
1. INPUT VALIDATION (Guardrails Layers 1-6)
   ├─ Sanitize input
   ├─ Check for PII/sensitive data
   ├─ Validate length and format
   ├─ Check for SQL injection attempts
   ├─ Verify no malicious keywords
   └─ Scan for encrypted/obfuscated content

2. AUTHENTICATION & AUTHORIZATION
   ├─ Extract token (Bearer header or cookie)
   ├─ Verify token signature and expiration
   ├─ Extract user_id, role from token
   └─ Check permission (Guardrails Layer 7 RBAC)

3. RATE LIMITING
   ├─ Check user rate limit (100 req/hour)
   ├─ Check endpoint rate limit (1000 req/hour global)
   ├─ Check /ask specific limit (50 req/hour per user)
   └─ Reject if exceeded

4. CONVERSATION MANAGEMENT
   ├─ Generate conversation_id if not provided
   ├─ Create or retrieve conversation from memory
   └─ Add user message to history

5. INTENT DETECTION
   ├─ Keyword matching against config:
   │  ├─ policy_keywords (policy, requirement, compliance, ...)
   │  ├─ vendor_keywords (vendor, supplier, partner, ...)
   │  └─ retail_keywords (refund, return, customer, ...)
   ├─ Determine routing intent: "rag", "sql", or hybrid
   └─ Record intent confidence

6. AGENT ROUTING & EXECUTION
   ├─ IF intent == "rag":
   │  ├─ RAG Agent:
   │  │  ├─ Embed query (1536 dimensions)
   │  │  ├─ Vector search in policy_documents table
   │  │  ├─ Multi-agent retrieval (semantic + keyword + ranking)
   │  │  ├─ Generate response from top chunks
   │  │  └─ Return: (result, confidence, sources, agent_detail, retrieval_detail)
   │
   ├─ ELSE IF intent == "sql":
   │  ├─ SQL Agent:
   │  │  ├─ Parse natural language
   │  │  ├─ Generate SQL query
   │  │  ├─ Validate SQL syntax
   │  │  ├─ Execute against database
   │  │  └─ Return: (result, confidence, sources, agent_detail)
   │
   └─ ELSE (hybrid):
       ├─ RAG Agent (as above)
       ├─ SQL Agent (as above)
       ├─ Combine results
       └─ Return: (combined_result, avg_confidence, merged_sources, both_agent_details)

7. RISK ASSESSMENT
   ├─ Analyze result for compliance keywords
   ├─ Check confidence score
   ├─ Apply risk thresholds:
   │  ├─ HIGH: confidence < 0.5 OR contains risk keywords
   │  ├─ MEDIUM: confidence 0.5-0.8 AND contains medium keywords
   │  └─ LOW: confidence > 0.8 AND no risk keywords
   └─ Record risk level

8. ESCALATION DECISION
   ├─ IF risk_level == "high":
   │  ├─ escalate = true
   │  └─ reason = "High confidence required for this policy"
   ├─ ELSE IF is_relevant == false:
   │  ├─ escalate = true
   │  └─ reason = "Query out of scope - human review needed"
   └─ ELSE:
       └─ escalate = false

9. COST TRACKING
   ├─ Count tokens: embedding_tokens + completion_tokens
   ├─ Calculate costs:
   │  ├─ embedding_cost = embedding_tokens * embedding_cost_per_1k / 1000
   │  └─ completion_cost = completion_tokens * completion_cost_per_1k / 1000
   ├─ Update budget tracking
   └─ Record in cost_summary

10. SLO ENFORCEMENT
    ├─ Record latency to SLO tracker
    ├─ IF SLO_ENFORCE_LATENCY && latency > SLO_LATENCY_HARD_LIMIT:
    │  ├─ enforcement_action = "reject"
    │  └─ Return 503 Service Unavailable
    ├─ ELSE IF SLO_ENFORCE_CONFIDENCE && confidence < SLO_CONFIDENCE_MIN:
    │  ├─ enforcement_action = "degrade"
    │  └─ Include degradation notice
    └─ ELSE:
        └─ enforcement_action = "none"

11. OUTPUT SANITIZATION (Guardrails Layers 2, 3, 8)
    ├─ Remove PII from response
    ├─ Mask sensitive data
    ├─ Ensure no data leakage
    └─ Apply role-based output filtering

12. DATABASE RECORDING
    ├─ Save AIQuery record:
    │  ├─ query
    │  ├─ result
    │  ├─ intent, route, risk_level
    │  ├─ escalated, confidence_score
    │  ├─ latency, cost_usd
    │  ├─ slo_breached, enforcement_action
    │  └─ created_at
    └─ Update dashboard metrics

13. OBSERVABILITY TRACING
    ├─ Trace to Langfuse:
    │  ├─ Query details
    │  ├─ Agent execution traces
    │  ├─ Retrieval pipeline steps
    │  ├─ Scores: confidence, risk, latency
    │  └─ User ID, intent, route
    └─ Flush tracer

14. CONVERSATION MEMORY UPDATE
    ├─ Add assistant message to conversation
    ├─ Include metadata:
    │  ├─ intent, route, risk_level
    │  ├─ escalate, cost_usd, latency_seconds
    │  └─ confidence_score
    └─ Persist in memory store

15. RETURN RESPONSE
    ├─ Include all 10 response fields
    ├─ Add multi-agent visibility (agents_used, agent_details)
    ├─ Include retrieval pipeline details
    ├─ Add SLO metrics
    └─ Return HTTP 200 or error status
```

### Intent Detection Logic

```python
def _detect_intent(query: str) -> str:
    query_lower = query.lower()
    
    # Check for strong compliance + vendor combination
    has_compliance = any(kw in query_lower for kw in policy_keywords)
    has_vendor = any(kw in query_lower for kw in vendor_keywords)
    has_count = any(kw in query_lower for kw in ["count", "how many", "number"])
    
    # Routing priority
    if has_compliance and has_vendor and (has_count or "list" in query_lower):
        return "hybrid"  # Both agents needed
    elif has_compliance:
        return "rag"     # Policy documents
    elif has_vendor and has_count:
        return "sql"     # Database queries
    else:
        return "rag"     # Default to policy search
```

### Risk Assessment Logic

```python
def _assess_risk_level(query: str, is_relevant: bool) -> str:
    if not is_relevant:
        return "high"    # Out of scope = high risk
    
    # Check for high-risk keywords
    high_risk_keywords = ["override", "violation", "critical", "gdpr", "breach"]
    if any(kw in query.lower() for kw in high_risk_keywords):
        return "high"
    
    # Check for medium-risk keywords
    medium_risk_keywords = ["approval", "compliance", "audit", "pending"]
    if any(kw in query.lower() for kw in medium_risk_keywords):
        return "medium"
    
    # Default to low risk
    return "low"
```

### Escalation Logic

```python
def _check_escalation_needed(is_relevant: bool, risk_level: str) -> tuple:
    if not is_relevant:
        return True, "Query out-of-scope - requires human review"
    
    if risk_level == "high":
        return True, "High risk query requires compliance officer review"
    
    if risk_level == "medium":
        return True, "Medium risk query needs review"
    
    return False, ""
```

---

## Multi-Agent Architecture

### Agent Types

#### 1. RAG Agent
**Purpose:** Retrieve answers from PDF policy documents

**When Triggered:**
- Intent classification yields "rag"
- Policy keywords detected
- No SQL indicators present

**Process:**
1. Embed query using OpenAI (1536 dims) or Ollama
2. Multi-agent retrieval:
   - **Semantic Retrieval Agent:** Vector similarity search (pgvector)
   - **Keyword Retrieval Agent:** Full-text search fallback
   - **Ranking Agent:** Re-rank by relevance score
3. Combine top-k results (6-12 chunks)
4. Generate response from context
5. Return: result, confidence (0.92 for PDF-backed), sources, metadata

**Confidence Calibration:**
- 0.92 if relevant chunks found
- 0.75 if partial matches
- 0.5 if no direct matches but plausible answer
- 0.0 if error

**Data Sources:**
- policy_documents table with pgvector embeddings
- Chunk metadata: document_name, page_number, section, chunk_number

#### 2. SQL Agent
**Purpose:** Query database using natural language to SQL translation

**When Triggered:**
- Intent classification yields "sql"
- Vendor/count keywords detected
- SQL indicators present ("how many", "list", "count")

**Process:**
1. Parse natural language query
2. Generate SQL query from keywords
3. Validate SQL syntax
4. Execute against database
5. Format results as text
6. Return: result, confidence (0.75-0.85), sources, metadata

**Confidence Calibration:**
- 0.85 if query executed successfully and returned results
- 0.75 if query executed but empty result set
- 0.5 if query required fallback interpretation
- 0.0 if error

**Data Sources:**
- users, vendors, compliance_reviews, query_logs tables
- Real-time database queries

#### 3. Hybrid Agent
**Purpose:** Combine RAG and SQL agents for comprehensive answers

**When Triggered:**
- Intent classification yields "hybrid"
- Both policy keywords AND vendor/count keywords present
- Complex queries requiring both documents and data

**Process:**
1. Run RAG Agent in parallel/sequence
2. Run SQL Agent in parallel/sequence
3. Combine results:
   - Prepend policy context
   - Append data validation
   - Merge sources
4. Return: combined_result, avg_confidence, merged_sources

**Confidence Calibration:**
- Average of RAG and SQL agent confidences
- May be adjusted based on result quality

#### 4. Intent Agent
**Purpose:** Classify query intent (rag, sql, hybrid)

**Keywords:**
```python
policy_keywords = [
    "policy", "procedure", "rule", "guideline", "process",
    "protocol", "standard", "requirement", "compliance",
    "approval", "authorization", "permission", "access",
    ...
]

vendor_keywords = [
    "vendor", "supplier", "partner", "cost", "price",
    "budget", "rate", "fee", "contract", "invoice",
    ...
]

retail_keywords = [
    "refund", "return", "exchange", "customer", "employee",
    "discount", "promotion", "sale", "inventory", "stock",
    ...
]
```

#### 5. Risk Agent
**Purpose:** Assess query risk level (low, medium, high)

**Thresholds:**
```yaml
high_risk_keywords:
  - override, violation, critical, legal hold, gdpr
  - escalation, non-compliant, breach, restriction
  - suspended, rejected, urgent

medium_risk_keywords:
  - approval, compliance, audit, finding, remediation
  - pending, under review, cross-border

low_risk_keywords:
  - routine, standard, general, informational
```

#### 6. Escalation Agent
**Purpose:** Determine if escalation is needed

**Logic:**
```python
escalate = (risk_level == "high") or (not is_relevant) or (risk_level == "medium")
```

#### 7. Confidence Agent
**Purpose:** Calibrate confidence scores

**Calibration:**
- RAG: 0.92 (PDF-backed), 0.75 (partial), 0.5 (fallback)
- SQL: 0.85 (success), 0.75 (empty), 0.5 (fallback)
- Hybrid: Average of component agents

#### 8. Response Agent
**Purpose:** Format final response

**Fields:**
- query, conversation_id, intent, route
- result, risk, escalate, escalation_reason
- latency_seconds, cost_usd, budget metrics
- slo_metrics, confidence_score, sources
- agents_used, agent_details, retrieval details

### Multi-Agent Retrieval (Level 2)

Within each RAG Agent, three sub-agents work together:

1. **Semantic Retrieval Agent**
   - Input: Embedded query
   - Process: Vector similarity search (pgvector cosine distance)
   - Output: Top-15 most similar chunks

2. **Keyword Retrieval Agent**
   - Input: Query keywords
   - Process: Full-text search fallback
   - Output: Top-8 keyword-matched chunks

3. **Ranking Agent**
   - Input: Combined chunks from semantic + keyword
   - Process: Re-rank by relevance, remove duplicates
   - Output: Top-6 final chunks

**Retrieval Pipeline Response:**
```json
{
  "retrieval_method": "multi_agent",
  "retrieval_agents": ["semantic_retrieval_agent", "keyword_retrieval_agent", "ranking_agent"],
  "retrieval_pipeline": {
    "semantic_search": {
      "status": "success",
      "results": 15,
      "top_scores": [0.95, 0.92, 0.89, ...]
    },
    "keyword_search": {
      "status": "success",
      "results": 8,
      "keywords_matched": ["encryption", "standard"]
    },
    "ranking": {
      "status": "success",
      "top_k": 6,
      "final_scores": [0.95, 0.89, 0.87, ...]
    }
  }
}
```

---

## Rate Limiting & Cost Tracking

### Rate Limiting

#### Token Bucket Algorithm
```
capacity = requests_per_hour
refill_rate = capacity / 3600 (per second)
```

#### Limits

| Endpoint | Limit | Burst |
|----------|-------|-------|
| User-wide | 100 req/hour | N/A |
| Endpoint-wide | 1000 req/hour | N/A |
| /ask endpoint | 50 req/hour per user | N/A |

#### Rate Limit Headers
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
```

#### Rate Limit Response (429)
```json
{
  "detail": "Rate limit exceeded. Limit: 50/hour",
  "rate_limits": {
    "ask_limit": {
      "limit": 50,
      "tokens_remaining": 0
    }
  }
}
```

### Cost Tracking

#### Configuration (.env)
```
COST_PROVIDER=ollama  # or openai, anthropic
EMBEDDING_COST_PER_1K=0.0  # (dollars per 1000 tokens)
COMPLETION_COST_PER_1K=0.0  # (dollars per 1000 tokens)
BUDGET_USD=100.0  # Total budget
```

#### Cost Calculation
```python
embedding_tokens = len(query.split()) + len(result.split())
completion_tokens = len(result.split())

embedding_cost = embedding_tokens * EMBEDDING_COST_PER_1K / 1000
completion_cost = completion_tokens * COMPLETION_COST_PER_1K / 1000
total_cost = embedding_cost + completion_cost

budget_used = total_cost
budget_remaining = BUDGET_USD - total_cost
budget_percent_used = (budget_used / BUDGET_USD) * 100
```

#### Cost Response
```json
{
  "cost_usd": 0.0012,
  "budget_remaining_usd": 99.9988,
  "budget_percent_used": 0.0012
}
```

#### Cost Summary
```python
class CostSummary:
    total_queries: int
    total_cost: float
    budget_limit: float
    budget_remaining: float
    budget_usage_percent: float
    average_cost_per_query: float
```

---

## Observability & Tracing

### Langfuse Integration

#### Configuration
```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

#### Traced Functions

All functions with `@trace_function()` decorator:

1. **orchestrator.run()**
   - Span type: chain
   - Traces full query processing
   - Logs all major steps

2. **rag_agent.run()**
   - Span type: span
   - Traces document retrieval
   - Logs embedding and search results

3. **sql_agent.run()**
   - Span type: span
   - Traces SQL generation and execution
   - Logs database queries

4. **retrieve_with_multi_agent()**
   - Span type: span
   - Traces retrieval pipeline
   - Logs semantic, keyword, and ranking steps

#### Score Tracing

```python
ScoreTracer.log_query_execution(
    query=query,
    route=route,
    confidence=confidence_score,
    risk_level=risk_level,
    latency_ms=latency * 1000,
    user_id=user_id,
)
```

#### Middleware Tracing
```python
@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    # Log all requests to Langfuse
    # Measure latency
    # Add X-Latency-MS header
    # Flush tracer async
```

#### Trace Status Endpoint
```json
GET /api/observability/langfuse-status
{
  "langfuse_enabled": true,
  "base_url": "https://cloud.langfuse.com",
  "client_initialized": true,
  "status": "ready"
}
```

### SLO Tracking

#### Configuration
```env
SLO_ENFORCE_LATENCY=false
SLO_ENFORCE_CONFIDENCE=false
SLO_ENFORCE_ACCURACY=false

SLO_LATENCY_TARGET_MS=2000
SLO_LATENCY_HARD_LIMIT_MS=5000
SLO_CONFIDENCE_MIN=0.70
```

#### SLO Metrics
```python
class SLOMetrics:
    latency_ms: float
    target_latency_ms: float = 2000.0
    slo_status: str  # "pass", "warning", "fail"
    confidence: float
    success_rate: float
```

#### SLO Enforcement Actions
```python
enforcement = {
    "allow": True/False,
    "breached": True/False,
    "enforcement_action": "none" | "degrade" | "reject",
    "enforcement_reason": "string",
    "http_status": 200 | 503,
}
```

#### SLO Summary
```json
{
  "total_queries": 156,
  "success_rate": 95.0,
  "average_latency_ms": 240.5,
  "target_latency_ms": 2000.0,
  "escalation_count": 13,
  "slo_status": "pass"
}
```

### Metrics Collection

#### Key Metrics Tracked
- Query latency (milliseconds)
- Confidence scores (0.0-1.0)
- Risk levels (low/medium/high distribution)
- Route distribution (RAG/SQL/Hybrid percentage)
- Escalation rate (%)
- Cost per query (USD)
- Budget usage (%)
- Agent execution times
- Retrieval latency
- Token counts

#### Metrics Endpoints
- `/api/observability` - Full observability dashboard
- `/api/dashboard` - Quick dashboard snapshot
- `/ws/stats` - WebSocket connection stats

---

## Configuration Files

### .env
```env
# Project
PROJECT_NAME=Retail Policy Intelligence & Decision Support System

# Database
DATABASE_URL=postgresql+psycopg://user:pass@host/db

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Langfuse
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com

# OpenAI (optional)
OPENAI_API_KEY=sk-...

# SLO Configuration
SLO_ENFORCE_LATENCY=false
SLO_ENFORCE_CONFIDENCE=false
SLO_ENFORCE_ACCURACY=false
SLO_LATENCY_TARGET_MS=2000
SLO_LATENCY_HARD_LIMIT_MS=5000
SLO_CONFIDENCE_MIN=0.70
```

### Security Configuration

**CORS Settings (main.py):**
```python
# Allow all localhost ports 3000-3099 for Next.js
# Allow Vite dev server (5173)
# enable_credentials=True for secure cookies
```

**CSRF Protection (core/csrf.py):**
```python
# CSRF token generation and validation
```

**JWT Configuration (core/auth.py):**
```python
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

**Cookie Configuration (core/cookies.py):**
```python
# Secure httpOnly cookies for both access and refresh tokens
# HTTPS-only in production
# SameSite=Lax for CSRF protection
```

---

## Frontend Integration Guide

### Quick Start

```javascript
// 1. Get token
const tokenRes = await fetch('/token', { method: 'POST' });
// Cookies automatically set (access_token, refresh_token)

// 2. Ask a question
const askRes = await fetch('/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // Send cookies
  body: JSON.stringify({
    query: "What is the data retention policy?",
    conversation_id: ""  // Auto-generated if empty
  })
});
const response = await askRes.json();
```

### WebSocket Streaming

```javascript
// Get token first
const token = /* from /token endpoint */;

// Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8001/ws/query-stream/${token}`);

ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'subscribe' }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'agent_start') {
    console.log(`Agent ${message.agent_name} started`);
  } else if (message.type === 'agent_update') {
    console.log(`Progress: ${message.progress * 100}%`);
  } else if (message.type === 'agent_complete') {
    console.log(`Agent completed in ${message.latency_ms}ms`);
  } else if (message.type === 'final_response') {
    console.log('Response:', message.result);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### Error Handling

```javascript
async function askQuestion(query) {
  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ query })
    });
    
    if (res.status === 401) {
      // Token expired - refresh
      await fetch('/token/refresh', { method: 'POST' });
      // Retry request
      return askQuestion(query);
    } else if (res.status === 429) {
      // Rate limited
      throw new Error('Too many requests. Please wait.');
    } else if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail);
    }
    
    return await res.json();
  } catch (err) {
    console.error('Query failed:', err.message);
    throw err;
  }
}
```

---

## Summary

This API contract provides a complete specification for building a frontend application for the Retail Policy Intelligence System. Key characteristics:

- **Multi-agent architecture** with automatic routing (RAG/SQL/Hybrid)
- **Real-time streaming** via WebSocket for agent progress
- **Comprehensive observability** with Langfuse tracing
- **Security-first** with JWT auth, RBAC, guardrails, and secure cookies
- **Cost tracking** with budget management
- **SLO enforcement** with latency and confidence monitoring
- **Rich responses** with multi-level visibility into agent execution
- **Conversation memory** for context management
- **Rate limiting** to prevent abuse

All endpoints follow RESTful conventions, return structured JSON responses, and include detailed error information for frontend error handling.
