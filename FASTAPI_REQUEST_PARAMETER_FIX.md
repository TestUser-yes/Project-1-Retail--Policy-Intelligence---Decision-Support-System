# FastAPI Request Parameter Issue - Fix Guide

## Problem

FastAPI 0.139.0 has a bug where it treats `Request` type annotations as required query parameters instead of recognizing them as FastAPI special types.

This breaks the following endpoints:
- `GET /api/dashboard`
- `GET /api/observability`
- `POST /ask`
- `POST /logout`

## Error

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "request"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

## Root Cause

FastAPI versions before 0.95.0 don't correctly distinguish between:
1. `request: Request` - FastAPI's special type for HTTP request object
2. `request: str` - A regular query/body parameter

## Solution

### Option 1: Upgrade FastAPI (RECOMMENDED)

Upgrade to FastAPI 0.95.0 or later which fixes this issue.

**Steps**:
1. Update `RetailPolicyAssistant/requirements.txt`:
   ```diff
   - fastapi==0.139.0
   + fastapi==0.100.0
   ```

2. Reinstall dependencies:
   ```bash
   cd RetailPolicyAssistant
   pip install -r requirements.txt --upgrade
   ```

3. Restart backend:
   ```bash
   python -m uvicorn app.main:app --host localhost --port 8001
   ```

### Option 2: Remove Unused Request Parameters

If Request objects are not actually used in the endpoints, remove them:

**Before**:
```python
from fastapi import APIRouter, Depends, Request
from fastapi.requests import Request

@router.get("")
async def get_dashboard_data(
    request: Request,  # ← This causes the issue
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

**After**:
```python
from fastapi import APIRouter, Depends

@router.get("")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

**Files to Update**:
- `RetailPolicyAssistant/app/routers/dashboard.py` - Line 14-15
- `RetailPolicyAssistant/app/routers/observability.py` - Line 15-16
- `RetailPolicyAssistant/app/api.py` - Line 240-244 (POST /ask endpoint)

### Option 3: Use Explicit Type Handling

If the Request object is needed, explicitly type it:

```python
from fastapi import APIRouter, Depends, Request

@router.get("")
async def get_observability_metrics(
    request: Request,  # Explicitly imported from fastapi
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Request object will be injected by FastAPI
    # and NOT treated as a query parameter
    pass
```

Then ensure you're importing Request from the correct location:
```python
from fastapi import Request  # ← Correct
# NOT: from starlette.requests import Request
```

## Verification

After applying the fix:

1. Test the dashboard endpoint:
   ```bash
   curl -s http://localhost:8001/api/dashboard \
     -H "Authorization: Bearer <token>" \
     | jq .
   ```

2. Should return 200 with data (not 422 validation error):
   ```json
   {
     "totalQueries": 0,
     "avgLatency": 0,
     "escalationRate": 0,
     ...
   }
   ```

3. Test all affected endpoints:
   - `GET /api/dashboard` → 200 ✅
   - `GET /api/observability` → 200 ✅
   - `POST /ask` → 200 ✅
   - `POST /logout` → 200 ✅

## Applied Workaround

Currently, the following workaround has been applied:

**File**: `RetailPolicyAssistant/app/routers/dashboard.py`
```python
from fastapi import Request
@router.get("")
async def get_dashboard_data(
    request: Request,  # Added as workaround
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

**File**: `RetailPolicyAssistant/app/routers/observability.py`
```python
from fastapi import Request
@router.get("")
async def get_observability_metrics(
    request: Request,  # Added as workaround
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

This workaround is NOT permanent and should be replaced with one of the solutions above.

## Testing After Fix

Run the integration test suite:

```bash
python3 << 'EOF'
import requests

session = requests.Session()

# Auth
session.post("http://localhost:8001/token")

# Test fixed endpoints
endpoints = [
    ("GET", "http://localhost:8001/api/dashboard"),
    ("GET", "http://localhost:8001/api/observability"),
    ("POST", "http://localhost:8001/ask", {"query": "test"}),
    ("POST", "http://localhost:8001/logout"),
]

for method, url, *payload in endpoints:
    data = payload[0] if payload else None
    if method == "GET":
        resp = session.get(url)
    else:
        resp = session.post(url, json=data)
    
    print(f"{method:4} {url.split('/')[-1]:15} → {resp.status_code}")
EOF
```

Expected output:
```
GET  dashboard        → 200
GET  observability    → 200
POST /ask             → 200
POST logout           → 200
```

## References

- FastAPI Issue: https://github.com/tiangolo/fastapi/issues/5177
- Fixed in FastAPI 0.95.0+
- Related: https://github.com/tiangolo/fastapi/pull/5179
