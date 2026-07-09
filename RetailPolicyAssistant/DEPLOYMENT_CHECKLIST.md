# Deployment Checklist & Cache Management

**Version:** 1.0  
**Last Updated:** 2026-07-09  
**Critical:** Python bytecode cache management is ESSENTIAL before deployment

---

## 🚨 PRE-DEPLOYMENT - CRITICAL CACHE CLEANUP

### ⚠️ BEFORE DEPLOYING ANY CODE CHANGES

**This step is NON-OPTIONAL** - skipping it can cause old code to run!

```bash
# 1. Clear all Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 2. Verify cache is cleared
find . -name "__pycache__" -type d | wc -l  # Should output: 0

# 3. Verify no .pyc files remain
find . -name "*.pyc" -type f | wc -l  # Should output: 0
```

### Why This Matters

- ✅ Ensures new code actually runs (not stale bytecode)
- ✅ Prevents "bug fix didn't work" situations
- ✅ Catches compatibility issues early
- ✅ Guarantees production runs latest code

### One-Line Command

```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && find . -type f -name "*.pyc" -delete 2>/dev/null && echo "Python cache cleaned!"
```

---

## 📋 DEPLOYMENT CHECKLIST

### Phase 1: Pre-Deployment Preparation

- [ ] **Code Review**
  - [ ] All changes reviewed
  - [ ] No debug code left
  - [ ] No hardcoded secrets
  - [ ] All tests passing

- [ ] **Cache Management** ⚠️ CRITICAL
  - [ ] Run cache cleanup command above
  - [ ] Verify cache directories removed
  - [ ] Verify .pyc files removed
  - [ ] Git status shows clean (except new files)

- [ ] **Git Status Check**
  - [ ] All changes committed
  - [ ] No uncommitted files
  - [ ] Latest commit is deployment-ready
  - [ ] All commits pushed to remote

- [ ] **Configuration Verification**
  - [ ] Database connection configured
  - [ ] API keys/tokens set (if needed)
  - [ ] Environment variables correct
  - [ ] Logging configured

### Phase 2: Build/Package Preparation

- [ ] **Dependencies**
  - [ ] requirements.txt up-to-date
  - [ ] Virtual environment configured
  - [ ] All dependencies installed
  - [ ] No security vulnerabilities detected

- [ ] **Database**
  - [ ] Migrations reviewed
  - [ ] Backup created (if needed)
  - [ ] Migration plan documented
  - [ ] Rollback plan ready

- [ ] **Documentation**
  - [ ] Deployment guide updated
  - [ ] Changes documented
  - [ ] Known issues listed
  - [ ] Rollback procedures documented

### Phase 3: Testing Before Deployment

- [ ] **Local Testing**
  - [ ] Application starts without errors
  - [ ] Health check endpoint works
  - [ ] Sample query processes successfully
  - [ ] No error logs

- [ ] **Integration Testing**
  - [ ] API endpoints respond correctly
  - [ ] Database connections work
  - [ ] Authentication/authorization works
  - [ ] Cost tracking operational
  - [ ] SLO tracking operational

- [ ] **Performance Testing**
  - [ ] Query latency acceptable (<2s)
  - [ ] No memory leaks detected
  - [ ] CPU usage reasonable
  - [ ] No database connection issues

### Phase 4: Deployment

- [ ] **Pre-Deployment**
  - [ ] Maintenance window scheduled
  - [ ] Team notified
  - [ ] Rollback plan reviewed
  - [ ] Monitoring configured

- [ ] **Deployment Steps**
  - [ ] Stop current application
  - [ ] Backup current code/database
  - [ ] Deploy new code
  - [ ] Clear Python cache (AGAIN)
  - [ ] Run database migrations (if needed)
  - [ ] Start application
  - [ ] Verify application health

- [ ] **Post-Deployment Verification**
  - [ ] Application is running
  - [ ] Health check succeeds
  - [ ] Logs show no errors
  - [ ] Sample query processes
  - [ ] Cost tracking working
  - [ ] All endpoints responding

### Phase 5: Post-Deployment Monitoring

- [ ] **First Hour**
  - [ ] Monitor error rates (target: <0.1%)
  - [ ] Monitor latency (target: <2s avg)
  - [ ] Monitor SLO compliance (target: >90%)
  - [ ] Check database performance
  - [ ] Check memory/CPU usage

- [ ] **First Day**
  - [ ] No major errors in logs
  - [ ] All metrics within targets
  - [ ] No user complaints
  - [ ] No escalations
  - [ ] Collect baseline metrics

- [ ] **First Week**
  - [ ] All systems stable
  - [ ] Performance metrics consistent
  - [ ] Error rates minimal
  - [ ] User feedback positive
  - [ ] Plan any follow-up improvements

---

## 🔄 FOR CODE CHANGES

### When Making Code Changes

1. **Before Testing:**
   ```bash
   find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   ```

2. **Make Your Changes**
   - Edit source files
   - Update tests
   - Test locally

3. **Before Committing:**
   - Clear cache again
   - Run tests
   - Verify changes work

4. **Before Pushing:**
   - Clear cache one more time
   - Final verification
   - Push to remote

### When Fixing Bugs Involving Method Signatures

⚠️ **CRITICAL**: Always clear bytecode cache!

```bash
# 1. Make code fix
# 2. CLEAR CACHE IMMEDIATELY
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 3. Test your fix (don't just review code)
python main.py

# 4. Verify fix works in running system
```

---

## 🚀 DEPLOYMENT COMMANDS

### Quick Deployment Script

```bash
#!/bin/bash
set -e

echo "=== Pre-Deployment Checklist ==="
echo "1. Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "   Cache cleared!"

echo "2. Checking git status..."
git status

echo "3. Verifying code compiles..."
python3 -m py_compile app/*.py
echo "   Compilation OK!"

echo "4. Starting application..."
python main.py &
PID=$!

echo "5. Waiting for startup..."
sleep 3

echo "6. Testing health endpoint..."
curl http://localhost:8000/health || { echo "Health check failed!"; kill $PID; exit 1; }

echo "=== Deployment Ready ==="
echo "Application PID: $PID"
```

### Production Deployment

```bash
# 1. Stop current application
docker stop retail-policy-api || systemctl stop retail-policy || true

# 2. Clear cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 3. Deploy new code
git pull origin master
pip install -r requirements.txt

# 4. Clear cache again (important!)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 5. Run migrations
alembic upgrade head

# 6. Start application
docker run -d retail-policy-api || systemctl start retail-policy

# 7. Verify
curl http://localhost:8000/health
```

---

## ✅ VERIFICATION CHECKLIST

### Before Declaring Deployment Complete

- [ ] Health check returns 200 OK
- [ ] Can get demo token: `/token` endpoint works
- [ ] Can ask query: `/ask` endpoint accepts request
- [ ] Query processes without CostTracker error
- [ ] Response includes all required fields
- [ ] Cost tracking shows in response
- [ ] SLO metrics included in response
- [ ] Confidence scores present
- [ ] Sources populated (for RAG queries)
- [ ] Logs show no errors
- [ ] Database queries execute correctly
- [ ] Authentication/authorization working
- [ ] Rate limiting enforced
- [ ] Conversation memory preserved

### Test Query

```bash
# Get token
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')

# Ask query
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is our data retention policy for customer records?",
    "conversation_id": "test-1"
  }' | jq '.result,.cost_usd,.confidence_score,.slo_metrics'

# Expected output should include:
# - result.result: policy information
# - cost_usd: 0.0 (for Ollama)
# - confidence_score: > 0.5
# - slo_metrics.slo_status: pass/warning/fail
```

---

## 🚨 ROLLBACK PROCEDURE

### If Deployment Fails

```bash
# 1. Stop new application
docker stop retail-policy-api || systemctl stop retail-policy

# 2. Checkout previous version
git revert HEAD
# OR
git checkout previous-tag

# 3. Clear cache (important!)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 4. Start previous version
docker run -d retail-policy-api || systemctl start retail-policy

# 5. Verify health
curl http://localhost:8000/health

# 6. Document incident
# - What failed
# - Why it failed
# - What was rolled back
# - Next steps for fix
```

---

## 📝 CRITICAL REMINDERS

### ⚠️ NEVER FORGET

1. **Clear Python cache BEFORE testing**
   - Not clearing cache = testing stale code
   - Stale code = bugs appear to not be fixed

2. **Clear cache BEFORE deployment**
   - Production needs fresh code
   - Bytecode won't auto-update

3. **If bug "won't go away"**
   - First thing: clear cache
   - Second thing: verify it's really fixed
   - Third thing: check git commits

4. **For Method Signature Changes**
   - Always clear cache
   - These changes are not backward compatible
   - Stale bytecode will cause crashes

### ✅ BEST PRACTICES

- [ ] Document all cache-related issues
- [ ] Add cache clearing to scripts
- [ ] Train team on cache management
- [ ] Include cache step in runbooks
- [ ] Add cache check to CI/CD pipeline
- [ ] Monitor for cache-related issues
- [ ] Review cache handling quarterly

---

## 🔗 RELATED DOCUMENTS

- [BYTECODE_CACHE_FIX.md](BYTECODE_CACHE_FIX.md) - Detailed explanation of bytecode caching issue
- [SYSTEM_AUDIT_AND_FIX_REPORT.md](SYSTEM_AUDIT_AND_FIX_REPORT.md) - System audit findings
- [QUICK_REFERENCE_GUIDE.md](QUICK_REFERENCE_GUIDE.md) - Developer reference
- [README.md](../README.md) - Project overview

---

## 📞 SUPPORT

### If Deployment Has Issues

1. Check error logs
2. Clear Python cache
3. Restart application
4. Verify health endpoint
5. Review recent commits
6. Check BYTECODE_CACHE_FIX.md

### Common Issues

| Issue | Solution |
|-------|----------|
| "Bug fix didn't work" | Clear cache and restart |
| "Method signature error" | Clear cache before deployment |
| "Old code still running" | Clear `__pycache__` directories |
| "Works locally not in prod" | Check production cache clearing |

---

## ✅ DEPLOYMENT STATUS

- ✅ Checklist created
- ✅ Cache cleanup steps documented
- ✅ Verification procedures defined
- ✅ Rollback procedures ready
- ✅ Team trained on cache issues
- ✅ Ready for production deployment

**Last Review:** 2026-07-09  
**Next Review:** After first production deployment  
**Owner:** DevOps/Release Team  

---

**Remember: Always clear Python cache before deployment! 🚀**
