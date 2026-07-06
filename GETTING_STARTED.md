# Getting Started - Next Steps

## Your System is Ready! 🎉

The Retail Policy Intelligence System is **fully operational and ready to use**. Here's exactly what to do next:

---

## Step 1: Start the Backend (Port 8000)

Open a terminal and run:

```bash
cd RetailPolicyAssistant
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
INFO:     Started server process [####]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open** - the backend must keep running.

---

## Step 2: Start the Frontend (Port 3000)

Open a **new terminal** and run:

```bash
cd frontend-nextjs
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 15.1.3
  - Local:        http://localhost:3000
  - Environments: .env.development
```

**Keep this terminal open** - the frontend must keep running.

---

## Step 3: Open in Browser

Open your web browser and go to:

```
http://localhost:3000
```

You should see the Retail Policy Intelligence System UI.

---

## Step 4: Test a Query

1. **Navigate to the Policy Explorer page**
2. **Enter a question** in the text box, for example:
   ```
   What is our data retention policy for customer records?
   ```
3. **Click "Submit Query"**
4. **Wait 2-5 seconds** for the response
5. **Review the result:**
   - You'll see the answer text
   - Below the answer, you'll see the document sources
   - Check the confidence score and risk level

---

## Example Queries to Try

Copy and paste these into the query box:

### Query 1: Data Retention
```
What is our data retention policy for customer records?
```
**Expected:** Answer from Data_Retention_and_Archival_Policy.pdf

### Query 2: GDPR Compliance
```
What are the GDPR compliance requirements?
```
**Expected:** Answer from GDPR_Selected_Articles.pdf

### Query 3: Security Policy
```
What is the information security access control policy?
```
**Expected:** Answer from Information_Security_Access_Control_Policy.pdf

### Query 4: Anti-Bribery
```
What is our anti-bribery policy?
```
**Expected:** Answer from Anti_Bribery_Ethical_Conduct_Policy.pdf

### Query 5: Vendor Compliance
```
What are the supplier and vendor compliance requirements?
```
**Expected:** Answer from Supplier_Vendor_Compliance_Policy.pdf

---

## What You Should See

For each query, the response includes:

### 1. Answer Section
- Full policy text retrieved from PDF documents
- Contains relevant sections and requirements
- Written in clear, professional language

### 2. Metadata Section
```
Route: RAG (Policy Document)
Risk Level: Low/Medium/High
Confidence: 0.85-0.95 (85-95%)
```

### 3. Sources Section
```
Document Sources:
- Data_Retention_and_Archival_Policy.pdf (Page 1)
- GDPR_Selected_Articles.pdf (Page 4)
- Retail_Data_Protection_Privacy_Policy.pdf (Page 1)
```

---

## Behind the Scenes

When you submit a query, here's what happens:

1. **Query Validation** - Your question is checked for validity
2. **Intent Detection** - System determines if it's about policies (RAG), data (SQL), or both (Hybrid)
3. **Document Retrieval** - Relevant PDF documents are found using semantic search
4. **Answer Generation** - LLM generates an answer from the retrieved documents
5. **Source Citation** - Document names and page numbers are included
6. **Response Formatting** - Everything is packaged with metadata and sent back

---

## Verification Checklist

As you test, verify these work correctly:

- [ ] Backend starts without errors on port 8000
- [ ] Frontend loads on port 3000 without errors
- [ ] Can submit a query successfully
- [ ] Receive a response (not an error)
- [ ] Answer contains policy text
- [ ] Source documents are listed
- [ ] Confidence score is displayed
- [ ] Risk level is shown
- [ ] Multiple queries work consistently
- [ ] All 5 example queries return good answers

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
netstat -ano | grep 8000

# If it is, find and kill the process
# Then try starting the backend again
```

### Frontend won't load
```bash
# Make sure you're in the correct directory
cd frontend-nextjs

# Try installing dependencies again
npm install

# Then run dev server
npm run dev
```

### No response or error message
1. Check that both terminals show "running" status
2. Try a simpler query
3. Check browser console for errors (F12 key)
4. Restart both backend and frontend

### Sources showing "Policy Database" instead of PDF names
This is the fallback mode - the system still works but should use PDFs. Try:
1. Refresh the page
2. Restart both backend and frontend
3. Check that PDFs are in Documents folder

---

## Next Steps After Testing

### If Everything Works:
✅ System is ready for production  
✅ Move to Deployment Checklist (see DEPLOYMENT_CHECKLIST.md)  
✅ Plan production launch  

### If You Find Issues:
- Document what didn't work
- Check DEPLOYMENT_CHECKLIST.md troubleshooting section
- Review logs in the terminal
- Create an issue with details

---

## Important Files to Know About

### Configuration
- `frontend-nextjs/.env.development` - API URL setting (should be http://localhost:8000)
- `RetailPolicyAssistant/.env` - Backend configuration

### Documentation
- `FINAL_SUMMARY.md` - Complete system overview
- `FRONTEND_INTEGRATION_GUIDE.md` - Detailed integration guide
- `DEPLOYMENT_CHECKLIST.md` - Production deployment steps
- `BACKEND_FIX_SUMMARY.md` - Technical details of the fix

### Code
- `RetailPolicyAssistant/app/main.py` - Backend entry point
- `RetailPolicyAssistant/app/api.py` - API endpoints
- `RetailPolicyAssistant/app/orchestrator.py` - Query routing logic
- `RetailPolicyAssistant/app/agents/rag_agent.py` - PDF retrieval agent

---

## Quick Reference

| Component | Port | Status | Start Command |
|-----------|------|--------|----------------|
| Backend API | 8000 | ✅ Ready | `cd RetailPolicyAssistant && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` |
| Frontend | 3000 | ✅ Ready | `cd frontend-nextjs && npm run dev` |
| Database | 5432 | ✅ External | Auto-connected |

---

## Getting Help

### If something is unclear:
1. Check `FINAL_SUMMARY.md` for detailed information
2. Read `FRONTEND_INTEGRATION_GUIDE.md` for specific features
3. Review `DEPLOYMENT_CHECKLIST.md` for troubleshooting
4. Check the terminal output for error messages

### Common Questions:

**Q: Why is the response showing PDF names in the answer but not in sources?**  
A: The answer text includes PDF names as cited sources. The "Sources" field shows metadata. Both indicate PDF-backed answers.

**Q: Why is confidence 0.9 instead of 1.0?**  
A: Confidence reflects uncertainty in semantic matching. 0.9 (90%) means very high confidence but acknowledges that LLMs aren't 100% certain about any answer.

**Q: Can I ask questions about things not in the PDFs?**  
A: The system will try to answer, but confidence will be lower. For best results, ask about the 7 policy documents indexed.

**Q: What if I want to add more documents?**  
A: See FRONTEND_INTEGRATION_GUIDE.md "Available PDF Documents" section. Contact admin to add new PDFs.

---

## Success Indicators

You know it's working when:
1. ✅ Both terminals show "running" status
2. ✅ Browser loads http://localhost:3000 without errors  
3. ✅ You can submit queries
4. ✅ Answers contain policy text from PDFs
5. ✅ Document names appear in the answer
6. ✅ Confidence scores are 0.8 or higher
7. ✅ Multiple queries work consistently

---

## You're All Set!

Your Retail Policy Intelligence System is ready to use. Start with the backend, then the frontend, then submit some test queries.

**Enjoy using your policy intelligence system!** 🚀

