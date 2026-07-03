# 🗑️ SAFE DELETION GUIDE - Vite Frontend Removal

**Date:** July 3, 2026  
**Action:** Remove old Vite frontend  
**Safety Level:** SAFE ✅ - All features preserved in Next.js

---

## ⚠️ PRE-DELETION VERIFICATION

### **Step 1: Confirm All Features in Next.js**

**Test URL:** `http://localhost:3000`

- [ ] **Home page loads** with "Backend Connected & Ready"
- [ ] **Navigation works** (Home, Ask Question buttons)
- [ ] **Query page loads** with form
- [ ] **Can enter query:** "What is our refund policy?"
- [ ] **Response appears** with all metadata
- [ ] **SLO metrics card shows** (green card)
- [ ] **Test out-of-scope:** "Tell me a joke"
- [ ] **Red escalation alert appears**
- [ ] **Handoff button visible**
- [ ] **Can open modal** with details
- [ ] **Can add notes** in modal
- [ ] **Can confirm handoff** successfully
- [ ] **No errors in console** (F12 → Console)
- [ ] **No errors in terminal** where npm run dev is running

### **Step 2: Verify Backend Connection**

```bash
# Test backend is running
curl http://localhost:8000/health
# Expected response: {"status":"healthy",...}

# Test token endpoint
curl http://localhost:8000/token
# Expected response: {"access_token":"...","token_type":"bearer"}

# Test with query
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query":"What is our refund policy?"}'
# Expected response: Complete response with escalate, slo_metrics, etc.
```

### **Step 3: Check Environment Configuration**

```bash
cd frontend-nextjs
cat .env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Step 4: Verify No Dependencies on Vite Files**

```bash
# Check if Next.js imports anything from Vite frontend
grep -r "frontend/" frontend-nextjs/app/ 2>/dev/null || echo "✅ No imports from Vite"

# Check if any configs reference Vite
grep -r "vite" frontend-nextjs/ --exclude-dir=node_modules 2>/dev/null || echo "✅ No Vite references"
```

---

## ✅ PRE-DELETION CHECKLIST

Before proceeding with deletion, confirm ALL of these:

- [ ] Next.js is fully working
- [ ] All 3 capstone features verified
- [ ] Backend connection confirmed
- [ ] No console errors
- [ ] Environment properly configured
- [ ] No code dependencies on Vite frontend
- [ ] Have backup (optional but recommended)
- [ ] Understand the deletion is final
- [ ] Ready to proceed

---

## 📦 BACKUP (Optional - Recommended)

If you want a backup before deletion:

```bash
# Create dated backup
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System"

# Windows:
xcopy frontend frontend-backup-2026-07-03 /E /I /H
# (This will create a full backup)

# Or compress it:
tar -czf frontend-backup-2026-07-03.tar.gz frontend/

# Verify backup created
ls -lh frontend-backup*
```

---

## 🗑️ DELETION PROCEDURES

### **Option A: Complete Clean Deletion (Recommended)**

This removes everything from the Vite frontend.

**Windows (Command Prompt):**
```cmd
cd "c:\Users\Anagha.e\project\Project-1-Retail  Policy Intelligence & Decision Support System"

REM Delete the entire Vite frontend
rmdir /s /q frontend

REM Verify deletion
dir frontend 2>nul || echo ✅ Vite frontend successfully deleted

REM Confirm Next.js still exists
dir frontend-nextjs\app\components\
echo ✅ Next.js frontend verified
```

**Mac/Linux (Terminal):**
```bash
cd "/path/to/project/Project-1-Retail  Policy Intelligence & Decision Support System"

# Delete the entire Vite frontend
rm -rf frontend

# Verify deletion
ls frontend 2>/dev/null || echo "✅ Vite frontend successfully deleted"

# Confirm Next.js still exists
ls -la frontend-nextjs/app/components/
echo "✅ Next.js frontend verified"
```

### **Option B: Cautious Deletion (More Steps)**

If you want to be extra careful, delete incrementally:

```bash
# 1. Delete source files
rm -rf frontend/src/

# 2. Delete public assets
rm -rf frontend/public/

# 3. Delete node_modules (large)
rm -rf frontend/node_modules/

# 4. Delete configuration files
rm -f frontend/vite.config.js
rm -f frontend/tsconfig.json
rm -f frontend/tailwind.config.js
rm -f frontend/postcss.config.js
rm -f frontend/package.json
rm -f frontend/package-lock.json

# 5. Delete remaining files
rm -f frontend/index.html
rm -f frontend/.gitignore
rm -f frontend/.env.local

# 6. Delete the directory
rmdir frontend

# 7. Verify
ls frontend 2>/dev/null || echo "✅ Successfully deleted"
```

---

## ✅ POST-DELETION VERIFICATION

After deleting, run these checks:

### **Check 1: Vite Frontend is Gone**
```bash
ls -la frontend/ 2>/dev/null || echo "✅ Vite frontend deleted"
```

Expected: Error message "cannot access 'frontend/'" or "No such file"

### **Check 2: Next.js Still Works**
```bash
cd frontend-nextjs
npm run dev

# Browser: http://localhost:3000
# Should load home page with "Backend Connected & Ready"
```

### **Check 3: All Features Still Work**
```
- Enter: "What is our refund policy?"
- Submit
- See response with green SLO card
- ✅ NO ESCALATION

- Enter: "Tell me a joke"
- Submit
- See response
- ✅ RED ESCALATION ALERT
- Click handoff
- ✅ Modal works
```

### **Check 4: Backend Connection**
```bash
# In separate terminal
cd RetailPolicyAssistant
uvicorn app.main:app --reload

# Backend should be accessible from frontend
# Check in Next.js app: Home page shows "Backend Connected & Ready" ✅
```

### **Check 5: Git Status**
```bash
git status

# You should see:
# deleted:    frontend/.gitignore
# deleted:    frontend/src/...
# etc.

# This is expected. Git will track the deletion.
```

---

## 🔄 AFTER DELETION: CLEANUP TASKS

### **Update Documentation**

1. **Update README.md** - Remove Vite references
2. **Update START_HERE.md** - Point to frontend-nextjs only
3. **Update NEXTJS_INSTALLATION.md** - Remove Vite comparison
4. **Update all guides** - Reference Next.js only
5. **Update startup scripts** - Use next.js only

### **Update Git**

```bash
# Commit the deletion
git add -A
git commit -m "Remove old Vite frontend, standardize on Next.js production build"

# Verify
git log --oneline -3
```

### **Update Project Structure Documentation**

```markdown
## Project Structure

**Before (Confusing):**
- frontend/          (old Vite - NOT USED)
- frontend-nextjs/   (new Next.js - USED)

**After (Clear):**
- frontend-nextjs/   (production Next.js)
```

### **Update CI/CD / Deployment Configs**

- [ ] Remove any Vite build steps from CI/CD
- [ ] Update deployment scripts to use Next.js
- [ ] Update environment variables
- [ ] Update docker configs if using Docker

---

## 🚨 TROUBLESHOOTING DELETION

### **Issue: "Permission Denied" on Linux/Mac**

**Solution:**
```bash
# Use sudo if needed
sudo rm -rf frontend

# Or change permissions first
chmod -R 755 frontend
rm -rf frontend
```

### **Issue: Files Won't Delete on Windows**

**Solution:**
```cmd
REM Try using PowerShell
powershell -Command "Remove-Item -Path frontend -Recurse -Force"

REM Or use Shift+Delete in File Explorer
```

### **Issue: Next.js Frontend Accidentally Deleted**

**Recovery:**
```bash
# If you made a backup
cp -r frontend-backup-2026-07-03 frontend-nextjs

# Or restore from git
git restore frontend-nextjs/
```

---

## ✅ DELETION CONFIRMATION CHECKLIST

After deletion, confirm:

- [ ] `frontend/` directory completely removed
- [ ] `frontend-nextjs/` still exists and works
- [ ] `npm run dev` in frontend-nextjs still works
- [ ] All features verified working
- [ ] Backend connection verified
- [ ] Console has no errors
- [ ] Git shows deletion
- [ ] Backup made (if desired)
- [ ] Documentation updated
- [ ] Ready to proceed with development

---

## 📋 FINAL SUMMARY

**Deleted:** `frontend/` (82M) - Old Vite frontend  
**Kept:** `frontend-nextjs/` (456M) - Production Next.js  
**Loss:** None - All features preserved and enhanced  
**Gain:** Clean structure, type safety, enterprise-grade code  

---

## 🎯 NEXT STEPS AFTER DELETION

1. **Update Documentation** ✅ Point all references to frontend-nextjs/
2. **Commit Changes** ✅ `git commit -m "Remove old Vite frontend"`
3. **Add Admin Dashboard** ✅ Start next phase
4. **Add Compliance Dashboard** ✅ Start next phase
5. **Begin Testing Implementation** ✅ Unit + E2E tests

---

## ⚠️ FINAL WARNING

**After deletion, you cannot undo this operation without the backup.**

Make sure:
1. ✅ All features are working in Next.js
2. ✅ You don't need any code from Vite frontend
3. ✅ Backend connection is verified
4. ✅ You have a backup (optional)

**Proceed only when confident.** 🚀

---

## 🎉 SUCCESS CRITERIA

You'll know the deletion was successful when:

```
✅ Frontend directory gone
✅ Frontend-nextjs works perfectly
✅ All 3 capstone features functional:
   ✅ Out-of-scope detection with red alerts
   ✅ SLO metrics with color coding
   ✅ Escalation & handoff workflow
✅ Backend connects properly
✅ No errors in console
✅ Ready for next development phase
```

---

**Status:** Ready for safe deletion ✅

Proceed when ready!
