# Multi-Agent System Visual Summary

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE / API CLIENT                        │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                          /api/ask endpoint
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INPUT VALIDATION & GUARDRAILS                            │
│  • Query validation  • Rate limiting  • Permission checking                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR (Brain)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  1. Intent Detection (Keyword Analysis)                            │  │
│  │     Query → Policy/Vendor/Compliance keywords → Intent             │  │
│  │                                                                     │  │
│  │  2. Risk Assessment (Low/Medium/High)                              │  │
│  │     Query → Risk classifier → Risk level                           │  │
│  │                                                                     │  │
│  │  3. Routing Decision (Which agent(s) to call)                     │  │
│  │     Intent → Routing logic → Route: RAG/SQL/HYBRID                │  │
│  │                                                                     │  │
│  │  4. Agent Invocation (Execute chosen path)                         │  │
│  │     Route → Call agent(s) → Collect results                       │  │
│  │                                                                     │  │
│  │  5. Response Synthesis (Combine results)                           │  │
│  │     Results → Combine + Score → Final response                    │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────┬──────────────────────────┬──────────────────────────────┬─────────────┘
     │                          │                              │
     ▼                          ▼                              ▼
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│   RAG AGENT        │  │   SQL AGENT        │  │  HYBRID MODE       │
├────────────────────┤  ├────────────────────┤  ├────────────────────┤
│ Semantic Search    │  │ Text-to-SQL        │  │ Parallel Exec      │
│ on PDF Documents   │  │ on Database        │  │ (RAG + SQL)        │
├────────────────────┤  ├────────────────────┤  ├────────────────────┤
│ Confidence: 0.92   │  │ Confidence: 0.85   │  │ Avg Confidence     │
│ Data: PDFs         │  │ Data: Database     │  │ Data: Both         │
└────────────────────┘  └────────────────────┘  └────────────────────┘
     │                          │                              │
     │                          │                  ┌───────────┘
     │                          │                  │
     └──────────────┬───────────┴──────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   Confidence Scoring              │
    │   (4-factor model)                │
    │   • Source quality                │
    │   • Relevance matching            │
    │   • Consistency                   │
    │   • Timeliness                    │
    └───────────────┬───────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   SLO & Observability             │
    │   • Latency tracking              │
    │   • Agent metrics                 │
    │   • LangFuse tracing              │
    └───────────────┬───────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────────────┐
    │   API RESPONSE                                            │
    │   ├─ answer (synthesized result)                         │
    │   ├─ agents_used: ["rag_agent"], ["sql_agent"], etc.   │
    │   ├─ agent_details: [{latency, confidence, status}]    │
    │   ├─ confidence_score: 0.92                             │
    │   ├─ sources: ["PDF", "Database"]                       │
    │   ├─ latency_seconds: 0.25                              │
    │   └─ escalation_needed: true/false                      │
    └───────────────────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────────────┐
    │   DATABASE & OBSERVABILITY                                │
    │   ├─ Store query & response                              │
    │   ├─ Record agent routing                                │
    │   ├─ Track SLO compliance                                │
    │   └─ Update metrics for dashboard                        │
    └───────────────────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────────────┐
    │   LANGFUSE TRACING (Optional)                             │
    │   Full trace visualization of:                            │
    │   • Orchestrator decisions                               │
    │   • Agent executions                                     │
    │   • LLM API calls                                        │
    │   • Token usage & costs                                  │
    └───────────────────────────────────────────────────────────┘
```

---

## Query Intent Detection Flow

```
Query: "Which vendors comply with our encryption policy?"
        │
        ▼
┌─────────────────────────────────────────┐
│ Extract Keywords                        │
├─────────────────────────────────────────┤
│ Policy: [encryption, policy]            │
│ Vendor: [vendors]                       │
│ Compliance: [comply, compliance]        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Apply Priority Rules                    │
├─────────────────────────────────────────┤
│ Priority 1: Compliance + Vendor?       │
│   ✓ has_compliance = True               │
│   ✓ has_vendor = True                   │
│   → HYBRID ✓                            │
└────────┬────────────────────────────────┘
         │
         ▼
  Route: HYBRID
         │
    ┌────┴────┐
    │          │
    ▼          ▼
 RAG Agent   SQL Agent
  (PDFs)    (Database)
    │          │
    └────┬─────┘
         │
         ▼
    Combine Results
         │
         ▼
    Response with Both Agents
```

---

## Response Payload Structure

### API Response with Agent Details

```json
{
  "query": "Which vendors comply with our encryption policy?",
  "route": "hybrid",
  "result": {
    "result": "Policy Analysis:\nEncryption Policy requires...\n\nDatabase Validation:\nVendors with encryption cert: 15/42"
  },
  "confidence_score": 0.88,
  
  "agents_used": ["rag_agent", "sql_agent"],
  
  "agent_details": [
    {
      "agent_name": "RAG Agent",
      "status": "success",
      "latency_ms": 245.3,
      "confidence": 0.92,
      "data_source": "PDF Documents"
    },
    {
      "agent_name": "SQL Agent",
      "status": "success",
      "latency_ms": 189.7,
      "confidence": 0.85,
      "data_source": "Database"
    }
  ],
  
  "sources": ["Encryption Policy.pdf", "Database"],
  "latency_seconds": 0.435,
  "escalate": false,
  "risk": {
    "risk_level": "low",
    "reason": "Routine policy query"
  }
}
```

---

## Agent Routing Decision Tree

```
                            Query Received
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Policy + Compliance?   │
                    └────┬──────────┬──────────┘
                        Yes        No
                         │          │
                         ▼          ▼
                      HYBRID    ┌──────────────┐
                               │ Compliance   │
                               │ Keywords?    │
                               └────┬─────┬──┘
                                  Yes    No
                                   │      │
                                   ▼      ▼
                                  RAG   ┌──────────────┐
                                       │ Vendor +     │
                                       │ Policy?      │
                                       └────┬─────┬──┘
                                         Yes    No
                                          │      │
                                          ▼      ▼
                                       HYBRID  ┌──────────────┐
                                              │ SQL          │
                                              │ Indicators?  │
                                              └────┬─────┬──┘
                                                Yes    No
                                                 │      │
                                                 ▼      ▼
                                                SQL    RAG
```

---

## Agent Execution Timeline (Hybrid Query)

```
Start Request: 0ms
       │
       ├─ Intent Detection: 5ms
       │
       ├─ Risk Assessment: 8ms
       │
       ├─ Route Decision: 2ms
       │  (Decided: HYBRID)
       │
       ├─ RAG Agent Start: 12ms ─────────────────┐
       │  [Semantic search on PDFs]              │
       │  [LLM call for answer]                  │
       │  ────────────────────────────── 245ms ──┤
       │                                          │
       ├─ SQL Agent Start: 14ms ────────────┐    │
       │  [Natural language to SQL]         │    │
       │  [Execute query]                   │    │
       │  ───────────── 189ms ──────────────┤    │
       │                                    │    │
       ├─ Wait for both: ───────────────────┴────┤
       │  (Parallel execution)                   │
       │  Max latency: 245ms                      │
       │                                          │
       ├─ Confidence Scoring: 12ms
       │  (Average: (0.92 + 0.85) / 2 = 0.88)
       │
       ├─ Response Building: 8ms
       │
       ├─ Database Save: 15ms
       │
       └─ Response Sent: 435ms total
```

---

## System Benefits Visualization

### Single-Agent Routing (80% of queries)
```
Query → Orchestrator → Single Agent → Fast Response
                      ✓ No wasted resources
                      ✓ Low latency
                      ✓ High efficiency
```

### Hybrid Routing (20% of queries)
```
Query → Orchestrator → RAG Agent ──┐
                   └→ SQL Agent ───┬→ Combined Response
                                   ✓ Complete answer
                                   ✓ Policy + Data
                                   ✓ High accuracy
```

---

## Confidence Score by Agent Type

```
Confidence Breakdown:
│
├─ RAG Agent (PDF-based)
│  ├─ With exact document match: 0.92
│  ├─ With partial match: 0.75
│  └─ No match (fallback): 0.50
│
├─ SQL Agent (Database-based)
│  ├─ With exact results: 0.90
│  ├─ With query interpretation: 0.85
│  └─ With ambiguous results: 0.60
│
└─ Hybrid (Combined)
   ├─ Both agents high confidence: 0.90
   ├─ Mixed confidence: 0.85
   └─ One agent low confidence: 0.70
```

---

## Observability Metrics Dashboard

```
┌────────────────────────────────────────────────────────┐
│          MULTI-AGENT SYSTEM DASHBOARD                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Agent Call Distribution (Last 24 Hours)              │
│  ┌──────────────────────────────────────────┐         │
│  │ RAG Agent:      ███████░  42 calls (42%) │         │
│  │ SQL Agent:      ███████░  38 calls (38%) │         │
│  │ Hybrid Mode:    ████░░░░  20 calls (20%) │         │
│  │ Total:          100 calls                │         │
│  └──────────────────────────────────────────┘         │
│                                                        │
│  Routing Efficiency                                    │
│  ├─ Single-Agent: 80% (Fast, efficient)               │
│  ├─ Hybrid: 20% (For complex queries)                 │
│  └─ Optimal Mix: ✓                                    │
│                                                        │
│  Average Latency by Agent                             │
│  ├─ RAG: 245ms (PDF retrieval)                        │
│  ├─ SQL: 189ms (Database query)                       │
│  └─ Hybrid: 434ms (Both agents)                       │
│                                                        │
│  Confidence Scores                                     │
│  ├─ RAG: Avg 0.92 (High confidence)                   │
│  ├─ SQL: Avg 0.85 (Good confidence)                   │
│  └─ Hybrid: Avg 0.88 (Strong confidence)              │
│                                                        │
│  SLO Compliance                                        │
│  ├─ Target Latency: 2000ms                            │
│  ├─ Achieved: 434ms avg                               │
│  ├─ Compliance: ✓ 100%                                │
│  └─ Status: PASS                                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Demo Demonstration Strategy

### Timeline: 5 Minutes

```
Minute 1: Show Architecture
├─ Display agent diagram
├─ Explain intent detection
└─ Show 3 agent types

Minute 2: Test RAG Query
├─ Send: "What is the data retention policy?"
├─ Show: agents_used: ["rag_agent"]
└─ Show: latency_ms: 245, confidence: 0.92

Minute 3: Test SQL Query
├─ Send: "How many vendors do we have?"
├─ Show: agents_used: ["sql_agent"]
└─ Show: latency_ms: 189, confidence: 0.85

Minute 4: Test Hybrid Query
├─ Send: "Which vendors comply with encryption policy?"
├─ Show: agents_used: ["rag_agent", "sql_agent"]
└─ Show: latency_ms: 434, confidence: 0.88

Minute 5: Show Dashboard
├─ /api/observability endpoint
├─ Agent routing stats
└─ SLO compliance metrics
```

---

## Key Takeaways

✅ **Not Just RAG** - Multiple specialized agents, not a single retrieval system
✅ **Smart Routing** - Only calls agents that are needed for each query
✅ **Observable** - Full visibility into which agents answered each query
✅ **Performant** - 80% of queries answered by single agent (fast)
✅ **Accurate** - Confidence scores reflect data source reliability
✅ **Scalable** - Easy to add more agents as needed
✅ **Professional** - Enterprise-grade orchestration with SLO tracking

