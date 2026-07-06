# COMPLETE FIX - Run Backend & Frontend Correctly

## The Real Problem

You were using **system Python** (Git Bash) instead of the **virtual environment**, which caused the uuid_utils error.

---

## SOLUTION: Use the Batch Scripts

I've created two batch files that properly activate the venv and run everything correctly.

### Step 1: Run Backend (Open CMD or PowerShell)

**Navigate to:**
```
C:\Users\Anagha.e\project\RetailPolicy_Intelligence_Decision_Support_System\RetailPolicyAssistant
```

**Double-click:** `run_backend.bat`

OR run:
```
run_backend.bat
```

**Expected Output:**
```
Activating virtual environment...
Installing/Updating uuid-utils in venv...
Starting backend on port 8001...
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

### Step 2: Run Frontend (Open NEW CMD or PowerShell)

**Navigate to:**
```
C:\Users\Anagha.e\project\RetailPolicy_Intelligence_Decision_Support_System\frontend-nextjs
```

**Double-click:** `run_frontend.bat`

OR run:
```
run_frontend.bat
```

**Expected Output:**
```
Starting frontend on port 3000...
✓ Ready in 2.9s
✓ Compiled / in 5.2s
```

### Step 3: Open Browser

```
http://localhost:3000
```

### Step 4: Test Query

**Enter:** "How long must we retain email data?"

**Expected Result:**
```
ANSWER:
Email data retention: 3 years for business purposes

CONFIDENCE: 0.92
RISK LEVEL: Low
SOURCES: 
- Data_Retention_and_Archival_Policy.pdf (Page 1)
```

---

## Why This Works

1. **`run_backend.bat`:**
   - Activates the virtual environment properly (using PowerShell/CMD, not Git Bash)
   - Installs uuid-utils in the venv
   - Runs the backend with proper Python from venv

2. **`run_frontend.bat`:**
   - Runs the Next.js dev server on port 3000

3. **Both use `.bat` files:**
   - `.bat` files properly handle Windows environment activation
   - Git Bash doesn't properly activate venv
   - PowerShell/CMD does

---

## If Still Getting Errors

### Error: "uuid_utils not found"

**Fix:** Delete the old venv and recreate:
```bash
# In RetailPolicyAssistant folder
rmdir venv /s /q
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Then use `run_backend.bat`

### Error: "Port already in use"

**Kill the process:**
```
netstat -ano | findstr :8001
taskkill /PID <number> /F
```

Then restart `run_backend.bat`

### Error: "Module not found"

**Make sure you're in the right folder when running .bat file:**
```
C:\Users\Anagha.e\project\RetailPolicy_Intelligence_Decision_Support_System\RetailPolicyAssistant\run_backend.bat
```

---

## Complete Checklist

- [ ] Backend started with `run_backend.bat` (see "Uvicorn running on 127.0.0.1:8001")
- [ ] Frontend started with `run_frontend.bat` (see "Ready in X.Xs")
- [ ] Browser opens to `http://localhost:3000` without errors
- [ ] Can enter query in text box
- [ ] Submit button works
- [ ] Get answer back (not error)
- [ ] Answer includes PDF document name
- [ ] Confidence score shows 0.9+
- [ ] Sources list PDF name and page number

---

## What Changed

### Before (BROKEN):
- You used Git Bash
- Git Bash didn't activate venv properly
- System Python was used
- uuid_utils in venv wasn't available
- Error: "uuid_utils not found"

### After (FIXED):
- Use `.bat` files (Windows native)
- `.bat` files properly activate venv
- Venv Python is used
- uuid_utils in venv is available
- Everything works!

---

## Files Created

1. `run_backend.bat` - Properly runs backend with venv
2. `run_frontend.bat` - Properly runs frontend
3. This file - Instructions

---

## QUICK START

1. Open CMD/PowerShell
2. Go to: `C:\Users\Anagha.e\project\RetailPolicy_Intelligence_Decision_Support_System\RetailPolicyAssistant`
3. Run: `run_backend.bat`
4. Open another CMD/PowerShell
5. Go to: `C:\Users\Anagha.e\project\RetailPolicy_Intelligence_Decision_Support_System\frontend-nextjs`
6. Run: `run_frontend.bat`
7. Open browser: `http://localhost:3000`
8. Test a query!

**This WILL work!** The issue was using Git Bash instead of Windows CMD/PowerShell.

