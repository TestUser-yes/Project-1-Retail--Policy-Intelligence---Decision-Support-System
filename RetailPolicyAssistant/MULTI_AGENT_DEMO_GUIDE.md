# Multi-Agent System Demo Guide

## Quick Summary

Your Retail Policy Intelligence platform uses a **multi-agent orchestration system** that intelligently routes queries to different agents based on query intent:

- **RAG Agent** → For policy document retrieval (PDFs)
- **SQL Agent** → For database queries (vendor data, counts, lists)
- **Hybrid Mode** → For complex queries needing both policy + data

---

## How to Demonstrate Multi-Agent Usage

### **Method 1: LangFuse Dashboard (BEST FOR VISUAL PROOF) ⭐**

#### Setup (2 minutes):

1. Go to https://cloud.langfuse.com and sign up
2. Create a new project
3. Copy your `PUBLIC_KEY` and `SECRET_KEY`
4. Add to your `.env` file:
   ```
   LANGFUSE_PUBLIC_KEY=pk_xxx
   LANGFUSE_SECRET_KEY=sk_xxx
   LANGFUSE_BASE_URL=https://cloud.langfuse.com
   ```
5. Restart your FastAPI server

#### Demo Flow:

```bash
# Terminal 1: Start your server
python -m uvicorn app.main:app --reload

# Terminal 2: Run demo queries
curl -X POST http://localhost:8000/api/ask \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the data retention policy?"}'
```

**Then in LangFuse Dashboard:**
- Open https://cloud.langfuse.com → Your Project
- You'll see a **trace tree** showing:
  - `Orchestrator.run()` (main coordinator)
  - `RAGAgent.run()` (PDF retrieval)
  - LLM calls and token usage
  - Exact latency for each agent

---

### **Method 2: API Response Visibility (IMMEDIATE)**

#### Try these test queries:

**Query 1: RAG Only**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the data retention policy?"}'
```

**Response will show:**
```json
{
  "query": "What is the data retention policy?",
  "route": "rag",
  "agents_used": ["rag_agent"],
  "agent_details": [
    {
      "agent_name": "RAG Agent",
      "status": "success",
      "latency_ms": 245.3,
      "confidence": 0.92,
      "data_source": "PDF Documents"
    }
  ],
  "confidence_score": 0.92,
  "sources": ["Data Retention Policy.pdf"]
}
```

---

**Query 2: SQL Only**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vendors do we have?"}'
```

**Response will show:**
```json
{
  "query": "How many vendors do we have?",
  "route": "sql",
  "agents_used": ["sql_agent"],
  "agent_details": [
    {
      "agent_name": "SQL Agent",
      "status": "success",
      "latency_ms": 189.7,
      "confidence": 0.85,
      "data_source": "Database"
    }
  ],
  "confidence_score": 0.85,
  "sources": ["Database"]
}
```

---

**Query 3: Hybrid (Both Agents)**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which vendors comply with our encryption policy?"}'
```

**Response will show:**
```json
{
  "query": "Which vendors comply with our encryption policy?",
  "route": "hybrid",
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
  "confidence_score": 0.88,
  "sources": ["Encryption Policy.pdf", "Database"]
}
```

---

### **Method 3: Demo Endpoint (Educational)**

```bash
curl http://localhost:8000/api/observability/demo-agents
```

This shows:
- How each agent works
- Example trigger queries
- Routing logic rules
- Intent detection keywords

---

### **Method 4: Observability Dashboard**

```bash
curl http://localhost:8000/api/observability
```

Returns stats like:
```json
{
  "multi_agent_summary": {
    "rag_agent_calls": 42,
    "sql_agent_calls": 38,
    "hybrid_agent_calls": 20,
    "total_agent_calls": 100,
    "agent_routing_efficiency": {
      "single_agent_percentage": 80.0,
      "hybrid_percentage": 20.0
    }
  }
}
```

Shows that your system intelligently routes:
- 80% of queries to single agents (fast)
- 20% to hybrid mode (when needed for complex queries)

---

## Query Examples for Demo

### Queries That Trigger RAG Agent (Policy Documents):
```
- "What is the data retention policy?"
- "Explain GDPR compliance requirements"
- "Tell me about the incident response policy"
- "What are PII handling standards?"
- "Describe vendor background check requirements"
```

### Queries That Trigger SQL Agent (Database):
```
- "How many vendors do we have?"
- "List all critical vendors"
- "Show vendors with approval status"
- "Count vendors with security certifications"
- "Which vendors need background verification?"
```

### Queries That Trigger Hybrid Mode (Both):
```
- "Which vendors comply with our encryption policy?"
- "List vendors that meet GDPR requirements"
- "Show vendors with high risk assessment scores"
- "Which vendors follow our data retention standards?"
- "Are our vendors compliant with incident response policies?"
```

---

## Talking Points for Demo

### "What is Multi-Agent in Your System?"

Your system uses **intelligent agent orchestration** where:

1. **Query arrives** → Orchestrator analyzes it
2. **Intent detection** → Uses keyword analysis to determine type
3. **Routing decision** → Selects appropriate agent(s)
4. **Parallel execution** → Agents run simultaneously if needed
5. **Response synthesis** → Combines results with confidence scores
6. **Tracing** → LangFuse records everything

### Key Differentiators:

✅ **Smart Routing** - Not all queries need both agents  
✅ **Performance** - Single-agent queries are 2x faster  
✅ **Accuracy** - Confidence scoring reflects data source certainty  
✅ **Observability** - Full trace of agent decision-making  
✅ **Scalability** - Easy to add more specialized agents  

---

## Implementation Details

### Agent Execution Flow:

```
User Query
    ↓
Orchestrator (Main Coordinator)
    ├─ Intent Detection (keyword analysis)
    ├─ Risk Assessment (low/medium/high)
    ├─ Route Decision (rag/sql/hybrid)
    ↓
Based on Route:
    ├─ RAG: Semantic search on PDFs
    ├─ SQL: Text-to-SQL on database
    └─ HYBRID: Parallel execution of both
    ↓
Confidence Scoring
    └─ 4-factor model: source quality, relevance, consistency, timeliness
    ↓
Response with Full Trace
    └─ agents_used, agent_details, confidence, sources, SLO metrics
```

### Code Changes Made:

1. **API Response** - Added `agents_used` and `agent_details` fields
2. **Orchestrator** - Tracks which agents were invoked + execution time
3. **Agent Handlers** - Return execution metadata (latency, status, confidence)
4. **Observability** - New `/demo-agents` endpoint + agent routing stats
5. **LangFuse Integration** - `@observe` decorators on all agent calls

---

## For Presentations

### Slide 1: System Architecture
- Show the diagram above with Orchestrator → Agents
- Highlight that it's not just RAG retrieval
- Show 3 agent types: RAG, SQL, Hybrid

### Slide 2: Demo Results
- Show LangFuse trace screenshot
- Show agent_details in API response
- Highlight latency and confidence scores

### Slide 3: Query Routing Intelligence
- Show table of query types → agent selection
- Emphasize smart routing (not all queries need hybrid)
- Show efficiency stats

### Slide 4: Observability
- Show `/api/observability` response
- Agent call distribution
- SLO compliance tracking

---

## Quick Checklist for Demo

- [ ] Start FastAPI server: `python -m uvicorn app.main:app --reload`
- [ ] Get auth token: `curl http://localhost:8000/api/token`
- [ ] Test RAG query and show `agent_details`
- [ ] Test SQL query and show agent routing
- [ ] Test Hybrid query and show both agents
- [ ] (Optional) Show LangFuse dashboard with traces
- [ ] Show `/api/observability/demo-agents` endpoint
- [ ] Show `/api/observability` stats

---

## Troubleshooting

### Agents not showing in response?
- Check that `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set
- Verify orchestrator.py returns `agents_used` and `agent_details`

### LangFuse not capturing traces?
- Verify credentials in `.env`
- Check that `@trace_function` decorators are on agent methods
- Restart server after adding env vars

### Query routing not working?
- Check `_detect_intent()` in orchestrator.py for keyword logic
- Verify keywords in config are loaded correctly
- Check logs for routing decision

---

## Next Steps to Enhance

1. **Add more specialized agents** - Document Agent, Compliance Agent, etc.
2. **Implement agent feedback loop** - Learn which agent combos work best
3. **Add tool use** - Give agents ability to call external APIs
4. **Implement agent memory** - Cross-query context awareness
5. **Create custom agent types** - Industry-specific agents

---

## Questions for Stakeholders

1. "How would you rate the intelligence of our routing system? Does it correctly choose which agent to use?"
2. "Are there query types we're not handling well with current agents?"
3. "Would you like us to add more specialized agents for other domains?"
4. "Is the multi-agent approach meeting your latency and accuracy requirements?"

