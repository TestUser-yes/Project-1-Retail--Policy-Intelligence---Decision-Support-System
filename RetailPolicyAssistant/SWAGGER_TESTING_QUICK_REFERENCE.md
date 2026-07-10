# Swagger Testing - Quick Reference Card

**Access Swagger**: `http://localhost:8000/docs`

---

## 🔑 Before Testing - Get Token

```bash
# Terminal:
curl -s http://localhost:8000/token | jq -r '.access_token'

# Copy the token, then:
# 1. In Swagger UI, click green "Authorize" button
# 2. Paste token in dialog
# 3. Click "Authorize"
# 4. Close dialog
```

---

## Test 1: Health Check (No Auth Required)

**Endpoint**: `GET /health`

**In Swagger**:
1. Find "GET /health"
2. Click "Try it out"
3. Click "Execute"

**Expected**:
```json
{
  "status": "healthy",
  "timestamp": "2024-07-10T14:30:00Z"
}
```

**Status**: 200 OK ✓

---

## Test 2: Upload Document

**Endpoint**: `POST /api/ingestion/ingest`

**In Swagger**:
1. Find "POST /api/ingestion/ingest"
2. Click "Try it out"
3. Click "Choose File" button
4. Select a PDF from your computer
5. Click "Execute"

**Body**: Multipart form-data with file

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

## Test 3: Search Documents

**Endpoint**: `POST /api/ingestion/retrieve`

**In Swagger**:
1. Find "POST /api/ingestion/retrieve"
2. Click "Try it out"
3. In "Request body" field, paste:

```json
{
  "query": "retention policy",
  "k": 3
}
```

4. Click "Execute"

**Expected Response**:
```json
{
  "query": "retention policy",
  "chunks": [
    {
      "content": "Section 3.2: Data Retention Policy...",
      "metadata": {
        "id": 1,
        "document_name": "your_file",
        "page_number": 2,
        "section": "3.2 Overview",
        "chunk_number": 0
      }
    }
  ],
  "count": 1,
  "timestamp": "2024-07-10T14:35:42.987654Z"
}
```

**Status**: 200 OK ✓

---

## Test 4: Ask Policy Question (MAIN TEST)

**Endpoint**: `POST /ask`

**In Swagger**:
1. Find "POST /ask"
2. Click "Try it out"
3. In "Request body" field, paste:

```json
{
  "query": "What is our retention policy for customer data?",
  "conversation_id": ""
}
```

4. Click "Execute"

**Expected Response** (Large, full response):
```json
{
  "query": "What is our retention policy for customer data?",
  "conversation_id": "conv_abc123xyz",
  "intent": {
    "intent": "rag",
    "reason": "User asking about policy details - RAG best suited"
  },
  "route": "rag",
  "result": {
    "result": "According to our retention policy, customer personal data must be retained for a minimum of 7 years following account closure or last transaction, in compliance with GDPR Article 5 and applicable data protection regulations."
  },
  "risk": {
    "risk_level": "low",
    "reason": "Standard policy information request with no sensitive triggers"
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
  "confidence_score": 0.92,
  "sources": [
    "documents/retention_policy_2024.pdf"
  ],
  "sql_validation": "Valid SQL generated",
  "recommendation": "Review with compliance officer before implementation"
}
```

**Status**: 200 OK ✓

---

## Test 5: Ask Different Type of Question

**Endpoint**: `POST /ask`

**Try**: High-risk escalation

```json
{
  "query": "Can we delete customer data from the EU without notifying them?",
  "conversation_id": ""
}
```

**Expected**:
- escalate: true
- risk_level: "high"
- Status: 200 OK (but escalated)

---

## Test 6: Low Confidence Scenario

**Endpoint**: `POST /ask`

**Try**: Ambiguous question

```json
{
  "query": "blah blah blah random words",
  "conversation_id": ""
}
```

**Expected**:
- confidence_score: Low (< 0.70)
- Status: 422 UNPROCESSABLE_ENTITY (escalated)

---

## Test 7: View Dashboard

**Endpoint**: `GET /api/dashboard`

**In Swagger**:
1. Find "GET /api/dashboard"
2. Click "Try it out"
3. Click "Execute"

**Expected**: Metrics including:
- Total queries
- Average latency
- SLO compliance rate
- Escalation count
- Query distributions

---

## Test 8: View Observability

**Endpoint**: `GET /api/observability`

**In Swagger**:
1. Find "GET /api/observability"
2. Click "Try it out"
3. Click "Execute"

**Expected**: Detailed metrics:
- Total queries (all-time + 24h)
- Risk distribution
- Route distribution
- Hourly trends
- Recent queries
- SLO metrics

---

## Response Fields Reference

### /ask Response Fields

| Field | What it Means | Example |
|-------|--------------|---------|
| `query` | Your original question | "What is retention policy?" |
| `conversation_id` | Tracks multi-turn chats | "conv_abc123" |
| `intent.intent` | Type of query | "rag", "sql", or "hybrid" |
| `route` | Which agent answered | "rag", "sql", or "hybrid" |
| `result.result` | The actual answer | "Customer data must be retained..." |
| `confidence_score` | How sure (0-1) | 0.92 = 92% confident |
| `risk.risk_level` | Safety level | "low", "medium", "high" |
| `escalate` | Needs review? | true or false |
| `latency_seconds` | Time taken | 1.823 seconds |
| `slo_metrics.slo_status` | SLO check | "pass", "warning", "fail" |
| `slo_metrics.slo_breached` | Was boundary violated? | true or false |
| `sources` | Which documents used | ["retention_policy.pdf"] |

---

## HTTP Status Codes Reference

| Code | Meaning | When It Happens |
|------|---------|-----------------|
| 200 | Success | Query successful, SLO met |
| 202 | Accepted | Success but SLO warning (needs review) |
| 400 | Bad Request | Query too short/long, invalid input |
| 403 | Forbidden | No permission (auth failed) |
| 422 | Unprocessable | Confidence too low, needs escalation |
| 429 | Too Many Requests | Rate limit exceeded |
| 503 | Service Unavailable | Latency SLO exceeded (too slow) |
| 500 | Internal Error | System error |

---

## Quick Testing Sequence

### Complete Test Flow (5 minutes)

**Step 1**: Get token
```bash
curl -s http://localhost:8000/token | jq -r '.access_token'
```

**Step 2**: In Swagger, click Authorize and paste token

**Step 3**: Test health
- GET /health → Status 200 ✓

**Step 4**: Upload PDF
- POST /ingest with a PDF file → Status 200 ✓

**Step 5**: Search documents
- POST /retrieve with query "your topic" → Status 200 ✓

**Step 6**: Ask question (MAIN)
- POST /ask with "your question" → Status 200 ✓
- Check: confidence_score, risk_level, slo_metrics

**Step 7**: View metrics
- GET /api/dashboard → See all metrics ✓

---

## Common Test Queries

### Test Basic Query
```json
{"query": "What is the company retention policy?"}
```
Expected: confidence_score ≈ 0.90+, risk_level = "low"

### Test Ambiguous Query
```json
{"query": "xyz abc 123"}
```
Expected: Status 422 (low confidence)

### Test High-Risk Query
```json
{"query": "Can we ignore data deletion requests from EU customers?"}
```
Expected: escalate = true, risk_level = "high"

### Test Long Query
```json
{"query": "I have a very long question about... " + "A" * 10000}
```
Expected: Status 200 or 400 depending on length

---

## Troubleshooting

### Issue: "Missing token"
**Solution**: Click green "Authorize" button, paste token

### Issue: "Only PDF files supported"
**Solution**: Upload a .pdf file, not .doc or .txt

### Issue: "Rate limit exceeded" (429)
**Solution**: Wait a minute before next request (50/hour limit)

### Issue: "Low confidence" (422)
**Solution**: Query will be escalated; this is expected for bad queries

### Issue: "Service Unavailable" (503)
**Solution**: Query took too long; try simpler query or wait if system is busy

---

## Expected Performance

| Operation | Typical Time | Status |
|-----------|--------------|--------|
| /health | <100ms | Instant |
| /ingest | 2-10s | Depends on PDF size |
| /retrieve | 200-500ms | Quick |
| /ask (RAG) | 1500-2000ms | ~2 seconds |
| /ask (SQL) | 1000-1500ms | ~1-1.5 seconds |
| /ask (Hybrid) | 2000-2500ms | ~2-2.5 seconds |
| /dashboard | 200-500ms | Quick |

---

## SLO Enforcement in Action

### Scenario 1: Query Under 2 seconds
```
latency_ms: 1823
slo_status: "pass"
slo_breached: false
enforcement_action: "none"
Status: 200 OK ✓
```

### Scenario 2: Query Between 2-2.4 seconds
```
latency_ms: 2150
slo_status: "warning"
slo_breached: true
enforcement_action: "warning"
Status: 202 ACCEPTED (with warning) ⚠
```

### Scenario 3: Query Over 2.4 seconds
```
latency_ms: 2600
slo_status: "fail"
slo_breached: true
enforcement_action: "reject"
Status: 503 SERVICE_UNAVAILABLE ❌
```

---

## Tips for Testing

1. **Start Simple**: Test /health first to verify server is running
2. **Upload Before Asking**: Upload a PDF before asking document questions
3. **Watch Latency**: Check latency_ms vs target_latency_ms
4. **Check Confidence**: confidence_score tells you how sure the system is
5. **Monitor SLO**: slo_metrics shows if boundaries are being met
6. **Escalation**: Look for escalate=true for sensitive topics
7. **Sources**: Check which documents were used (sources field)

---

## Documentation Links

- **Full Guide**: See `ENDPOINTS_COMPLETE_GUIDE.md`
- **Comparison**: See `THREE_ENDPOINTS_COMPARISON.md`
- **SLO Details**: See `SLO_BOUNDED_IMPLEMENTATION.md`
- **System Overview**: See `COMPLETE_SYSTEM_OVERVIEW.md`
- **Setup Instructions**: See `QUICK_SETUP.txt`

---

## Ready to Test?

1. Start server: `uvicorn app.main:app --reload --port 8000`
2. Open Swagger: `http://localhost:8000/docs`
3. Get token and authorize
4. Follow tests above
5. All status codes should be 200 or 202 ✓

**Enjoy testing your SLO-Bounded system! 🚀**

