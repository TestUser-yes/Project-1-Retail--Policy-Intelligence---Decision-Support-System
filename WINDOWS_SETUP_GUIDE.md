# 🪟 Windows Setup Guide

**Retail Policy Intelligence & Decision Support System**

---

## 🚀 Fastest Way to Start (3 Steps)

### Option A: Using Batch Files (Easiest) ✅

**Step 1**: Open first Command Prompt
```cmd
RUN_BACKEND.bat
```

**Step 2**: Open second Command Prompt
```cmd
RUN_FRONTEND.bat
```

**Step 3**: Open browser
```
http://localhost:5173
```

---

### Option B: Using PowerShell (Recommended) ✅

**Step 1**: Open PowerShell (Windows Key + X → PowerShell)

**Step 2**: Navigate to project
```powershell
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System"
```

**Step 3**: Start backend (Terminal 1)
```powershell
cd RetailPolicyAssistant
python -m uvicorn app.main:app --reload --port 8000
```

Wait for:
```
Uvicorn running on http://127.0.0.1:8000
```

**Step 4**: Open new PowerShell (Windows Key + X → PowerShell)

**Step 5**: Start frontend (Terminal 2)
```powershell
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System"
cd frontend
npm run dev
```

Wait for:
```
Local:   http://localhost:5173/
```

**Step 6**: Open browser
```
http://localhost:5173
```

---

### Option C: Using VS Code (Best for Development) ✅

**Step 1**: Open VS Code
- File → Open Folder
- Select: `Project-1-Retail  Policy Intelligence & Decision Support System`

**Step 2**: Open Integrated Terminal (Ctrl+`)

**Step 3**: Split Terminal (Ctrl+Shift+5)

**Step 4**: Terminal 1 (Left)
```powershell
cd RetailPolicyAssistant
python -m uvicorn app.main:app --reload
```

**Step 5**: Terminal 2 (Right)
```powershell
cd frontend
npm run dev
```

**Step 6**: Open Browser
```
http://localhost:5173
```

---

## ✅ Verification Checklist

### Backend Running?
Open new PowerShell:
```powershell
curl http://localhost:8000/health
```

Should see:
```json
{"status":"healthy","version":"1.0.0"}
```

### Frontend Loading?
Open browser: `http://localhost:5173`

Should see:
- Navigation bar with logo
- Query form
- Beautiful UI

### Try a Query
1. Type: "What is our data retention policy?"
2. Click "Ask Query"
3. Wait for response
4. Should show: Route=RAG, Risk=Low

---

## 🔧 Troubleshooting Windows Issues

### Issue 1: "'Decision' is not recognized"

**Cause**: Windows cmd.exe doesn't handle the `&` in folder name  

**Solution**: Use PowerShell or batch files instead

**Which to use**:
- ✅ PowerShell (Recommended)
- ✅ Git Bash
- ✅ Batch files (RUN_BACKEND.bat, RUN_FRONTEND.bat)
- ❌ cmd.exe (doesn't work)

---

### Issue 2: "Cannot find module vite"

**Cause**: Dependencies not installed

**Solution**:
```powershell
cd frontend
npm install
```

Then try:
```powershell
npm run dev
```

---

### Issue 3: Python not found

**Check** Python is installed:
```cmd
python --version
```

**If not installed**:
1. Download from https://python.org
2. Install with "Add Python to PATH" ✅
3. Restart PowerShell
4. Try again

---

### Issue 4: npm not found

**Check** Node.js is installed:
```cmd
npm --version
```

**If not installed**:
1. Download from https://nodejs.org
2. Install (includes npm)
3. Restart PowerShell
4. Try again

---

### Issue 5: Port 8000 or 5173 in use

**Check**:
```powershell
# Check port 8000
netstat -ano | findstr :8000

# Check port 5173
netstat -ano | findstr :5173
```

**Kill process** (replace PID with actual number):
```powershell
taskkill /PID <PID> /F
```

Or change ports in code:
- Backend: Change `8000` in RUN_BACKEND.bat
- Frontend: Add `--port 3000` to RUN_FRONTEND.bat

---

### Issue 6: Database connection error

**Ensure PostgreSQL is running**:
```powershell
# For PostgreSQL on Windows
# Check Services (services.msc) → look for "postgresql-x64-xx"
# If stopped, right-click → Start
```

**Or check .env**:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/retail_policy
```

Make sure credentials are correct.

---

### Issue 7: CORS errors in browser console

**Cause**: Frontend can't reach backend  

**Check**:
1. Backend running on port 8000?
2. Browser showing http://localhost:5173?
3. Check browser console (F12)

**Solution**:
1. Verify backend health: `curl http://localhost:8000/health`
2. Check that both ports are correct
3. Restart both services

---

## 📋 Pre-Setup Checklist

Before starting, verify you have:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] PostgreSQL running (if using SQL queries)
- [ ] Ollama running (`ollama serve`)
- [ ] Project folder downloaded
- [ ] PowerShell or VS Code installed

---

## 🚀 Alternative: Using Docker (Advanced)

If local setup doesn't work, use Docker:

```cmd
docker-compose up
```

(Requires Docker Desktop installed)

Then access: `http://localhost:5173`

---

## 📊 Expected Output

### Backend Starting
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Frontend Starting
```
  VITE v8.1.1  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### Browser Shows
```
Retail Policy Intelligence & Decision Support System

[Query Form with suggestions]
```

---

## 💡 Windows Tips

**Tip 1**: Pin PowerShell to taskbar
- Right-click PowerShell → "Pin to taskbar"

**Tip 2**: Create desktop shortcuts
- Right-click desktop → New → Shortcut
- Target: `cmd.exe /k "cd /d path && RUN_BACKEND.bat"`

**Tip 3**: Use Windows Terminal (Modern)
- Microsoft Store → Search "Windows Terminal"
- Better than cmd.exe for special characters

**Tip 4**: VS Code is best for development
- File → Open Folder
- Integrated terminal handles paths correctly

---

## 🎬 Full Demo Script (After Setup)

Once running:

1. **Query 1** (RAG)
   ```
   "What is our data retention policy?"
   Expected: Route=RAG, Risk=Low
   ```

2. **Query 2** (SQL)
   ```
   "List vendors with critical findings"
   Expected: Route=SQL, Risk=High
   ```

3. **Query 3** (High-Risk)
   ```
   "Delete compliance records?"
   Expected: Risk=HIGH, Escalation Alert
   ```

4. **Dashboard**
   - Click "Dashboard" tab
   - Show SLO metrics

---

## 🆘 Quick Support

**Not working?**

1. Check: Are both servers running? (Backend + Frontend)
2. Check: Is browser showing http://localhost:5173?
3. Check: Are there any error messages?

**Still stuck?**

1. Read: QUICK_START_WINDOWS.md (this file)
2. Read: DEPLOYMENT.md (detailed setup)
3. Read: 00_READ_ME_FIRST.md (overall guide)
4. Check: Browser console (F12 → Console tab)
5. Check: PowerShell error messages

---

## ✅ You're Ready!

After following above steps:
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ System fully functional
- ✅ Ready to demo

---

**Status**: ✅ Windows Setup Complete  
**Next**: Run the system and try example queries!
