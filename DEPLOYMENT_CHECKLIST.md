# Deployment Checklist

## Pre-Deployment Verification

### Backend Setup
- [x] UUID-utils dependency installed
- [x] RAG pipeline retrieves from PDF documents
- [x] Answers include source citations
- [x] Confidence scores properly calculated
- [x] Risk assessment working
- [x] Error handling with graceful fallback
- [x] CORS enabled for frontend
- [x] Rate limiting configured
- [x] Cost tracking active
- [x] Authentication implemented

### Frontend Setup
- [x] Next.js configured
- [x] API URL configured to backend
- [x] Policy Explorer page ready
- [x] Query submission form working
- [x] Response display formatting ready
- [x] Environment variables set

### Database Setup
- [x] PostgreSQL with pgvector extension
- [x] Policy documents indexed (36 chunks from 7 PDFs)
- [x] Embeddings calculated and stored
- [x] Vector similarity search working

### Documentation
- [x] BACKEND_FIX_SUMMARY.md created
- [x] FIX_COMPLETE.txt created
- [x] FRONTEND_INTEGRATION_GUIDE.md created
- [x] This DEPLOYMENT_CHECKLIST.md created

---

## Local Testing Checklist

### Test 1: Backend Health
```bash
cd RetailPolicyAssistant
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 3
curl http://localhost:8000/health
```
**Expected:** HTTP 200 with healthy status

- [ ] Health check passes
- [ ] Server responds quickly

### Test 2: Document Retrieval
```bash
curl http://localhost:8000/token -s | jq -r .access_token > token.txt
TOKEN=$(cat token.txt)
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our data retention policy?"}' \
  -s | jq .sources
```
**Expected:** List of document sources from PDFs

- [ ] Sources returned
- [ ] Document names visible
- [ ] Page numbers included

### Test 3: Answer Quality
```bash
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our data retention policy?"}' \
  -s | jq '.result.result' | head -c 300
```
**Expected:** Actual policy text from Data_Retention_and_Archival_Policy.pdf

- [ ] Answer contains PDF document names
- [ ] Answer contains relevant policy content
- [ ] No error messages in answer

### Test 4: All Test Queries Pass
Run all 5 test queries from FRONTEND_INTEGRATION_GUIDE.md:

- [ ] Test Case 1: Data Retention Query
- [ ] Test Case 2: GDPR Compliance Query
- [ ] Test Case 3: Security Query
- [ ] Test Case 4: Vendor Query
- [ ] Test Case 5: Anti-Bribery Query

### Test 5: Frontend Integration
```bash
cd frontend-nextjs
npm run dev &
# Open http://localhost:3000
```
**Expected:** Frontend loads and connects to backend

- [ ] Frontend starts without errors
- [ ] Page loads in browser
- [ ] Can submit queries
- [ ] Responses display correctly
- [ ] Sources show PDF names

---

## Staging Deployment

### Database Preparation
```bash
# Verify PostgreSQL is running
psql -U postgres -d retail_policy -c "SELECT count(*) FROM policy_documents;"
```
- [ ] Database accessible
- [ ] 36+ documents indexed
- [ ] Embeddings calculated

### Backend Deployment
```bash
# Install dependencies
cd RetailPolicyAssistant
pip install -r requirements.txt

# Verify uuid-utils is installed
pip list | grep uuid-utils
```
**Expected:** uuid-utils version shown

- [ ] All dependencies installed
- [ ] uuid-utils present
- [ ] No conflicts

### Backend Startup
```bash
# Run on staging server
python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```
- [ ] Starts without errors
- [ ] Health check passes
- [ ] Database connection works
- [ ] LLM connection working (or fallback used)

### Frontend Deployment
```bash
cd frontend-nextjs
# Build for production
npm run build

# Start production server
npm start
```
- [ ] Build completes without errors
- [ ] Server starts
- [ ] Frontend accessible
- [ ] API requests succeed

### Monitoring Setup
- [ ] Logging configured
- [ ] Metrics collection active
- [ ] Alerts configured
- [ ] Health checks scheduled

---

## Production Deployment

### Pre-Production Approval
- [ ] Tech lead review completed
- [ ] Security review completed
- [ ] Performance testing passed
- [ ] User acceptance testing passed

### Production Infrastructure
- [ ] Production database provisioned
- [ ] Database backups configured
- [ ] SSL/TLS certificates installed
- [ ] Load balancer configured
- [ ] DNS updated
- [ ] CDN configured (if needed)

### Production Deployment
```bash
# On production servers

# 1. Backend
cd /opt/retail-policy/backend
git pull origin main
pip install -r requirements.txt
systemctl restart retail-policy-api

# 2. Frontend  
cd /opt/retail-policy/frontend
git pull origin main
npm install --production
npm run build
systemctl restart retail-policy-web

# 3. Verify
curl https://api.retailpolicy.com/health
curl https://retailpolicy.com/
```

### Post-Deployment Verification
- [ ] Health checks passing
- [ ] Metrics showing normal patterns
- [ ] No error logs
- [ ] Users can submit queries
- [ ] Responses include PDF sources
- [ ] Database performing normally

### Monitoring & Alerting
- [ ] Error rate < 0.1%
- [ ] Latency < 5 seconds (p95)
- [ ] Confidence scores > 0.7
- [ ] No uuid-utils errors
- [ ] Database connections healthy

---

## Rollback Plan

### If Backend Fails
```bash
# Revert to previous version
cd RetailPolicyAssistant
git revert <commit-hash>
python -m uvicorn app.main:app --reload

# Or restore from backup
systemctl stop retail-policy-api
pg_restore -d retail_policy backup.sql
systemctl start retail-policy-api
```

### If Frontend Fails
```bash
cd frontend-nextjs
git revert <commit-hash>
npm install
npm run build
systemctl restart retail-policy-web
```

### Communication
- [ ] Notify stakeholders
- [ ] Create incident ticket
- [ ] Document root cause
- [ ] Update status page

---

## Post-Deployment Tasks

### Documentation
- [ ] Update user guides
- [ ] Document new features
- [ ] Create troubleshooting guide
- [ ] Update API documentation

### Training
- [ ] Train support team
- [ ] Create training videos
- [ ] Document common issues
- [ ] Set up FAQ

### Optimization
- [ ] Monitor query latency
- [ ] Identify slow queries
- [ ] Optimize indexes if needed
- [ ] Review cost tracking

### Maintenance
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Set up monitoring dashboards
- [ ] Schedule regular reviews

---

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@host/retail_policy

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# API Configuration  
API_HOST=0.0.0.0
API_PORT=8000

# Authentication
SECRET_KEY=your-secret-key-here

# Cost Tracking
MONTHLY_BUDGET_USD=1000
COST_PER_1K_EMBEDDING=0.002
COST_PER_1K_COMPLETION=0.001

# Features
ENABLE_RATE_LIMITING=true
ENABLE_COST_TRACKING=true
ENABLE_LANGFUSE=true
```

### Frontend (.env.production)
```env
NEXT_PUBLIC_API_URL=https://api.retailpolicy.com
```

---

## Dependency Versions

Critical dependencies that must be maintained:

```
langchain>=1.0.0
langchain-core>=1.4.0
uuid-utils>=0.15.0
pgvector>=0.3.0
fastapi>=0.100.0
uvicorn>=0.23.0
```

---

## Success Criteria

### Functionality
- [x] All queries return HTTP 200 responses
- [x] Answers come from PDF documents (not just fallback)
- [x] Sources include document names and page numbers
- [x] Confidence scores reflect answer quality
- [x] Risk levels properly assessed
- [x] Error handling works without crashes

### Performance
- [ ] Average query latency < 3 seconds
- [ ] p95 latency < 5 seconds
- [ ] SLO: 99% of queries complete within target
- [ ] Database query time < 1 second

### Reliability
- [ ] Error rate < 0.1%
- [ ] No crashes in 48-hour test period
- [ ] Graceful fallback when LLM unavailable
- [ ] Database connections stable

### User Experience
- [ ] Frontend loads quickly
- [ ] Responses display properly
- [ ] Sources are readable
- [ ] Error messages are helpful

---

## Sign-Off

- [ ] Backend Lead: _________________ Date: _______
- [ ] Frontend Lead: _________________ Date: _______
- [ ] DevOps Lead: _________________ Date: _______
- [ ] QA Lead: _________________ Date: _______
- [ ] Product Lead: _________________ Date: _______

---

## Notes

```
[Space for additional notes, issues discovered, or changes made]
```

