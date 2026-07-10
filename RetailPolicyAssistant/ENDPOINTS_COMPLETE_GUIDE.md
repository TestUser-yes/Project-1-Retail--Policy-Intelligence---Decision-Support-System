# Complete API Endpoints Guide - All Three Routes Explained

**Status**: All 3 endpoints are implemented and registered ✓  
**Date**: July 10, 2026

---

## 📌 Quick Overview - Three Endpoints

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| **POST /ask** | POST | Query policy questions with full analysis | Text query | Answer + Risk + Route + SLO |
| **POST /api/ingestion/ingest** | POST | Upload & index PDF documents | PDF file | Ingestion status + chunks |
| **POST /api/ingestion/retrieve** | POST | Vector search for relevant chunks | Text query | Top-k chunks with metadata |

---

## 🔄 Three-Phase RAG Flow

```
Phase 0: Document Ingestion (Manual - /ingest endpoint)
    PDF Upload → Split → Embed → Store in pgvector
    
Phase 1: Data Retrieval (Automatic - used by /ask internally)
    Query → Embed → Vector Search → Get chunks
    
Phase 2: Answer Generation (Full Processing - /ask endpoint)
    Query → Retrieve Chunks → Route (RAG/SQL/Hybrid) → Risk Assessment → Return Answer
```

---

## Endpoint 1: POST /ask - Full Query Processing

### 📝 Purpose
Process a policy question with **complete analysis**:
- Intent detection
- Multi-agent routing (RAG/SQL/Hybrid)
- Risk assessment
- Escalation detection
- SLO enforcement
- Confidence scoring

### 🎯 Use Case
User asks a policy question and wants complete intelligence:
- What is the answer?
- How confident are we?
- Is it high risk?
- Should this be escalated?
- How long did it take?

### 📥 Request (Swagger)

**Endpoint**: `POST http://localhost:8000/ask`

**Headers**:
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "query": "What is our retention policy for customer data?",
  "conversation_id": "conv_123456"
}
```

**Fields**:
- `query` (required, string): The policy question (3-10,000 chars)
- `conversation_id` (optional, string): For conversation tracking

### 📤 Response (Example)

```json
{
  "query": "What is our retention policy for customer data?",
  "conversation_id": "conv_123456",
  "intent": {
    "intent": "rag",
    "reason": "Query asks about policy details - RAG best suited"
  },
  "route": "rag",
  "result": {
    "result": "Customer data retention policy requires keeping all personal information for 7 years after account closure, as per compliance regulations..."
  },
  "risk": {
    "risk_level": "low",
    "reason": "Standard policy question with no sensitive escalation triggers"
  },
  "escalate": false,
  "escalation_reason": "",
  "latency_seconds": 1.850,
  "cost_usd": 0.0,
  "budget_remaining_usd": 100.0,
  "budget_percent_used": 0.0,
  "slo_metrics": {
    "latency_ms": 1850.0,
    "target_latency_ms": 2000.0,
    "slo_status": "pass",
    "slo_breached": false,
    "enforcement_action": "none",
    "enforcement_reason": "SLO OK"
  },
  "validation_passed": true,
  "confidence_score": 0.92,
  "sources": [
    "policy_documents/retention_policy_2024.pdf"
  ],
  "sql_validation": "Valid SQL generated",
  "recommendation": "Review with compliance officer before implementation"
}
```

**HTTP Status Codes**:
- `200 OK` - Query successful, SLO met
- `202 ACCEPTED` - Query successful but SLO warning (needs review)
- `400 BAD_REQUEST` - Query validation failed (too short/long, PII detected)
- `403 FORBIDDEN` - Permission denied
- `422 UNPROCESSABLE_ENTITY` - Confidence too low (requires escalation)
- `429 TOO_MANY_REQUESTS` - Rate limit exceeded
- `503 SERVICE_UNAVAILABLE` - Latency SLO exceeded (timeout)
- `500 INTERNAL_SERVER_ERROR` - Processing error

---

## Endpoint 2: POST /api/ingestion/ingest - Upload & Index

### 📝 Purpose
Upload PDF documents and index them for **later retrieval**:
- Load PDF from upload
- Split into chunks (1000 chars, 200 overlap)
- Generate embeddings
- Store in PostgreSQL with pgvector

### 🎯 Use Case
Admin wants to add new policy documents to the system:
- Upload company policies
- Upload compliance documents
- Upload standard procedures

### 📥 Request (Swagger)

**Endpoint**: `POST http://localhost:8000/api/ingestion/ingest`

**Headers**:
```
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data
```

**Body** (Form Data):
```
file: [SELECT PDF FILE FROM YOUR COMPUTER]
```

**In Swagger UI**:
1. Click "Choose File" button
2. Select your PDF (e.g., `retention_policy.pdf`)
3. Click "Execute"

### 📤 Response (Example)

```json
{
  "filename": "retention_policy.pdf",
  "document_name": "retention_policy_2024",
  "chunks_created": 45,
  "total_pages": 12,
  "status": "indexed",
  "timestamp": "2024-07-10T14:32:18.123456Z"
}
```

**Fields Explained**:
- `filename`: Original uploaded filename
- `document_name`: Name stored in database
- `chunks_created`: How many text chunks were created (45 chunks)
- `total_pages`: Pages in the PDF (12 pages)
- `status`: Always "indexed" on success
- `timestamp`: When the upload was processed

**HTTP Status Codes**:
- `200 OK` - Document indexed successfully
- `400 BAD_REQUEST` - File not PDF or file empty
- `403 FORBIDDEN` - Permission denied
- `500 INTERNAL_SERVER_ERROR` - Indexing failed

### ⚠️ Important Notes
- Only PDF files supported
- File must not be empty
- Documents are stored in `Documents/` folder
- Chunks are created with 1000 char size, 200 char overlap
- Embeddings generated automatically using offline method

---

## Endpoint 3: POST /api/ingestion/retrieve - Vector Search

### 📝 Purpose
Search for **relevant document chunks** using vector similarity:
- Embed query
- Find similar chunks in database
- Return top-k most relevant chunks
- Include metadata (source, page, section)

### 🎯 Use Case
User wants to find specific chunks from uploaded documents:
- Find retention policy details
- Find escalation procedures
- Find vendor requirements
- OR used internally by /ask endpoint during RAG routing

### 📥 Request (Swagger)

**Endpoint**: `POST http://localhost:8000/api/ingestion/retrieve`

**Headers**:
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "query": "customer data retention",
  "k": 3
}
```

**Fields**:
- `query` (required, string): Search query (1-1000 chars)
- `k` (optional, int): Top-k chunks to return (1-20, default 6)

### 📤 Response (Example)

```json
{
  "query": "customer data retention",
  "chunks": [
    {
      "content": "Section 3.2: Data Retention Policy\n\nCustomer personal data must be retained for a minimum of 7 years following account closure or last transaction, in compliance with GDPR Article 5 and data protection regulations...",
      "metadata": {
        "id": 42,
        "document_name": "retention_policy_2024",
        "page_number": 5,
        "section": "3.2 Data Retention Policy",
        "chunk_number": 3
      }
    },
    {
      "content": "Annual retention audits must be conducted by the compliance team to ensure all customer data is retained according to policy. Data exceeding retention periods must be securely deleted within 30 days of retention expiration...",
      "metadata": {
        "id": 43,
        "document_name": "retention_policy_2024",
        "page_number": 6,
        "section": "3.3 Audit Requirements",
        "chunk_number": 4
      }
    },
    {
      "content": "Customer communication records including emails, chat logs, and support tickets must be retained for 5 years minimum. Marketing communication records must be retained for 3 years...",
      "metadata": {
        "id": 44,
        "document_name": "retention_policy_2024",
        "page_number": 7,
        "section": "3.4 Communication Records",
        "chunk_number": 5
      }
    }
  ],
  "count": 3,
  "timestamp": "2024-07-10T14:35:42.987654Z"
}
```

**Fields Explained**:
- `query`: Your search query
- `chunks`: Array of relevant chunks
  - `content`: The actual text from the document
  - `metadata.id`: Database ID of the chunk
  - `metadata.document_name`: Which document this came from
  - `metadata.page_number`: Which page in the PDF
  - `metadata.section`: Section heading (if available)
  - `metadata.chunk_number`: Which chunk this is within the document
- `count`: Number of chunks returned
- `timestamp`: When search was performed

**HTTP Status Codes**:
- `200 OK` - Search successful (may return 0 chunks)
- `400 BAD_REQUEST` - Query empty or too long
- `403 FORBIDDEN` - Permission denied
- `500 INTERNAL_SERVER_ERROR` - Search failed

---

## 🔍 Key Differences Between Three Endpoints

### /ask Endpoint
**What it does**: Complete policy analysis and answering
```
Query → Intent Detection → Multi-Agent Routing → Risk Assessment → 
Answer Generation → Escalation Check → SLO Enforcement → Response
```
**Input**: Text question
**Output**: Full answer with metadata (confidence, risk, route, SLO)
**Processing**: ~2000ms target (2400ms hard limit)
**When to use**: When you need a complete answer with all analysis

---

### /ingest Endpoint
**What it does**: Document upload and indexing
```
PDF Upload → Save → Extract Text → Split into Chunks → 
Generate Embeddings → Store in pgvector
```
**Input**: PDF file
**Output**: Ingestion status and chunk count
**Processing**: One-time, no query needed
**When to use**: When adding new documents to the system (admin task)

---

### /retrieve Endpoint
**What it does**: Vector similarity search
```
Query → Generate Embedding → Vector Similarity Search → 
Top-k Chunks → Return with Metadata
```
**Input**: Text query + k (optional)
**Output**: List of relevant chunks with source/page info
**Processing**: ~200-500ms
**When to use**: When you want raw chunks without full analysis, or to understand what /ask found

---

## 🧪 Complete Swagger Testing Guide

### Setup
1. Start server:
```bash
uvicorn app.main:app --reload --port 8000
```

2. Open Swagger UI:
```
http://localhost:8000/docs
```

3. Get token:
```bash
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')
echo $TOKEN
```

### Test 1: Upload Document (POST /ingest)

**In Swagger**:
1. Click "POST /api/ingestion/ingest"
2. Click "Authorize" button
3. Paste your token
4. Click "Try it out"
5. Click "Choose File" and select a PDF
6. Click "Execute"

**Expected Response**:
```json
{
  "filename": "your_file.pdf",
  "document_name": "your_file",
  "chunks_created": 42,
  "total_pages": 10,
  "status": "indexed",
  "timestamp": "2024-07-10T14:32:18.123456Z"
}
```

**Status**: 200 OK ✓

---

### Test 2: Search Documents (POST /retrieve)

**In Swagger**:
1. Click "POST /api/ingestion/retrieve"
2. Click "Authorize" button (already done)
3. Click "Try it out"
4. Enter JSON:
```json
{
  "query": "retention policy",
  "k": 3
}
```
5. Click "Execute"

**Expected Response**:
```json
{
  "query": "retention policy",
  "chunks": [
    {
      "content": "Section 1: Retention policy states...",
      "metadata": {
        "id": 1,
        "document_name": "retention_policy_2024",
        "page_number": 2,
        "section": "1.0 Overview",
        "chunk_number": 0
      }
    },
    ...
  ],
  "count": 3,
  "timestamp": "2024-07-10T14:35:42.987654Z"
}
```

**Status**: 200 OK ✓

---

### Test 3: Ask Policy Question (POST /ask)

**In Swagger**:
1. Click "POST /ask"
2. Click "Authorize" button (already done)
3. Click "Try it out"
4. Enter JSON:
```json
{
  "query": "What is the retention policy for customer data?",
  "conversation_id": ""
}
```
5. Click "Execute"

**Expected Response**:
```json
{
  "query": "What is the retention policy for customer data?",
  "conversation_id": "conv_abc123",
  "intent": {
    "intent": "rag",
    "reason": "Policy question - RAG best suited"
  },
  "route": "rag",
  "result": {
    "result": "Based on the retention policy documents, customer data must be retained for 7 years after account closure..."
  },
  "risk": {
    "risk_level": "low",
    "reason": "Standard policy question"
  },
  "escalate": false,
  "escalation_reason": "",
  "latency_seconds": 1.823,
  "cost_usd": 0.0,
  "budget_remaining_usd": 100.0,
  "budget_percent_used": 0.0,
  "slo_metrics": {
    "latency_ms": 1823.0,
    "target_latency_ms": 2000.0,
    "slo_status": "pass",
    "slo_breached": false,
    "enforcement_action": "none",
    "enforcement_reason": "SLO OK"
  },
  "validation_passed": true,
  "confidence_score": 0.91,
  "sources": [
    "policy_documents/retention_policy_2024.pdf",
    "policy_documents/data_governance.pdf"
  ],
  "sql_validation": "Valid SQL generated",
  "recommendation": "Review with compliance officer before implementation"
}
```

**Status**: 200 OK ✓

---

## 📊 Workflow Example - Real Usage

### Scenario: New employee onboarding

**Step 1: Admin uploads policies**
```bash
# POST /api/ingestion/ingest
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@company_policies.pdf" \
  http://localhost:8000/api/ingestion/ingest

# Response: 42 chunks indexed ✓
```

**Step 2: Employee searches for specific policy**
```bash
# POST /api/ingestion/retrieve
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "vacation days policy", "k": 3}' \
  http://localhost:8000/api/ingestion/retrieve

# Response: Top 3 relevant chunks about vacation policy
```

**Step 3: Employee asks comprehensive question**
```bash
# POST /ask
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vacation days can I take in my first year?"}' \
  http://localhost:8000/ask

# Response: Complete analysis with answer, confidence, sources, and risk assessment
```

---

## 🎯 When to Use Each Endpoint

### Use /ask When:
✓ User wants a policy answer with full analysis  
✓ You need confidence scores and risk assessment  
✓ You need automatic escalation for sensitive queries  
✓ You want SLO-bounded response with latency enforcement  
✓ You need conversation memory and tracking  

### Use /retrieve When:
✓ You want raw document chunks for inspection  
✓ You need to understand what documents matched a query  
✓ You want to programmatically get source documents  
✓ You're debugging why a certain answer was provided  

### Use /ingest When:
✓ Adding new policy documents to the system  
✓ Admin/operator task to populate the knowledge base  
✓ Bulk uploading multiple PDFs  
✓ One-time operation (not per-query)  

---

## 📋 Response Field Glossary (/ask Response)

| Field | Purpose | Example |
|-------|---------|---------|
| `query` | Original user query | "What is retention policy?" |
| `conversation_id` | Tracks multi-turn conversation | "conv_abc123" |
| `intent.intent` | Detected intent | "rag", "sql", or "hybrid" |
| `intent.reason` | Why that intent was chosen | "Query asks for policy details" |
| `route` | Which agent processed query | "rag", "sql", or "hybrid" |
| `result.result` | The actual answer | "Retention policy requires..." |
| `risk.risk_level` | Risk classification | "low", "medium", or "high" |
| `risk.reason` | Why that risk level | "Standard policy question" |
| `escalate` | Whether human review needed | true or false |
| `escalation_reason` | Why escalation triggered | "High-risk data transfer" |
| `latency_seconds` | Total query time | 1.823 |
| `cost_usd` | API cost (disabled) | 0.0 |
| `slo_metrics.latency_ms` | Latency in milliseconds | 1823.0 |
| `slo_metrics.slo_status` | "pass", "warning", or "fail" | "pass" |
| `slo_metrics.slo_breached` | Was SLO boundary violated | false |
| `slo_metrics.enforcement_action` | SLO enforcement taken | "none", "warning", "escalate", "reject" |
| `confidence_score` | Model confidence (0-1) | 0.91 |
| `sources` | Which documents were used | ["retention_policy.pdf"] |
| `sql_validation` | SQL validation status | "Valid SQL generated" |
| `recommendation` | Action recommendation | "Review with compliance officer" |

---

## ⚠️ Common Issues & Solutions

### Issue: "Only PDF files are supported"
**Cause**: Trying to upload non-PDF file  
**Solution**: Use .pdf files only, not .doc, .txt, etc.

### Issue: "Permission denied" (403)
**Cause**: No valid authentication token  
**Solution**: Get token from `/token` endpoint, include in Authorization header

### Issue: "Rate limit exceeded" (429)
**Cause**: Too many requests in short time  
**Solution**: Wait before making new requests, limit is 50 /ask per hour

### Issue: "Low confidence" (422)
**Cause**: Answer confidence < 0.70  
**Solution**: Query will be escalated; check dashboard for status

### Issue: "SLO exceeded" (503)
**Cause**: Query took > 2400ms  
**Solution**: Try again, system may be under load

---

## 🚀 API Endpoints Summary

All 8 endpoints available:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| GET /health | GET | System health check |
| GET /token | GET | Get demo token |
| POST /ask | POST | **Full policy Q&A with analysis** |
| GET /conversations/{id}/history | GET | Get conversation history |
| POST /api/ingestion/ingest | POST | **Upload & index PDF** |
| POST /api/ingestion/retrieve | POST | **Vector search documents** |
| GET /api/dashboard | GET | Dashboard metrics |
| GET /api/observability | GET | Observability traces |

---

## 📖 Documentation

- See `SLO_BOUNDED_IMPLEMENTATION.md` for SLO enforcement details
- See `app/routers/ingestion.py` for implementation
- See `app/api.py` for /ask endpoint implementation
- Try `http://localhost:8000/docs` for interactive Swagger UI
- Try `http://localhost:8000/redoc` for ReDoc documentation

