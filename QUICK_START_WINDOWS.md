# 🚀 Quick Start Guide - Windows

**Retail Policy Intelligence & Decision Support System**

---

## ⚠️ Known Issue: Path with Special Characters

The folder name contains `&` which causes issues on Windows. Here are the solutions:

---

## Solution 1: Use PowerShell (Recommended)

### Terminal 1: Backend
```powershell
cd frontend
cd ..
cd RetailPolicyAssistant
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend
```powershell
cd frontend
npx vite
```

### Browser
```
http://localhost:5173
```

---

## Solution 2: Use Batch Files (Easiest)

### Run Backend
```bash
RUN_BACKEND.bat
```

### Run Frontend
```bash
RUN_FRONTEND.bat
```

---

## Solution 3: Change Directory Approach

If PowerShell doesn't work:

### Terminal 1: Backend
```cmd
cd %CD:&=^&%
cd RetailPolicyAssistant
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend (Change to frontend subfolder first)
```cmd
cd frontend
npx vite
```

---

## Solution 4: VS Code Integration (Recommended)

Open VS Code in the project folder, then use integrated terminal (Ctrl+`):

### Terminal 1
```bash
cd RetailPolicyAssistant
python -m uvicorn app.main:app --reload
```

### Terminal 2
```bash
cd frontend
npm run dev
```

VS Code handles the special characters automatically!

---

## Full Setup Steps (Windows PowerShell)

### Step 1: Open PowerShell
```
Windows key + X
Select "Windows PowerShell" or "Terminal"
```

### Step 2: Navigate to Project
```powershell
# Navigate to project root
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System"
```

### Step 3: Start Backend (Terminal 1)
```powershell
cd RetailPolicyAssistant
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Start Frontend (Terminal 2 - New PowerShell)
```powershell
# From project root
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System"
cd frontend
npx vite
```

Expected output:
```
  VITE v8.1.1  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### Step 5: Open Browser
```
http://localhost:5173
```

---

## Troubleshooting

### Error: "'Decision' is not recognized"
**Cause**: Windows cmd.exe interpreting the `&` character  
**Solution**: Use PowerShell or VS Code terminal instead

### Error: "Cannot find module vite"
**Solution**: 
```powershell
cd frontend
npm install
```

### Error: Backend won't start
**Check**:
```cmd
python --version
```

Should be Python 3.8+

**Fix**:
```powershell
cd RetailPolicyAssistant
pip install -r requirements.txt
```

### Error: Frontend won't load
**Check** browser console (F12)  
**Check** backend is running:
```cmd
curl http://localhost:8000/health
```

---

## Quick Verification

### Health Check (Cmd/PowerShell)
```cmd
curl http://localhost:8000/health
```

Expected:
```json
{"status": "healthy", "version": "1.0.0"}
```

### Frontend Access
Open browser: `http://localhost:5173`

Should see homepage with:
- Navigation bar
- "Retail Policy Intelligence System"
- Query form
- Example queries

---

## One-Click Setup (VS Code)

If using VS Code:

1. **Open project folder** in VS Code
2. **Click Extensions** (Ctrl+Shift+X)
3. **Search and install**:
   - "Python" by Microsoft
   - "REST Client" by Huachao Mao
4. **Open Integrated Terminal** (Ctrl+`)
5. **Split Terminal** (Ctrl+Shift+5)
6. **Run commands**:
   - Terminal 1: `cd RetailPolicyAssistant && python -m uvicorn app.main:app --reload`
   - Terminal 2: `cd frontend && npm run dev`

VS Code automatically handles the special characters!

---

## .env Configuration

Verify `.env` file in `RetailPolicyAssistant`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/retail_policy
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
OPENAI_API_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

---

## Demo Walkthrough (After Setup)

Once both are running:

1. **Navigate to Query Page**
   - Click "Queries" in navbar

2. **Run Query 1 - RAG**
   - Input: "What is our data retention policy?"
   - Expected: Route=RAG, Risk=Low

3. **Run Query 2 - SQL**
   - Input: "List vendors with critical findings"
   - Expected: Route=SQL, Risk=High

4. **Run Query 3 - Escalation**
   - Input: "Delete compliance records?"
   - Expected: Risk=HIGH, Escalation Alert

5. **Check Dashboard**
   - Click "Dashboard" in navbar
   - See SLO metrics

---

## Performance Tips

- **Backend**: First query takes ~2s (embeddings load)
- **Subsequent queries**: 0.5-1.5s
- **Frontend**: Hot reload on code changes (Vite feature)
- **Database**: Ensure PostgreSQL is running

---

## Frequently Asked Questions

**Q: Can I use Git Bash instead of PowerShell?**  
A: Yes! Git Bash handles special characters better than cmd.exe

**Q: Do I need PostgreSQL running?**  
A: Yes, for SQL queries. For testing RAG only, it's optional.

**Q: Can I access from another computer?**  
A: For local only. Change `localhost` to `0.0.0.0` in main.py for network access.

**Q: How do I stop the servers?**  
A: Press `Ctrl+C` in each terminal

---

## Next Steps

1. ✅ Follow steps above to start system
2. ✅ Try example queries
3. ✅ Check dashboard
4. ✅ Read DEMO.md for presentation script
5. ✅ Review documentation in root folder

---

**Status**: ✅ Ready to Run  
**Last Updated**: 2026-07-03  
**Questions**: Check 00_READ_ME_FIRST.md
