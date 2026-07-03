# Quick Start: Demo Execution

**Time to demo:** 2-3 minutes

---

## Prerequisites
- Python 3.11+ with pip
- Node.js 18+ with npm
- Two terminal windows

---

## Step 1: Start Backend (Terminal 1)

```bash
cd RetailPolicyAssistant
pip install -r requirements.txt  # if needed
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Wait for:**
```
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```

---

## Step 2: Start Frontend (Terminal 2)

```bash
cd frontend
npm install  # if needed
npm run dev
```

**Wait for:**
```
Local:   http://localhost:5173/
```

---

## Step 3: Open Browser

Navigate to: **http://localhost:5173**

---

## Step 4: Test Auth Flow

### Query 1: Policy Question
```
Input: "What is our refund policy?"
Expected: Response shows policy information with confidence and risk level
```

### Query 2: Vendor Question  
```
Input: "Tell me about vendor costs"
Expected: Response shows vendor information and budget data
```

### Query 3: Verify Multi-turn
```
Input: "How does this affect compliance?"
Expected: System maintains context, reuses token, returns analysis
```

---

## What's Happening Behind the Scenes

1. **Frontend initialization**: Calls `GET /token` → receives JWT
2. **Token storage**: Stored in browser localStorage
3. **Query submission**: Includes `Authorization: Bearer <jwt>` header
4. **Backend validation**: Verifies JWT signature and expiration
5. **Query routing**: Classifies as RAG/SQL/Hybrid
6. **Response**: Returns intent, route, result, risk, escalate, latency

---

## Test Unauthorized Access (Optional)

In browser console:
```javascript
// This will fail with 401 Unauthorized
fetch('http://localhost:8000/ask', {
  method: 'POST',
  body: JSON.stringify({query: 'test'}),
  headers: {'Content-Type': 'application/json'}
})
```

Expected: `{"detail": "Invalid authentication credentials"}`

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
# Try: python -m uvicorn app.main:app --port 8001
```

### Frontend won't start (npm error with spaces in path)
```bash
# Use MSYS2 or Git Bash instead of Windows CMD
# Or use double quotes around path: cd "folder with spaces"
```

### Token getting 401
- Backend server down
- Token expired (30 min max)
- Refresh by visiting frontend home page (auto-retrieves new token)

---

## Demo Talking Points

- **Security**: JWT authentication required for all policy queries
- **Multi-turn**: System maintains context across conversation turns
- **Routing**: Intelligent classification - different handling for policy vs vendor queries
- **Risk**: Risk assessment and escalation ready for high-stakes queries
- **Performance**: Sub-millisecond response times for demo queries

---

## Advanced: Raw API Testing

```bash
# Get token
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')

# Use token
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is our refund policy?"}'
```

---

## Stopping the Demo

- Terminal 1: Ctrl+C
- Terminal 2: Ctrl+C
- Browser: Close tab

All data is in-memory (no state persisted for demo).
