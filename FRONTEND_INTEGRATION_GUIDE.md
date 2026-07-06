# Frontend Integration Guide

## Status: READY FOR TESTING ✅

The backend is now **fully operational** with PDF-backed answers. The frontend can now submit queries and receive complete policy responses with:
- Semantic routing (RAG/SQL/Hybrid)
- Risk assessment
- Confidence scoring
- Source citations from PDF documents
- Cost tracking & SLO metrics

---

## Quick Start

### 1. Start the Backend (Terminal 1)
```bash
cd RetailPolicyAssistant
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 2. Start the Frontend (Terminal 2)
```bash
cd frontend-nextjs
npm run dev
```

Expected output:
```
  ▲ Next.js 15.1.3
  - Local:        http://localhost:3000
```

### 3. Test in Browser
- Open `http://localhost:3000`
- Navigate to **Policy Explorer** page
- Submit a test query: `"What is our data retention policy?"`

---

## Expected Behavior

### Query Submission
1. User enters query in the UI text box
2. Clicks "Submit Query" button

### Backend Processing
1. Query validated and classified
2. Documents retrieved from PDF database
3. Answer generated from relevant policies
4. Sources cited with document names and page numbers

### Response Display
```
Query: "What is our data retention policy?"

Answer:
Data Retention & Archival Policy

1. Purpose
   This policy defines the standards governing the retention, 
   archival, and secure disposal of enterprise data...

Metadata:
- Route: RAG (Policy Document)
- Risk Level: Low
- Confidence: 0.9 (90%)
- Escalate: No

Sources:
- Data_Retention_and_Archival_Policy.pdf (Page 1)
- GDPR_Selected_Articles.pdf (Page 4)
- Retail_Data_Protection_Privacy_Policy.pdf (Page 1)
```

---

## Test Plan

### Test Case 1: Basic RAG Query
**Query:** "What is our data retention policy for customer records?"
**Expected:**
- Route: RAG
- Confidence: 0.85-0.95
- Risk: Low
- Answer contains "Data Retention & Archival Policy"
- Sources: [Data_Retention_and_Archival_Policy.pdf]

### Test Case 2: Compliance Query
**Query:** "What are the GDPR compliance requirements?"
**Expected:**
- Route: RAG
- Confidence: 0.85-0.95
- Risk: High
- Answer contains "GDPR" or "Article"
- Sources: [GDPR_Selected_Articles.pdf]

### Test Case 3: Security Query
**Query:** "What are the information security access control requirements?"
**Expected:**
- Route: RAG
- Confidence: 0.85-0.95
- Risk: Medium-High
- Answer contains "access control" or "security"
- Sources: [Information_Security_Access_Control_Policy.pdf]

### Test Case 4: Vendor Query
**Query:** "What are our vendor compliance requirements?"
**Expected:**
- Route: RAG or Hybrid
- Confidence: 0.80-0.95
- Risk: Medium
- Answer contains "vendor" or "supplier"
- Sources: [Supplier_Vendor_Compliance_Policy.pdf]

### Test Case 5: Anti-Bribery Query
**Query:** "What is our anti-bribery policy?"
**Expected:**
- Route: RAG
- Confidence: 0.85-0.95
- Risk: High
- Answer contains "anti-bribery" or "ethical conduct"
- Sources: [Anti_Bribery_Ethical_Conduct_Policy.pdf]

---

## Response Structure

The API returns a complete response object:

```json
{
  "query": "What is our data retention policy?",
  "conversation_id": "unique-id-uuid",
  "intent": {
    "intent": "rag",
    "reason": "Query classified as rag"
  },
  "route": "rag",
  "result": {
    "result": "Full policy answer text from PDFs..."
  },
  "risk": {
    "risk_level": "low",
    "reason": "Routine policy query"
  },
  "escalate": false,
  "escalation_reason": "",
  "latency_seconds": 2.34,
  "cost_usd": 0.00245,
  "budget_remaining_usd": 999.75,
  "budget_percent_used": 0.025,
  "confidence_score": 0.92,
  "sources": [
    {
      "document": "Data_Retention_and_Archival_Policy.pdf",
      "page": 1,
      "section": ""
    },
    {
      "document": "GDPR_Selected_Articles.pdf",
      "page": 4,
      "section": ""
    }
  ],
  "slo_metrics": {
    "latency_ms": 2340,
    "target_latency_ms": 2000,
    "slo_status": "warning"
  }
}
```

---

## Configuration

### Backend Configuration
**File:** `RetailPolicyAssistant/.env`

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/retail_policy

# LLM - Ollama (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# API
API_HOST=127.0.0.1
API_PORT=8000

# Cost Tracking
MONTHLY_BUDGET_USD=1000
```

### Frontend Configuration
**File:** `frontend-nextjs/.env.development`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Issue: Backend connection refused
**Solution:**
```bash
# Ensure backend is running on port 8000
lsof -i :8000  # Check what's using port 8000
# Kill if needed: pkill -f "uvicorn"
```

### Issue: CORS errors
**Solution:** Backend has CORS enabled for all localhost ports 3000-3099

### Issue: No sources in response
**Solution:**
1. Verify PDFs are indexed: `python check_documents.py`
2. Check database connection
3. Restart backend to reload documents

### Issue: Low confidence scores
**Solution:**
- If <0.5: Documents may not be relevant to query
- Check golden set: `app/evaluation/golden_set.py`
- Verify document content matches query terms

### Issue: Slow responses (>5 seconds)
**Solution:**
- Check Ollama connection (if using external LLM)
- Monitor database queries
- Check system resources

---

## Features Verification

### ✅ Query Routing
- [x] RAG queries retrieve from PDF documents
- [x] SQL queries query vendor database
- [x] Hybrid queries combine both

### ✅ Risk Assessment
- [x] Low-risk routine queries
- [x] Medium-risk policy queries
- [x] High-risk compliance queries

### ✅ Confidence Scoring
- [x] High confidence (0.8+) for PDF-backed answers
- [x] Medium confidence (0.6-0.8) for partial matches
- [x] Low confidence (0.3-0.6) for fallback policies

### ✅ Source Citation
- [x] Document names included in answer
- [x] Page numbers provided
- [x] Sources array populated in response

### ✅ Error Handling
- [x] Graceful fallback when LLM unavailable
- [x] Proper error messages
- [x] No crashes on invalid queries

### ✅ Performance
- [x] Typical latency: 1.5-3 seconds
- [x] SLO tracking enabled
- [x] Cost calculation active

---

## Available PDF Documents

Your system has 7 policy documents indexed (36 total chunks):

1. **Data_Retention_and_Archival_Policy.pdf**
   - Retention periods for different data types
   - Archival procedures
   - Secure deletion

2. **GDPR_Selected_Articles.pdf**
   - GDPR compliance requirements
   - Data subject rights
   - Processing requirements

3. **Retail_Data_Protection_Privacy_Policy.pdf**
   - Privacy requirements for retail operations
   - Data handling procedures
   - Customer data protection

4. **Information_Security_Access_Control_Policy.pdf**
   - Access control requirements
   - Authentication standards
   - Audit logging

5. **ISO_27001_Access_Control_Summary.pdf**
   - ISO 27001 compliance guidelines
   - Access management best practices

6. **Anti_Bribery_Ethical_Conduct_Policy.pdf**
   - Anti-corruption requirements
   - Ethical conduct standards

7. **Supplier_Vendor_Compliance_Policy.pdf**
   - Vendor approval process
   - Compliance requirements
   - Risk assessment

---

## Next Steps

1. **Frontend Testing**
   - Test all 5 test cases listed above
   - Verify sources display correctly
   - Check confidence scores

2. **Browser Compatibility**
   - Test on Chrome, Firefox, Safari
   - Verify responsive design on mobile

3. **Performance Testing**
   - Measure latency
   - Monitor SLO compliance
   - Check cost tracking

4. **User Acceptance Testing**
   - Gather feedback from end users
   - Verify answer quality
   - Test edge cases

5. **Deployment Preparation**
   - Set up staging environment
   - Configure production database
   - Set up monitoring & logging

---

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "version": "1.0.0", ...}
```

### Token Generation
```bash
curl http://localhost:8000/token
# Returns: {"access_token": "...", "token_type": "bearer"}
```

### Query Testing
```bash
TOKEN=$(curl -s http://localhost:8000/token | jq -r .access_token)
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our data retention policy?"}' \
  | jq .confidence_score
# Should return: 0.9 or higher
```

---

## Support

For issues, check:
1. Backend logs: `RetailPolicyAssistant/logs/`
2. Frontend logs: Browser DevTools Console
3. Database status: `psql -l` to list databases
4. Document index: Query count from database

