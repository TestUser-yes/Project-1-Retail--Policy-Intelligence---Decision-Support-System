# Three Endpoints - Visual Comparison

## Quick Reference Table

```
╔════════════════╦═══════════════════╦═════════════════╦════════════════╗
║   ENDPOINT     ║      /ask         ║     /ingest     ║    /retrieve   ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ URL            ║ POST /ask         ║ POST            ║ POST           ║
║                ║                   ║ /api/ingestion  ║ /api/ingestion ║
║                ║                   ║ /ingest         ║ /retrieve      ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ PURPOSE        ║ Answer policy     ║ Upload & index  ║ Search chunks  ║
║                ║ questions with    ║ PDF documents   ║ by similarity  ║
║                ║ full analysis     ║                 ║                ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ INPUT          ║ JSON:             ║ Form Data:      ║ JSON:          ║
║                ║ {                 ║ file: <PDF>     ║ {              ║
║                ║   "query": "...",  ║                 ║   "query":"...║
║                ║   "conversation   ║                 ║   "k": 6       ║
║                ║    _id": ""        ║                 ║ }              ║
║                ║ }                 ║                 ║                ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ OUTPUT         ║ Answer with:      ║ Ingestion       ║ Chunks with:   ║
║                ║ • Result text     ║ status:         ║ • Chunk text   ║
║                ║ • Confidence 0-1  ║ • Filename      ║ • Metadata     ║
║                ║ • Risk level      ║ • Chunks created║ • Source doc   ║
║                ║ • SLO metrics     ║ • Pages         ║ • Page number  ║
║                ║ • Escalation      ║ • Timestamp     ║ • Section      ║
║                ║ • Sources         ║                 ║ • Chunk ID     ║
║                ║ • Route (RAG/SQL) ║                 ║ • Timestamp    ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ PROCESSING     ║ ~2000ms target    ║ Depends on PDF  ║ ~200-500ms     ║
║ TIME           ║ (2400ms hard limit)║ size            ║                ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ USE CASE       ║ "What is the      ║ "Upload        ║ "Find chunks   ║
║                ║  retention        ║  employee      ║  about         ║
║                ║  policy?"         ║  handbook"     ║  vacation      ║
║                ║                   ║                 ║  policy"       ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ WHEN TO USE    ║ When you want:    ║ When you need:  ║ When you want: ║
║                ║ ✓ Full answer     ║ ✓ To populate   ║ ✓ Raw chunks   ║
║                ║ ✓ Confidence      ║   knowledge base║ ✓ For debuging ║
║                ║ ✓ Risk detection  ║ ✓ One-time      ║ ✓ Document     ║
║                ║ ✓ Escalation      ║   admin task    ║   inspection   ║
║                ║ ✓ SLO enforcement ║ ✓ Bulk upload   ║ ✓ Understanding║
║                ║ ✓ Conversation    ║                 ║   what matched ║
║                ║   tracking        ║                 ║                ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ FREQUENCY      ║ Every query       ║ Rarely (once    ║ Optional or    ║
║                ║ per user          ║ per new doc)    ║ per analysis   ║
╠════════════════╬═══════════════════╬═════════════════╬════════════════╣
║ INTERNAL USE   ║ Main endpoint     ║ Manually called ║ Used internally║
║                ║ exposed to users  ║ by admins       ║ by /ask during ║
║                ║                   ║                 ║ RAG routing    ║
╚════════════════╩═══════════════════╩═════════════════╩════════════════╝
```

---

## Detailed Workflow Comparison

### Scenario: New Employee Needs Help

```
WORKFLOW 1: Using /ingest + /retrieve (Manual, Step-by-Step)
═══════════════════════════════════════════════════════════

Step 1: Admin uploads employee handbook
┌─────────────────────────────────────┐
│ POST /api/ingestion/ingest          │
│                                     │
│ Input: employee_handbook.pdf        │
│                                     │
│ Output:                             │
│ ✓ filename: "employee_handbook.pdf" │
│ ✓ chunks_created: 245               │
│ ✓ total_pages: 98                   │
└─────────────────────────────────────┘

Step 2: Employee searches for vacation policy
┌──────────────────────────────────────────┐
│ POST /api/ingestion/retrieve             │
│                                          │
│ Input: "How many vacation days?"         │
│ k: 3                                     │
│                                          │
│ Output: Top 3 chunks:                    │
│ 1. "Vacation Days - Standard employees   │
│    get 15 days/year..."                  │
│ 2. "First year employees get 10 days..." │
│ 3. "Managers must approve vacation..."   │
└──────────────────────────────────────────┘

Step 3: Employee reads chunks manually
        ✓ Gets raw information
        ✗ No confidence score
        ✗ No risk assessment
        ✗ No escalation detection
        ✗ Manual data navigation


WORKFLOW 2: Using /ask (Automatic, Complete Analysis)
═══════════════════════════════════════════════════════

Single Step: Employee asks question
┌──────────────────────────────────────────────┐
│ POST /ask                                    │
│                                              │
│ Input: "How many vacation days can I take    │
│         in my first year?"                   │
│                                              │
│ Output: Complete Analysis:                   │
│                                              │
│ Answer:                                      │
│ "Based on policy, first year employees      │
│  receive 10 days of vacation per year..."   │
│                                              │
│ confidence_score: 0.94                       │
│ ✓ System is 94% confident                   │
│                                              │
│ risk_level: "low"                            │
│ ✓ Safe question, no escalation needed       │
│                                              │
│ sources: ["employee_handbook.pdf"]           │
│ ✓ Came from official handbook                │
│                                              │
│ slo_metrics: {                               │
│   latency_ms: 1823,                          │
│   slo_status: "pass",                        │
│   enforcement_action: "none"                 │
│ }                                            │
│ ✓ Response was fast and met all SLO          │
│                                              │
│ escalate: false                              │
│ ✓ No need for human review                   │
│                                              │
│ route: "rag"                                 │
│ ✓ Used document retrieval (not SQL)          │
└──────────────────────────────────────────────┘

Result: One call gives you everything! ✓
```

---

## Data Flow Diagram

### /ingest Flow (Upload)
```
┌─────────────┐
│ PDF Upload  │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Parse PDF    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Split Chunks │ (1000 chars, 200 overlap)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Embed Chunks │ (Generate 1536-dim vectors)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Store DB     │ (PostgreSQL + pgvector)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Return       │ IngestResponse
│ Status       │ (chunks_created, pages, etc)
└──────────────┘
```

### /retrieve Flow (Search)
```
┌─────────────┐
│ Query       │ "vacation policy"
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Embed Query  │ (Generate vector from query)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Vector Search│ (pgvector similarity)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Get Top-k    │ (k=6 or user-specified)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Add Metadata │ (source, page, section)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Return       │ RetrieveResponse
│ Chunks       │ (content + metadata)
└──────────────┘
```

### /ask Flow (Complete Analysis)
```
┌─────────────┐
│ Query       │ "What is retention policy?"
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Validate     │ (Check PII, length)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Detect Intent│ (RAG/SQL/Hybrid)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Route Query  │ (Call appropriate agent)
└──────┬───────┘
       │
    ┌──┴───┬──────────┐
    │      │          │
    ▼      ▼          ▼
 ┌────┐ ┌────┐    ┌────────┐
 │RAG │ │SQL │    │HYBRID  │
 └─┬──┘ └─┬──┘    └─┬──────┘
   │      │         │
   └──────┼─────────┘
          │
          ▼
   ┌──────────────┐
   │ Get Response │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Assess Risk  │ (low/medium/high)
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Check Escalat│ (Need human review?)
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ SLO Enforce  │ (Check latency, confidence)
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Return       │ AskResponse
   │ Complete     │ (Answer + analysis)
   │ Analysis     │
   └──────────────┘
```

---

## Response Size Comparison

### /ingest Response (Smallest)
```json
{
  "filename": "retention_policy.pdf",
  "document_name": "retention_policy",
  "chunks_created": 45,
  "total_pages": 12,
  "status": "indexed",
  "timestamp": "2024-07-10T14:32:18.123456Z"
}
```
**Size**: ~200 bytes

---

### /retrieve Response (Medium)
```json
{
  "query": "retention policy",
  "chunks": [
    {
      "content": "...chunk text here...",
      "metadata": {
        "id": 42,
        "document_name": "retention_policy",
        "page_number": 5,
        "section": "3.2 Data Retention",
        "chunk_number": 3
      }
    },
    // ... up to k chunks
  ],
  "count": 3,
  "timestamp": "2024-07-10T14:35:42.987654Z"
}
```
**Size**: ~5-10 KB (depends on k and chunk size)

---

### /ask Response (Largest)
```json
{
  "query": "What is the retention policy?",
  "conversation_id": "conv_123",
  "intent": { "intent": "rag", "reason": "..." },
  "route": "rag",
  "result": { "result": "...full answer..." },
  "risk": { "risk_level": "low", "reason": "..." },
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
  "confidence_score": 0.92,
  "sources": ["retention_policy.pdf"],
  "sql_validation": "Valid SQL generated",
  "recommendation": "Review with compliance officer"
}
```
**Size**: ~3-5 KB

---

## Feature Comparison Matrix

| Feature | /ask | /ingest | /retrieve |
|---------|------|---------|-----------|
| Requires Authentication | ✓ | ✓ | ✓ |
| Rate Limited | ✓ (50/hour) | ✗ | ✗ |
| SLO Enforced | ✓ (2400ms limit) | ✗ | ✗ |
| Returns Answer | ✓ | ✗ | ✗ (raw chunks) |
| Confidence Score | ✓ | ✗ | ✗ |
| Risk Assessment | ✓ | ✗ | ✗ |
| Escalation Detection | ✓ | ✗ | ✗ |
| Conversation Memory | ✓ | ✗ | ✗ |
| Logs to Database | ✓ (AIQuery) | ✓ (Documents) | ✗ |
| Vector Search Used | ✓ (internally) | ✗ (storage) | ✓ (retrieval) |
| Latency Enforcement | ✓ | ✗ | ✗ |
| Multi-Agent Routing | ✓ (RAG/SQL/Hybrid) | ✗ | ✗ |
| Cost Tracking | ✓ (disabled) | ✗ | ✗ |

---

## HTTP Status Codes by Endpoint

### /ask Endpoint
- 200 OK - Success, SLO met
- 202 ACCEPTED - Success, SLO warning
- 400 BAD_REQUEST - Invalid query
- 403 FORBIDDEN - Permission denied
- 422 UNPROCESSABLE - Confidence too low
- 429 TOO_MANY - Rate limit exceeded
- 503 UNAVAILABLE - Latency SLO exceeded
- 500 ERROR - Processing error

### /ingest Endpoint
- 200 OK - Document indexed
- 400 BAD_REQUEST - Not PDF or empty
- 403 FORBIDDEN - Permission denied
- 500 ERROR - Indexing failed

### /retrieve Endpoint
- 200 OK - Search successful (may have 0 results)
- 400 BAD_REQUEST - Query empty/too long
- 403 FORBIDDEN - Permission denied
- 500 ERROR - Search failed

---

## Typical Usage Pattern

```
Day 1: Admin Activity
┌─────────────────────────────────────┐
│ Upload company policies            │
│ POST /api/ingestion/ingest (once)  │
│ Response: 500 chunks indexed       │
└─────────────────────────────────────┘

Days 2+: Employee Activity
┌─────────────────────────────────────┐
│ Ask policy questions                │
│ POST /ask (many times per day)      │
│                                     │
│ Each query includes:                │
│ • Full answer                       │
│ • Confidence score                  │
│ • Risk assessment                   │
│ • SLO enforcement                   │
│ • Escalation detection              │
└─────────────────────────────────────┘

Optional: Developer/Researcher Activity
┌─────────────────────────────────────┐
│ Debug/inspect what was retrieved    │
│ POST /api/ingestion/retrieve        │
│ (to understand /ask results)        │
└─────────────────────────────────────┘
```

---

## Summary

| Aspect | /ask | /ingest | /retrieve |
|--------|------|---------|-----------|
| **Type** | Query | Upload | Search |
| **Frequency** | Every query | One-time | Optional |
| **User** | Everyone | Admin | Developer |
| **Output** | Full Answer | Status | Chunks |
| **SLO** | Enforced | Not Enforced | Not Enforced |
| **Confidence** | Included | N/A | N/A |
| **Risk** | Included | N/A | N/A |
| **Best For** | Getting answers | Populating KB | Debugging |

