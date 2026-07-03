# 🚀 Startup Guide - Retail Policy System

**Status**: Complete & Ready to Run  
**Last Updated**: 2026-07-03

---

## ✅ Pre-Startup Checklist

Before starting, ensure you have:

- [ ] Python 3.8+ installed
- [ ] PostgreSQL running (or available)
- [ ] Ollama running (or available)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] .env file configured (check `RetailPolicyAssistant/.env`)

---

## 🔍 Step 1: Run System Check

Open PowerShell in `RetailPolicyAssistant` folder:

```powershell
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System\RetailPolicyAssistant"
python check_system.py
```

**This will verify**:
- ✅ Python version
- ✅ FastAPI installed
- ✅ SQLAlchemy installed
- ✅ PostgreSQL running
- ✅ Ollama running
- ✅ All agents loaded
- ✅ Configuration correct

**You'll see output like**:
```
✅
  Python version: 3.11.0
  FastAPI: 0.109.0
  SQLAlchemy: 2.0.25
  PostgreSQL connection: OK
  Ollama connection: OK
  LangChain: OK
  All agents imported successfully

SUMMARY: 8 OK | 0 Warnings | 0 Errors
✅ All systems ready!
```

---

## 🗄️ Step 2: Initialize Database (if needed)

If you get PostgreSQL error, initialize the database:

```powershell
cd RetailPolicyAssistant
python app/db_init.py
```

This will:
- Create database tables
- Initialize schema
- Seed test data

**Wait for completion**. You should see:
```
✅ Database initialized successfully
✅ Tables created
✅ Test data inserted
```

---

## 🤖 Step 3: Start Ollama (in new terminal)

Open **new PowerShell terminal**:

```powershell
ollama serve
```

**Wait for**:
```
Listening on 127.0.0.1:11434
```

Leave this running. **Keep the terminal open!**

---

## 🔌 Step 4: Start PostgreSQL (if not running)

**Windows Services**:
1. Press `Windows Key + R`
2. Type `services.msc`
3. Find "postgresql-x64-XX"
4. If stopped, right-click → Start

Or via PowerShell:
```powershell
Start-Service postgresql-x64-15  # adjust version number
```

---

## 🚀 Step 5: Start Backend

Open **new PowerShell terminal**:

```powershell
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System\RetailPolicyAssistant"
python -m uvicorn app.main:app --reload --port 8000
```

**Wait for**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Keep this terminal open!** This is your backend server.

---

## 🎨 Step 6: Start Frontend

Open **new PowerShell terminal**:

```powershell
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System\frontend"
npm run dev
```

**Wait for**:
```
  VITE v8.1.1  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Keep this terminal open!** This is your frontend server.

---

## 🌐 Step 7: Access the System

Open your browser and go to:
```
http://localhost:5173
```

You should see:
- Navigation bar with logo
- Query form with input field
- Beautiful Tailwind CSS styling
- Example queries dropdown

---

## ✅ Step 8: Test the System

### Test via Swagger (Backend API)

```
http://localhost:8000/docs
```

**Click**: `GET /health`  
**Click**: "Try it out"  
**Click**: "Execute"

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "system": "Retail Policy AI",
  "agents": "active",
  "db": "connected"
}
```

### Test via Frontend (UI)

1. Go to `http://localhost:5173`
2. Type: "What is our data retention policy?"
3. Click "Ask Query"
4. Wait for response
5. You should see:
   - Route: RAG
   - Risk: Low
   - Response with policy text
   - Latency in seconds

---

## 🔧 Troubleshooting

### PostgreSQL Connection Error

**Error**: `connection timeout expired`

**Fix**:
```powershell
# Check if PostgreSQL is running
psql -h localhost -U postgres -c "SELECT 1"

# If not running, start it
Start-Service postgresql-x64-15

# Or open Services → postgresql → Start
```

### Ollama Connection Error

**Error**: `requests.exceptions.ConnectionError`

**Fix**:
```powershell
# Start Ollama in new terminal
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### 500 Error on /ask endpoint

**Possible causes**:
1. Ollama not running
2. PostgreSQL not running
3. Database not initialized

**Fix**:
1. Check system: `python check_system.py`
2. Start Ollama: `ollama serve`
3. Start PostgreSQL: `services.msc`
4. Initialize DB: `python app/db_init.py`

### Frontend won't load

**Error**: `npm: not found`

**Fix**:
```powershell
# Install Node.js from https://nodejs.org
# Then verify installation
node --version
npm --version

# Install dependencies
cd frontend
npm install

# Try again
npm run dev
```

### Port already in use

**Error**: `Address already in use`

**Fix** (if port 8000 in use):
```powershell
# Stop all Python processes
taskkill /F /IM python.exe

# Or change port in command:
python -m uvicorn app.main:app --reload --port 8001
```

**Fix** (if port 5173 in use):
```powershell
# Change frontend port:
cd frontend
npm run dev -- --port 3000
# Then go to http://localhost:3000
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────┐
│         Browser (http://localhost:5173)     │
│  React UI with Tailwind CSS                 │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  Frontend Server (Vite dev server, npm run) │
│  Port: 5173                                 │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  Backend API (FastAPI, Uvicorn)             │
│  Port: 8000                                 │
│  Endpoints: /health, /ask, /docs            │
└─────────────────────────────────────────────┘
           ↙              ↓              ↘
    Ollama          PostgreSQL       Agents
 (Port 11434)     (Port 5432)
   Embeddings      Policy Docs        RAG
                   Vendor Data        SQL
                                   Hybrid
```

---

## 📝 Example Queries to Try

### Query 1: RAG (Policy)
```
"What is our data retention policy?"
```
Expected: Route=RAG, Risk=Low

### Query 2: SQL (Database)
```
"List vendors with critical findings"
```
Expected: Route=SQL, Risk=High

### Query 3: Hybrid (Both)
```
"Is vendor 456 compliant with our retention policy?"
```
Expected: Route=Hybrid, Risk=High

### Query 4: High-Risk (Escalation)
```
"Delete compliance records?"
```
Expected: Risk=HIGH, Escalation Alert

---

## 🎯 Quick Start Commands

**All 3 at once** (in separate terminals):

**Terminal 1**:
```powershell
cd RetailPolicyAssistant && python -m uvicorn app.main:app --reload
```

**Terminal 2**:
```powershell
cd frontend && npm run dev
```

**Terminal 3**:
```powershell
ollama serve
```

Then open browser: `http://localhost:5173`

---

## 🆘 Still Not Working?

1. **Run diagnostics**:
   ```powershell
   python check_system.py
   ```

2. **Check backend logs** in the terminal running Uvicorn

3. **Check browser console** (F12 in browser)

4. **Verify all 3 services running**:
   - Backend: Port 8000
   - Frontend: Port 5173
   - Ollama: Port 11434

5. **Check .env file** in `RetailPolicyAssistant/`:
   - DATABASE_URL set correctly
   - OLLAMA_BASE_URL = http://localhost:11434
   - OLLAMA_MODEL = phi3:mini

---

## ✨ System is Running!

Once you see all 3 running:
- ✅ Backend: `Uvicorn running on http://127.0.0.1:8000`
- ✅ Frontend: `VITE ready on http://localhost:5173/`
- ✅ Ollama: `Listening on 127.0.0.1:11434`

Open browser to `http://localhost:5173` and start querying!

---

**Status**: 🟢 Ready to Run  
**Next**: Follow steps 1-7 above
