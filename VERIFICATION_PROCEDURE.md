# Dashboard 422 Error - Verification Procedure

## Quick Start Verification

### Step 1: Start the Backend
```bash
cd RetailPolicyAssistant
python -m uvicorn app.main:app --reload --port 8001
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

### Step 2: Start the Frontend
```bash
cd frontend-nextjs
npm run dev
```

Expected output:
```
Local:        http://localhost:3000
```

### Step 3: Open Browser
Navigate to: `http://localhost:3000`

Expected behavior:
1. Home page redirects to `/dashboard`
2. RootProvider initializes auth on app load
3. Dashboard loads successfully ✅
4. No 422 errors in browser console
5. Dashboard displays metrics and charts

---

## Detailed Verification Steps

### Phase 1: Check RootProvider Initialization

**In Browser DevTools Console:**
```javascript
// Check if authentication is working
fetch('/auth/status', { credentials: 'include' })
  .then(r => r.json())
  .then(d => console.log('Auth Status:', d))

// Should show:
// Auth Status: { authenticated: true, user_id: "...", username: "...", email: "...", role: "..." }
```

**Expected**: `authenticated: true`

**If Not Authenticated**: RootProvider failed to initialize tokens
- Check browser console for errors
- Check Network tab: POST /token should return 200
- Check Application tab: Cookies should have `access_token` and `refresh_token`

---

### Phase 2: Check Dashboard Data Loading

**In Browser DevTools Network Tab:**
1. Filter by Fetch/XHR requests
2. Look for: `GET /api/dashboard`
3. Click on the request

**Expected**:
- **Status**: 200 (NOT 422) ✅
- **Headers**: Contains `Cookie: access_token=...`
- **Response**: JSON with all dashboard metrics

**If 422 Error**:
- Authentication initialization failed
- Check RootProvider is wrapping the app
- Check `initializeTokens()` is being called
- Check `/token` endpoint returns 200

**If 401 Error**:
- Token is invalid or expired
- Check token in cookies via browser DevTools
- Try hard refresh: Ctrl+Shift+R

---

### Phase 3: Check Backend Logs

**Expected Backend Logs When Dashboard Loads**:
```
GET /api/dashboard HTTP/1.1
200 OK

[Dashboard endpoint processing...]
[Query count from database...]
[Recent queries retrieved...]
[Hourly trends calculated...]
```

**If 422 Appears in Logs**:
```
GET /api/dashboard HTTP/1.1
422 Unprocessable Content
```

This indicates: No authentication token in request
- Check CORS middleware (should allow credentials)
- Check frontend is sending cookies
- Check cookie names match between frontend/backend

---

### Phase 4: Verify All Components Load

**Dashboard should display**:
- ✅ Retail Policy Intelligence header
- ✅ Quick Actions (Ask Question, Compliance Center)
- ✅ Metric Cards (Total Queries, Avg Response Time, Escalation Rate, Budget Used)
- ✅ Success Rate card (SLO compliance)
- ✅ Charts (Query Routes, Risk Distribution, System Health)
- ✅ Query Trends (24h)
- ✅ Top Policies table
- ✅ Recent Queries table

**If Anything Missing**:
- Check browser console for JavaScript errors
- Check Network tab for failed requests
- Look for 422 errors specifically

---

### Phase 5: Test Other Protected Endpoints

**Test Query Endpoint**:
1. Click "Ask Question" button
2. Enter a test query: "What is the vendor approval process?"
3. Click Submit

**Expected**:
- Loading spinner appears
- Query processes successfully
- Response displays with intent, risk, route, etc.

**If 422 Error**:
- Same authentication issue as dashboard
- Check token is still valid in cookies
- Check `/ask` endpoint documentation

**Test Logout**:
1. Click Logout button
2. Cookies should be cleared
3. Try accessing dashboard
4. Should get 401 error (expected - logged out)

---

## Automated Testing

### Run Integration Tests
```bash
cd RetailPolicyAssistant
pytest tests/test_dashboard_integration.py -v
```

**Expected Output**:
```
tests/test_dashboard_integration.py::TestAuthenticationFlow::test_token_endpoint_returns_200 PASSED
tests/test_dashboard_integration.py::TestAuthenticationFlow::test_auth_status_with_bearer_token_returns_200 PASSED
tests/test_dashboard_integration.py::TestDashboardEndpoint::test_dashboard_with_bearer_token_returns_200 PASSED
tests/test_dashboard_integration.py::TestDashboardEndpoint::test_dashboard_response_structure PASSED
...

====================== 15 passed in 2.34s ======================
```

**If Any Tests Fail**:
- Most likely: Database not initialized
- Solution: `python -c "from app.database.session import Base, engine; Base.metadata.create_all(engine)"`
- Or check database connection string in environment

---

## Performance Verification

### Check Token Initialization Time

**In Browser DevTools Performance Tab**:
1. Open Performance tab
2. Start recording
3. Refresh page
4. Stop recording
5. Look for: `initializeTokens()` and `POST /token`

**Expected**:
- Token request completes within 100-200ms
- Dashboard data request starts after token completes
- Total page load time: 1-2 seconds

**If Slow**:
- Check backend performance
- Check database performance
- Check network latency

---

## Rollback Plan (If Needed)

### If Issues Occur After Fix:

**Option 1: Disable RootProvider**
```typescript
// In layout.tsx, comment out RootProvider
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {/* <RootProvider> */}
        {children}
        {/* </RootProvider> */}
      </body>
    </html>
  );
}
```

**Option 2: Revert Changes**
```bash
git revert HEAD~2  # Revert the auth initialization commits
```

---

## Success Criteria

✅ **All of the following must be true**:

1. **Dashboard Loads**
   - Page displays without errors
   - All metrics visible
   - Charts render correctly

2. **No 422 Errors**
   - Browser console: No 422 errors
   - Network tab: No 422 responses
   - Backend logs: No 422 responses

3. **Authentication Works**
   - DevTools: `authenticated: true`
   - Cookies: `access_token` and `refresh_token` present
   - Bearer token validation: Works

4. **All Features Accessible**
   - Dashboard: ✅ 200 OK
   - Query page: ✅ Can ask questions
   - Observability: ✅ Can see metrics
   - Ingestion: ✅ Can upload files
   - Logout: ✅ Works and clears cookies

5. **Tests Pass**
   - All 15+ integration tests pass
   - No failed assertions
   - No exception errors

---

## Common Issues & Solutions

### Issue: 422 Error Still Appears

**Diagnosis**:
```javascript
// In console, check if tokens were set
document.cookie  // Should show access_token and refresh_token
```

**Solutions**:
1. Check RootProvider is in layout.tsx
2. Check `initializeTokens()` is called in useEffect
3. Check `/token` endpoint returns 200
4. Check CORS middleware has `allow_credentials: True`
5. Check frontend axios has `withCredentials: true`

---

### Issue: 401 Error After Loading

**Diagnosis**: Token exists but is invalid

**Solutions**:
1. Clear cookies and refresh: Ctrl+Shift+Delete
2. Check token expiration time
3. Check token has correct claims (user_id, username, etc.)
4. Check backend secret key matches between requests

---

### Issue: CORS Error

**Error**: "No 'Access-Control-Allow-Credentials' header"

**Solutions**:
1. Check backend CORS middleware:
   ```python
   allow_credentials=True
   ```
2. Check frontend axios:
   ```typescript
   withCredentials: true
   ```
3. Check allowed origins includes frontend URL

---

### Issue: Cookies Not Persisting

**Diagnosis**: Cookies set but not sent with requests

**Solutions**:
1. Check cookie settings:
   ```python
   httponly: True
   secure: False  # for localhost
   samesite: "lax"
   ```
2. Check browser privacy mode isn't blocking cookies
3. Check browser cookie settings allow localhost

---

## Monitoring & Alerting

### What to Monitor

1. **Dashboard 422 Error Rate**
   - Should drop from ~100% to 0%
   - If increases again, authentication initialization failed

2. **Dashboard 200 Response Rate**
   - Should increase from ~0% to ~100%
   - If decreases, check database connectivity

3. **Dashboard Response Time**
   - Should be < 500ms (excluding network latency)
   - If increases, check database query performance

4. **Token Initialization Success Rate**
   - Track `/token` endpoint success rate
   - Should be > 99%
   - Failures indicate backend issues

### Error Logging

```python
# Add to RootProvider error handling
initializeTokens().catch((err) => {
  console.error('[AUTH] Token initialization failed:', err);
  // Could send to error tracking service
  // sendToErrorTracking(err, 'AUTH_INIT_FAILED');
});
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All tests pass: `pytest tests/test_dashboard_integration.py -v`
- [ ] Dashboard loads in development
- [ ] No 422 errors in development
- [ ] No JavaScript errors in browser console
- [ ] Cookies properly set (check DevTools)
- [ ] Authentication flow works end-to-end
- [ ] Logout and re-login works
- [ ] Token refresh works (wait 30+ minutes)
- [ ] CORS configured for production domain
- [ ] Cookie secure flag set to true (HTTPS only)
- [ ] Backend logs show successful requests
- [ ] Database queries perform acceptably
- [ ] Error handling works for all edge cases

---

## Summary

The 422 error has been fixed by:
1. Exporting `initializeTokens()` function
2. Creating RootProvider component
3. Wrapping app with RootProvider

**Verification Method**: 
- ✅ Start backend and frontend
- ✅ Open dashboard
- ✅ Check for 200 status (not 422)
- ✅ Verify metrics display
- ✅ Run integration tests

**Expected Outcome**: Dashboard loads successfully with all features working.
