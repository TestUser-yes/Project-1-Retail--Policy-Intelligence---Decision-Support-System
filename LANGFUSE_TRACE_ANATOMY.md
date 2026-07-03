# Langfuse Trace Anatomy

## Complete Trace Structure for `/ask` Query

This document shows exactly what data flows through Langfuse for each query.

---

## Root Trace: `ask-query`

```json
{
  "trace_id": "conv-abc123def456",
  "name": "ask-query",
  "user_id": "user123",
  "session_id": "conv-abc123def456",
  "metadata": {
    "query_length": 42,
    "user_role": "user",
    "timestamp": "2026-07-03T10:30:45.123Z"
  },
  "start_time": 1751234445.123,
  "duration_ms": 245.67
}
```

---

## Spans Within the Trace

### 1. Permission Check Span
```json
{
  "name": "permission-check",
  "input": {
    "user_id": "user123",
    "role": "user"
  },
  "output": {
    "allowed": true
  },
  "duration_ms": 2.5,
  "level": "INFO"
}
```

**What it tracks**:
- User authentication status
- User role (user, compliance_officer, admin)
- Permission validation result
- Permission granted or denied

**Why it matters**:
- Audit trail of access control
- Debug permission issues
- Track user roles over time

---

### 2. Input Validation Span
```json
{
  "name": "input-validation",
  "input": {
    "query": "What is the refund policy?"
  },
  "output": {
    "is_valid": true
  },
  "duration_ms": 5.2,
  "level": "INFO"
}
```

**What it tracks**:
- Query format validation
- Length check (3-10K characters)
- UTF-8 encoding validation
- Validation pass/fail result

**Why it matters**:
- Identify malformed queries
- Track validation failures
- Debug encoding issues

---

### 3. Rate Limit Check Span
```json
{
  "name": "rate-limit-check",
  "input": {
    "user_id": "user123",
    "endpoint": "/ask"
  },
  "output": {
    "allowed": true,
    "tokens_remaining": 47,
    "limit": 50
  },
  "duration_ms": 1.1,
  "metadata": {
    "tokens_remaining": 47
  }
}
```

**What it tracks**:
- Rate limit enforcement
- Tokens remaining in bucket
- Per-user limit status
- Allowed vs blocked requests

**Why it matters**:
- Identify rate limit abusers
- Track quota usage
- Debug rate limit issues

---

### 4. Query Orchestration Span
```json
{
  "name": "query-orchestration",
  "input": {
    "query": "What is the refund policy?"
  },
  "output": {
    "intent": "policy",
    "route": "rag",
    "risk_level": "low",
    "escalate": false
  },
  "duration_ms": 180.5,
  "level": "INFO"
}
```

**What it tracks**:
- Intent detection (policy, vendor, hybrid)
- Routing decision (RAG, SQL, Hybrid)
- Risk assessment result
- Escalation requirement

**Why it matters**:
- Analyze routing accuracy
- Debug intent detection
- Monitor risk assessment
- Identify escalation patterns

---

### 5. Cost Tracking Span
```json
{
  "name": "cost-tracking",
  "input": {
    "query_length": 27,
    "response_length": 156
  },
  "output": {
    "cost_usd": 0.00,
    "budget_remaining": 99.985,
    "budget_used_percent": 0.015
  },
  "metadata": {
    "cost_usd": 0.00,
    "budget_remaining": 99.985,
    "budget_used_percent": 0.015
  }
}
```

**What it tracks**:
- Query cost (USD)
- Token usage (query/response lengths)
- Budget remaining
- Budget percentage used

**Why it matters**:
- Monitor spending
- Track cost trends
- Predict budget exhaustion
- Compare cost by route/user

---

### 6. HTTP Response Span
```json
{
  "name": "http-response",
  "input": {
    "method": "POST",
    "path": "/ask"
  },
  "output": {
    "status_code": 200,
    "latency_ms": 245.67
  },
  "duration_ms": 245.67,
  "level": "INFO"
}
```

**What it tracks**:
- HTTP status code (200, 400, 429, 500)
- Response latency
- HTTP method and path
- Overall request duration

**Why it matters**:
- Monitor API health
- Track performance
- Identify slow endpoints
- Debug HTTP issues

---

## Complete Request/Response Cycle

### Request
```bash
POST /ask HTTP/1.1
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "query": "What is the refund policy?",
  "conversation_id": "conv-abc123def456"
}
```

### Response
```json
{
  "query": "What is the refund policy?",
  "conversation_id": "conv-abc123def456",
  "intent": {
    "intent": "policy",
    "reason": "Query mentions 'policy'"
  },
  "route": "rag",
  "result": {
    "result": "Our refund policy states..."
  },
  "risk": {
    "risk_level": "low",
    "reason": "No sensitive information detected"
  },
  "escalate": false,
  "latency_seconds": 0.2456,
  "cost_usd": 0.00,
  "budget_remaining_usd": 99.985,
  "budget_percent_used": 0.015,
  "validation_passed": true
}
```

### Response Header
```
X-Trace-ID: conv-abc123def456
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 47
```

---

## Trace Timeline

```
T=0ms      ┌─ ask-query trace starts
           │  user_id: user123, session_id: conv-abc...
           │
T=2ms      ├─ permission-check (2ms)
           │  ✓ User has permission
           │
T=7ms      ├─ input-validation (5ms)
           │  ✓ Query valid (27 chars)
           │
T=8ms      ├─ rate-limit-check (1ms)
           │  ✓ Allowed (47 tokens remaining)
           │
T=188ms    ├─ query-orchestration (180ms)
           │  ├─ Intent: policy
           │  ├─ Route: rag
           │  ├─ Risk: low
           │  └─ Escalate: false
           │
T=200ms    ├─ cost-tracking (metadata)
           │  ├─ Cost: $0.00
           │  ├─ Budget: $99.985
           │  └─ Usage: 0.015%
           │
T=246ms    ├─ http-response (246ms total)
           │  ├─ Status: 200
           │  └─ Latency: 245.67ms
           │
T=246ms    └─ ask-query trace ends
              Trace ID: conv-abc123def456
              Total duration: 246ms
```

---

## Data Points Captured

### Per Trace
- Trace ID (unique identifier)
- Trace name
- User ID
- Session/Conversation ID
- Start timestamp
- Duration

### Per Span
- Span name
- Input data
- Output data
- Duration
- Log level
- Custom metadata

### Metadata Examples
```json
{
  "query_length": 27,
  "user_role": "user",
  "intent": "policy",
  "route": "rag",
  "risk_level": "low",
  "cost_usd": 0.00,
  "latency_ms": 245.67,
  "tokens_remaining": 47,
  "escalate": false
}
```

---

## Error Trace Example

When an error occurs:

```json
{
  "trace_id": "conv-error123",
  "name": "ask-query",
  "user_id": "user123",
  "spans": [
    {
      "name": "permission-check",
      "output": { "allowed": true }
    },
    {
      "name": "input-validation",
      "output": { 
        "is_valid": false, 
        "error": "Query too long (11,500 chars > 10,000 max)"
      }
    },
    {
      "name": "error",
      "output": {
        "error": "Query validation failed: Query too long"
      }
    }
  ]
}
```

---

## Trace Aggregation Examples

### By Route (RAG vs SQL)
```
Total Queries: 1000
├─ RAG: 650 (65%)
│  ├─ Avg Latency: 180ms
│  ├─ Avg Cost: $0.008
│  └─ Success Rate: 98%
├─ SQL: 300 (30%)
│  ├─ Avg Latency: 120ms
│  ├─ Avg Cost: $0.002
│  └─ Success Rate: 97%
└─ Hybrid: 50 (5%)
   ├─ Avg Latency: 250ms
   ├─ Avg Cost: $0.012
   └─ Success Rate: 95%
```

### By User
```
Top Users by Cost:
1. user456: $12.45 (145 queries)
2. user123: $8.90 (98 queries)
3. user789: $5.33 (67 queries)
```

### By Risk Level
```
Risk Distribution:
├─ Low: 900 (90%)
├─ Medium: 80 (8%)
├─ High: 15 (1.5%)
└─ Critical: 5 (0.5%)
```

---

## Performance Baseline

### Typical Span Durations
| Operation | Typical Duration | Range |
|-----------|------------------|-------|
| Permission Check | 2ms | 1-5ms |
| Input Validation | 5ms | 3-10ms |
| Rate Limit Check | 1ms | 0-3ms |
| Query Orchestration | 150ms | 50-300ms |
| Total Request | 200ms | 100-400ms |

### Budget Usage Example
```
Daily Budget: $100.00

After 100 queries (mix of RAG/SQL):
- Average cost/query: $0.008
- Total spent: $0.80
- Budget remaining: $99.20
- Usage rate: 0.8%
- Estimated daily usage: $11.52
- Status: Excellent
```

---

## Summary

Each trace provides complete visibility into:
- ✅ **Security**: Who accessed, permissions checked
- ✅ **Quality**: Intent detection, risk assessment
- ✅ **Performance**: Latency for each operation
- ✅ **Cost**: Financial impact of each query
- ✅ **Routing**: Which handler processed the query
- ✅ **Errors**: What went wrong and why
- ✅ **Context**: Conversation history, user info
- ✅ **Audit**: Complete record for compliance

This comprehensive tracing enables:
- Real-time monitoring
- Performance optimization
- Cost management
- Security auditing
- Debugging and troubleshooting
- Usage analytics
- Capacity planning
