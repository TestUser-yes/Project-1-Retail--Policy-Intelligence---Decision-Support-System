# How to Check Multi-Agent Retrieval in Swagger: Step-by-Step

## 🎯 Goal
Verify that your RAG pipeline uses multi-agent retrieval by checking API responses in Swagger

---

## ⚡ QUICK START (2 minutes)

### Step 1: Start Server
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

### Step 2: Open Swagger
Open in browser:
```
http://localhost:8000/docs
```

You should see the **FastAPI Swagger UI** with all endpoints listed

---

### Step 3: Get Token
1. **Scroll down** to find `GET /api/token`

2. **Click the green "GET" button**
   ```
   GET /api/token
   ```

3. **Click "Try it out"** button

4. **Click "Execute"** button

5. **Copy the access_token** (the long string in the response)
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "token_type": "bearer"
   }
   ```

---

### Step 4: Authorize
1. **Find the 🔒 Lock icon** at the top right of Swagger

2. **Click it**

3. **Paste your token** in the "Value" field

4. **Click "Authorize"** button

5. **Close the dialog**

---

### Step 5: Test RAG Query with Multi-Agent Retrieval

1. **Find `POST /api/ask`** (blue POST button)

2. **Click "Try it out"**

3. **Enter this query** in the Request body:
```json
{
  "query": "What is the data retention policy?"
}
```

4. **Click "Execute"**

5. **Wait for response** (should be 2-3 seconds)

---

### Step 6: Find Multi-Agent Proof

**Scroll down** in the response and look for this:

```json
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
    "top_k": 6
  },
  "keyword_agent": {
    "agent": "keyword_retrieval_agent",
    "method": "keyword_matching",
    "keywords": ["data", "retention", "policy"],
    "documents_retrieved": 6,
    "top_k": 6
  },
  "ranking_agent": {
    "agent": "ranking_agent",
    "method": "multi_agent_fusion",
    "semantic_weight": 0.6,
    "keyword_weight": 0.4,
    "documents_fused": 10,
    "final_documents": 6,
    "consensus_boost_applied": true,
    "scored_results": [
      {
        "document_name": "Data Retention Policy.pdf",
        "final_score": 1.04,
        "semantic_score": 1.0,
        "keyword_score": 0.83,
        "appearances": 2
      }
    ]
  },
  "total_agents": 3
}
```

✅ **THIS IS YOUR PROOF OF MULTI-AGENT RETRIEVAL!**

---

## 📋 Detailed Step-by-Step with Screenshots

### Step 1: Start Server (1 minute)

**Open Terminal/Command Prompt:**

```bash
cd c:\Users\Anagha.e\project\RetailPolicy_Intelligence_Decision_Support_System\RetailPolicyAssistant
```

**Run server:**
```bash
python -m uvicorn app.main:app --reload
```

**You should see:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

✅ **Server is running**

---

### Step 2: Open Swagger (30 seconds)

**Open any browser** (Chrome, Firefox, Edge, Safari)

**Go to:**
```
http://localhost:8000/docs
```

**You should see:**
```
╔════════════════════════════════════════╗
║   Retail Policy AI                     ║
║   Swagger UI - Try API endpoints       ║
║                                        ║
║ GET /api/health                        ║
║ GET /api/token                 ← FIND THIS
║ POST /api/ask                  ← AND THIS
║ GET /api/conversations/...             ║
║ GET /api/observability                 ║
║ GET /api/observability/demo-agents     ║
║ (more endpoints below)                 ║
╚════════════════════════════════════════╝
```

✅ **Swagger UI is open**

---

### Step 3: Get Authorization Token (1 minute)

**In Swagger, find:**
```
GET /api/token
```

**Location:** Scroll down a bit in Swagger, you'll see a green button with "GET"

**Click:** The green "GET /api/token" button

**You should see:**
```
┌─────────────────────────────────────┐
│ GET /api/token                      │
│ └─ Authentication token endpoint    │
│                                     │
│ [ Try it out ]  [ Cancel ]          │
│                                     │
│ [ Execute ]  [ Clear ]              │
└─────────────────────────────────────┘
```

**Click:** "Try it out" button

**Then click:** "Execute" button

**Wait** for response (1-2 seconds)

**You should see response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZW1vIiwiaWF0IjoxNjg5OTk5OTk5LCJleHAiOjE2OTAwMDAwMDB9.XXXXXXXXXXXX",
  "token_type": "bearer"
}
```

**Copy the entire `access_token` value** (the very long string starting with "eyJ0...")

✅ **You have your token**

---

### Step 4: Set Authorization in Swagger (1 minute)

**In Swagger, look at the TOP RIGHT corner:**

```
┌──────────────────────────────────────────┐
│ Servers    Swagger UI    Docs    [v]     │
│                                          │
│ ┌────────────────────────────────────┐   │
│ │  🔒 Authorize                      │   │ ← CLICK HERE
│ └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

**Click the 🔒 Authorize button** (or look for lock icon)

**A dialog box will appear:**
```
┌──────────────────────────────────────────┐
│ Available authorizations                 │
├──────────────────────────────────────────┤
│                                          │
│ HTTPBearer                               │
│                                          │
│ Value:                                   │
│ ┌──────────────────────────────────────┐ │
│ │ [Paste your token here]              │ │
│ │ eyJ0eXAiOiJKV1QiLCJhb...             │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ [ Authorize ]   [ Cancel ]               │
└──────────────────────────────────────────┘
```

**Paste your token** in the Value field

**Click:** "Authorize" button

**Then click:** "Close" or just click outside the dialog

✅ **You are now authorized**

---

### Step 5: Make RAG Query (30 seconds)

**Scroll down** in Swagger to find:
```
POST /api/ask
```

**It's a blue button** that says "POST"

**Click:** "Try it out" button

**You should see:**
```
┌─────────────────────────────────────────┐
│ POST /api/ask                           │
│ Ask a policy question                   │
│                                         │
│ [ Try it out ]  [ Cancel ]              │
│                                         │
│ Request body:                           │
│ ┌─────────────────────────────────────┐ │
│ │ {                                   │ │
│ │   "query": "string"                 │ │
│ │   "conversation_id": "string"       │ │
│ │ }                                   │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Delete the default content** and type:
```json
{
  "query": "What is the data retention policy?"
}
```

**Your screen should look like:**
```
┌─────────────────────────────────────────┐
│ Request body:                           │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ {                                   │ │
│ │   "query": "What is the data       │ │
│ │   retention policy?"                │ │
│ │ }                                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [ Execute ]                             │
└─────────────────────────────────────────┘
```

**Click:** "Execute" button

**Wait** for response (2-3 seconds)

✅ **Query submitted**

---

### Step 6: Check Multi-Agent Proof (1 minute)

After clicking Execute, **scroll down** to see the response

**Look for this section** (might be long, so scroll A LOT):

```json
{
  "query": "What is the data retention policy?",
  "route": "rag",
  "agents_used": ["rag_agent"],
  
  "result": {
    "result": "Data retention policy requires..."
  },
  
  "retrieval_method": "multi_agent",     ← KEY FIELD 1
  
  "retrieval_agents": [                  ← KEY FIELD 2
    "semantic_retrieval_agent",
    "keyword_retrieval_agent",
    "ranking_agent"
  ],
  
  "retrieval_pipeline": {                ← KEY FIELD 3 (MOST IMPORTANT)
    "semantic_agent": {
      "agent": "semantic_retrieval_agent",
      "method": "embedding_similarity",
      "documents_retrieved": 6,
      "top_k": 6
    },
    
    "keyword_agent": {
      "agent": "keyword_retrieval_agent",
      "method": "keyword_matching",
      "keywords": ["data", "retention", "policy"],
      "documents_retrieved": 6,
      "top_k": 6
    },
    
    "ranking_agent": {
      "agent": "ranking_agent",
      "method": "multi_agent_fusion",
      "semantic_weight": 0.6,
      "keyword_weight": 0.4,
      "documents_fused": 10,
      "final_documents": 6,
      "consensus_boost_applied": true,
      "scored_results": [
        {
          "document_name": "Data Retention Policy.pdf",
          "final_score": 1.04,
          "semantic_score": 1.0,
          "keyword_score": 0.83,
          "appearances": 2
        },
        {
          "document_name": "Compliance Policy.pdf",
          "final_score": 0.92,
          "semantic_score": 0.85,
          "keyword_score": 0.88,
          "appearances": 2
        },
        ...
      ]
    },
    
    "total_agents": 3                    ← THIS PROVES MULTI-AGENT!
  },
  
  "confidence_score": 0.92,
  "sources": [...],
  ...
}
```

✅ **Multi-Agent Retrieval is working!**

---

## 🎯 What to Look For

### Key Indicators of Multi-Agent Retrieval:

**1. Check `retrieval_method`:**
```json
"retrieval_method": "multi_agent"  ✅ Correct
"retrieval_method": "semantic"     ❌ Wrong (fallback)
```

**2. Check `retrieval_agents` array:**
```json
"retrieval_agents": [
  "semantic_retrieval_agent",
  "keyword_retrieval_agent",
  "ranking_agent"
]
```
✅ All 3 agents should be present

**3. Check `retrieval_pipeline` structure:**
```json
"retrieval_pipeline": {
  "semantic_agent": {...},
  "keyword_agent": {...},
  "ranking_agent": {...},
  "total_agents": 3  ✅ PROOF!
}
```

**4. Verify agent execution details:**
```json
"semantic_agent": {
  "documents_retrieved": 6,
  "method": "embedding_similarity"
}

"keyword_agent": {
  "documents_retrieved": 6,
  "keywords": ["data", "retention", "policy"],
  "method": "keyword_matching"
}

"ranking_agent": {
  "documents_fused": 10,
  "final_documents": 6,
  "consensus_boost_applied": true
}
```

**5. Check consensus boost results:**
```json
"scored_results": [
  {
    "document_name": "Data Retention Policy.pdf",
    "final_score": 1.04,
    "appearances": 2  ✅ Found by 2 agents = boosted!
  }
]
```

---

## 📊 Sample Responses

### Response 1: Successful Multi-Agent Retrieval

**Query:** `"What is the data retention policy?"`

**Expected Response (key parts):**
```json
{
  "retrieval_method": "multi_agent",
  "retrieval_agents": [
    "semantic_retrieval_agent",
    "keyword_retrieval_agent",
    "ranking_agent"
  ],
  "retrieval_pipeline": {
    "semantic_agent": {
      "documents_retrieved": 6
    },
    "keyword_agent": {
      "documents_retrieved": 6,
      "keywords": ["data", "retention", "policy"]
    },
    "ranking_agent": {
      "documents_fused": 10,
      "consensus_boost_applied": true,
      "total_agents": 3
    }
  }
}
```

✅ **This is correct!**

---

### Response 2: Check Scoring Details

**In `scored_results`, you should see:**

```json
{
  "document_name": "Data Retention Policy.pdf",
  "final_score": 1.04,
  "semantic_score": 1.0,      ← RAG Agent found it
  "keyword_score": 0.83,      ← SQL Agent found it
  "appearances": 2            ← Both found it = BOOSTED!
}
```

**vs**

```json
{
  "document_name": "Other Policy.pdf",
  "final_score": 0.60,
  "semantic_score": 0.5,
  "keyword_score": 0.0,       ← Only semantic found it
  "appearances": 1            ← Single agent = no boost
}
```

✅ **Documents found by both agents have higher scores!**

---

## 🧪 Try Different Queries

### Query 1: Policy Terminology
```json
{"query": "GDPR compliance requirements"}
```

**Expected:**
- Keyword agent finds "GDPR" exact match
- Semantic agent finds related concepts
- Both in scored_results

---

### Query 2: Complex Query
```json
{"query": "Which vendors comply with our data retention and encryption standards?"}
```

**Expected:**
- Many documents retrieved
- High consensus_boost_applied
- Documents with appearances: 2 ranked highest

---

### Query 3: Specific Policy
```json
{"query": "What is our incident response policy?"}
```

**Expected:**
- Semantic agent finds semantically similar docs
- Keyword agent finds "incident response" exact match
- Combined results better than single agent

---

## 🎬 Full Demo Flow (5 minutes)

**Minute 1: Setup**
- [ ] Start server
- [ ] Open Swagger
- [ ] Get token
- [ ] Authorize

**Minute 2: Make Query**
- [ ] Find POST /api/ask
- [ ] Click "Try it out"
- [ ] Enter query
- [ ] Click "Execute"

**Minute 3: Scroll and Find**
- [ ] Scroll down in response
- [ ] Find `retrieval_method: "multi_agent"`
- [ ] Find `retrieval_agents` array with 3 agents

**Minute 4: Show Details**
- [ ] Point to `retrieval_pipeline`
- [ ] Show `semantic_agent` details
- [ ] Show `keyword_agent` details
- [ ] Show `ranking_agent` details

**Minute 5: Prove Fusion**
- [ ] Show `documents_fused: 10+`
- [ ] Show `consensus_boost_applied: true`
- [ ] Show scored_results with `appearances: 2`
- [ ] Explain scoring logic

**Result: Multi-Agent Retrieval Proven!** ✅

---

## 🎤 What to Say

**To your committee:**

> "As you can see in the API response:
>
> 1. **retrieval_method** is set to 'multi_agent'
> 2. **retrieval_agents** shows 3 agents: semantic, keyword, ranking
> 3. **retrieval_pipeline** shows each agent's execution:
>    - Semantic Agent retrieved 6 documents using embeddings
>    - Keyword Agent retrieved 6 documents using keyword matching
>    - Ranking Agent fused 10 total documents into top 6 ranked results
>
> 4. **consensus_boost_applied** is true, meaning documents found by
>    both agents were ranked higher
>
> This demonstrates sophisticated multi-agent retrieval, not just simple RAG."

---

## ✅ Verification Checklist

After making the query, verify:

- [ ] Server started successfully
- [ ] Swagger UI opened
- [ ] Token obtained
- [ ] Authorization set
- [ ] Query executed
- [ ] Response contains `retrieval_method: "multi_agent"`
- [ ] Response contains all 3 agents in `retrieval_agents`
- [ ] `retrieval_pipeline` section present
- [ ] `semantic_agent` shows documents_retrieved > 0
- [ ] `keyword_agent` shows keywords extracted
- [ ] `keyword_agent` shows documents_retrieved > 0
- [ ] `ranking_agent` shows documents_fused > final_documents
- [ ] `ranking_agent` shows consensus_boost_applied: true
- [ ] `total_agents: 3` present
- [ ] `scored_results` array has entries
- [ ] Some entries have `appearances: 2`

**All checked?** ✅ **Multi-Agent Retrieval is working!**

---

## 🚀 You're Done!

You now know exactly how to:
1. Check multi-agent retrieval in Swagger
2. Verify all 3 agents are executing
3. Confirm result fusion is happening
4. Show proof to your capstone committee

**Go demonstrate your multi-agent system!** 🎉

