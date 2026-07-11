# Swagger Testing Guide: Multi-Agent System Demo

## 📋 Step-by-Step Instructions to Test in Swagger

---

## STEP 1: Start Your FastAPI Server

```bash
cd c:\Users\Anagha.e\project\RetailPolicy_Intelligence_Decision_Support_System\RetailPolicyAssistant

python -m uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

---

## STEP 2: Open Swagger UI

Open your browser and go to:

```
http://localhost:8000/docs
```

**You should see:**
- FastAPI Swagger interface
- List of all available endpoints
- Green "GET", "POST" buttons

---

## STEP 3: Get Demo Token (First!)

### **In Swagger:**

1. **Look for** the `GET /api/token` endpoint (scroll down to find it)
   
2. **Click the green "GET /api/token" button**

3. **Click "Try it out"** button

4. **Click "Execute"** button

**You should see:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

5. **COPY the entire access_token value** (it's a long string)

---

## STEP 4: Test RAG Agent (Policy Retrieval)

### **In Swagger:**

1. **Find** the `POST /api/ask` endpoint (blue POST button)

2. **Click "Try it out"** button

3. **You'll see two sections:**
   - Authorization (at top right)
   - Request body

### **First: Add Authorization Token**

4. **Click the padlock icon** 🔒 at the top right of Swagger
   - Or look for "Authorize" button

5. **Paste your token** in the "Value" field:
   ```
   eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```

6. **Click "Authorize"** button

7. **Close the dialog**

### **Now: Enter Your First Query**

8. **In the Request body field**, enter:

```json
{
  "query": "What is the data retention policy?"
}
```

9. **Click "Execute"** button

### **Check the Response:**

Look for `agents_used` and `agent_details`:

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
  "sources": ["Data Retention Policy.pdf"],
  "latency_seconds": 0.245,
  ...
}
```

**✅ What this proves:**
- RAG Agent was called
- It executed successfully
- Latency: 245ms
- Confidence: 0.92 (high, because from PDF)
- Source: PDF Documents

---

## STEP 5: Test SQL Agent (Database Query)

### **In Swagger:**

1. **Scroll down** to find `POST /api/ask` again (or look at your browser history)

2. **Click "Try it out"** button

3. **In the Request body**, CHANGE the query to:

```json
{
  "query": "How many vendors do we have?"
}
```

4. **Click "Execute"** button

### **Check the Response:**

Look for different `agents_used`:

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
  "sources": ["Database"],
  "latency_seconds": 0.189,
  ...
}
```

**✅ What this proves:**
- SQL Agent was called (not RAG)
- Different agent was selected automatically
- Latency: 189ms (faster than RAG)
- Confidence: 0.85 (good, because from database)
- Source: Database

---

## STEP 6: Test Hybrid Mode (Both Agents)

### **In Swagger:**

1. **Find `POST /api/ask` again**

2. **Click "Try it out"** button

3. **In the Request body**, CHANGE to:

```json
{
  "query": "Which vendors comply with our encryption policy?"
}
```

4. **Click "Execute"** button

### **Check the Response:**

Look for **BOTH agents** in `agents_used`:

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
  "sources": ["Encryption Policy.pdf", "Database"],
  "latency_seconds": 0.434,
  ...
}
```

**✅ What this proves:**
- BOTH agents were called (hybrid mode)
- RAG Agent answered policy part
- SQL Agent answered vendor part
- Combined confidence: 0.88 (average of 0.92 and 0.85)
- Both sources in response
- Total latency: 434ms (they ran in parallel)

---

## STEP 7: View Demo Endpoint (Educational)

### **In Swagger:**

1. **Look for `GET /api/observability/demo-agents`**

2. **Click "Try it out"** button

3. **Click "Execute"** button

### **Check the Response:**

You'll see documentation showing:
- How each agent works
- Example trigger queries
- Routing logic
- How to test

**This is educational reference material about your multi-agent system.**

---

## STEP 8: View Observability Statistics

### **In Swagger:**

1. **Look for `GET /api/observability`**

2. **Click "Try it out"** button

3. **Click "Execute"** button

### **Check the Response (scroll down to find):**

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

**✅ What this proves:**
- Total agent calls tracked: 100
- RAG Agent used: 42 times
- SQL Agent used: 38 times
- Hybrid mode used: 20 times (for complex queries)
- 80% single-agent (efficient)
- 20% hybrid (comprehensive)

---

## 📊 Summary: What You See in Swagger

### **For Each Query Response, Look For:**

#### **Field 1: agents_used**
```json
"agents_used": ["rag_agent"]           // Single agent
// OR
"agents_used": ["sql_agent"]           // Single agent
// OR
"agents_used": ["rag_agent", "sql_agent"]  // Both agents (hybrid)
```

#### **Field 2: agent_details (The Key Proof!)**
```json
"agent_details": [
  {
    "agent_name": "RAG Agent",         // Which agent
    "status": "success",               // Did it work?
    "latency_ms": 245.3,               // How fast?
    "confidence": 0.92,                // How confident?
    "data_source": "PDF Documents"     // Where from?
  }
]
```

#### **Field 3: route**
```json
"route": "rag"        // or "sql" or "hybrid"
```

#### **Field 4: confidence_score**
```json
"confidence_score": 0.92   // Overall confidence
```

#### **Field 5: sources**
```json
"sources": ["Data Retention Policy.pdf", "Database"]
```

---

## 🎯 Quick Test Checklist

Use this checklist when testing in Swagger:

### **Test 1: RAG Query**
- [ ] Go to POST /api/ask
- [ ] Enter query: "What is the data retention policy?"
- [ ] Execute
- [ ] Check: `agents_used` = ["rag_agent"]
- [ ] Check: `route` = "rag"
- [ ] Check: `confidence_score` ≈ 0.92
- [ ] Check: `sources` contains PDF

### **Test 2: SQL Query**
- [ ] Go to POST /api/ask
- [ ] Enter query: "How many vendors do we have?"
- [ ] Execute
- [ ] Check: `agents_used` = ["sql_agent"]
- [ ] Check: `route` = "sql"
- [ ] Check: `confidence_score` ≈ 0.85
- [ ] Check: `sources` = ["Database"]

### **Test 3: Hybrid Query**
- [ ] Go to POST /api/ask
- [ ] Enter query: "Which vendors comply with our encryption policy?"
- [ ] Execute
- [ ] Check: `agents_used` = ["rag_agent", "sql_agent"]
- [ ] Check: `route` = "hybrid"
- [ ] Check: `confidence_score` ≈ 0.88
- [ ] Check: `sources` contains both PDF and Database
- [ ] Check: `latency_seconds` > 400ms (parallel execution)

### **Test 4: Observability**
- [ ] Go to GET /api/observability
- [ ] Execute
- [ ] Check: `multi_agent_summary` exists
- [ ] Check: `agent_routing_efficiency` shows 80% single-agent

### **Test 5: Demo Endpoint**
- [ ] Go to GET /api/observability/demo-agents
- [ ] Execute
- [ ] Check: Explains all 3 agent types
- [ ] Check: Shows example queries

---

## 🔍 Finding Endpoints in Swagger

**All endpoints are organized by tags. Here's where to find them:**

```
POST /api/ask                              ← Main endpoint (find under "api")
GET  /api/token                            ← Get token (find under "api")
GET  /api/observability                    ← Stats (find under "observability")
GET  /api/observability/demo-agents        ← Demo info (find under "observability")
```

**Scroll down in Swagger to find all endpoints.**

---

## 💡 What Each Response Field Means

| Field | Meaning | Example |
|-------|---------|---------|
| `agents_used` | Which agents answered | ["rag_agent"] |
| `agent_details` | Execution details | [{agent_name, latency, confidence}] |
| `route` | Type of routing | "rag" or "sql" or "hybrid" |
| `confidence_score` | How sure we are | 0.92 |
| `sources` | Where answer came from | ["PDF", "Database"] |
| `latency_seconds` | How long it took | 0.245 |
| `result` | The actual answer | "Data retention policy says..." |

---

## ⚠️ Common Issues & Solutions

### **Issue 1: "Cannot find Authorize button"**
**Solution:** Look for 🔒 lock icon at top right of Swagger, click it

### **Issue 2: "Token keeps expiring"**
**Solution:** Get a fresh token every time from `/api/token`

### **Issue 3: "agents_used is empty"**
**Solution:** This means there's a bug. Check that app/api.py includes it in AskResponse

### **Issue 4: "Can't see agent_details in response"**
**Solution:** Scroll down in the response JSON, it's there

### **Issue 5: "All queries show same agent"**
**Solution:** Try different queries. RAG: "policy", SQL: "how many", Hybrid: "policy + vendor"

---

## 🎬 Live Demo Flow (Recommended)

### **Time: 5 minutes**

**Minute 1: Show Swagger**
- Open http://localhost:8000/docs in browser
- Point out the 3 agent endpoints

**Minute 2: Get Token**
- Call GET /api/token
- Copy token (don't show the full value to audience)

**Minute 3: Test RAG**
- Call POST /api/ask with policy question
- Show agents_used = ["rag_agent"]
- Show confidence_score = 0.92

**Minute 4: Test SQL**
- Call POST /api/ask with vendor count question
- Show agents_used = ["sql_agent"]
- Show different confidence_score = 0.85

**Minute 5: Test Hybrid**
- Call POST /api/ask with vendor + policy question
- Show agents_used = ["rag_agent", "sql_agent"]
- Show combined confidence_score = 0.88

**Conclusion:** "As you can see, the system intelligently chose which agents to use for each query type."

---

## 📸 Screenshots to Take

For your presentation, take screenshots of:

1. **Swagger UI with /api/ask endpoint open**
2. **RAG Query response** (showing agents_used: ["rag_agent"])
3. **SQL Query response** (showing agents_used: ["sql_agent"])
4. **Hybrid Query response** (showing both agents)
5. **Observability response** (showing agent statistics)

These screenshots prove your multi-agent system visually.

---

## ✨ Pro Tips

### **Tip 1: Save Test Queries**
Keep these queries handy:
```
RAG: "What is the data retention policy?"
SQL: "How many vendors do we have?"
Hybrid: "Which vendors comply with our encryption policy?"
```

### **Tip 2: Explain agents_used**
"Notice `agents_used` shows which agent answered this query. RAG for policies, SQL for data, both for complex questions."

### **Tip 3: Highlight Confidence Scores**
"Each agent has different confidence levels. RAG is 0.92 (from PDFs), SQL is 0.85 (from database). We tell users where their answer came from."

### **Tip 4: Show Routing Efficiency**
"80% of queries use single agent (fast), 20% use hybrid mode when needed. Smart routing."

### **Tip 5: Explain agent_details**
"This shows latency per agent. RAG: 245ms, SQL: 189ms, Hybrid: 434ms (parallel). This is observability."

---

## 🎓 What to Tell Your Audience

**When showing RAG response:**
"This is the RAG Agent answering from PDF documents. High confidence (0.92) because we're pulling directly from policy PDFs."

**When showing SQL response:**
"This is the SQL Agent querying the database. Different confidence (0.85) because it's database accuracy, not document match."

**When showing Hybrid response:**
"This is the interesting one. The system detected it needed BOTH policy context AND vendor data, so it called both agents in parallel. Combined confidence is 0.88."

**When showing observability:**
"We track every agent call. This shows 80% single-agent (efficient), 20% hybrid (complex). This is how we monitor the system."

---

## 🚀 You're Ready!

You now know how to:
✅ Access Swagger  
✅ Get authorization token  
✅ Test all 3 agent types  
✅ Find agents_used and agent_details in responses  
✅ Explain what each field means  
✅ Demo the system live  

**Good luck with your capstone presentation! 🎓**

