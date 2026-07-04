# Phase 7 Frontend Integration Guide

**Quick Start:** All Phase 7 components are built and ready to use. This guide shows how to integrate them into your layout and connect to backend APIs.

---

## 1. Add Sidebar to Layout

Update your root layout to include the new unified sidebar:

**File:** `frontend-nextjs/app/layout.tsx`

```tsx
import Sidebar from '@/app/components/Sidebar';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Sidebar />
        {/* Add margin to account for sidebar on desktop */}
        <main className="md:ml-64">
          {children}
        </main>
      </body>
    </html>
  );
}
```

**Result:** Sidebar appears on all pages with active route highlighting

---

## 2. Response Formatter in Query Page

The query page has been updated to use the new ResponseFormatter. Verify it's working:

**File:** `frontend-nextjs/app/query/page.tsx` (Already Updated ✅)

**Current implementation:**
```tsx
import ResponseFormatter from '@/app/components/ResponseFormatter';

// In component:
{result && (
  <ResponseFormatter result={result} onEscalate={handleEscalate} />
)}
```

**What it displays:**
- Structured AI response with all metadata
- Confidence, Risk, Retrieval Mode, Policy Sources
- SQL Validation section
- Recommendation and Reasoning
- Escalation button for high-risk cases

---

## 3. Connect Policy Explorer to Backend

**File:** `frontend-nextjs/app/policy-explorer/page.tsx`

**Current:** Uses mock data (7 hardcoded policies)

**To connect to backend:**

```tsx
// At top of component
const [policies, setPolicies] = useState<Policy[]>([]);
const [loading, setLoading] = useState(true);

// In useEffect:
useEffect(() => {
  const fetchPolicies = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/knowledge-base/policies`);
      const data = await response.json();
      setPolicies(data);
    } catch (err) {
      console.error('Failed to load policies:', err);
    } finally {
      setLoading(false);
    }
  };
  fetchPolicies();
}, []);

// Replace POLICIES constant with policies state
```

**Expected API response:**
```json
{
  "policies": [
    {
      "id": "policy-1",
      "title": "Policy Title",
      "category": "Category",
      "version": "1.0",
      "effectiveDate": "2025-01-01",
      "sections": 8,
      "clauses": 24,
      "status": "active",
      "description": "..."
    }
  ]
}
```

---

## 4. Connect Escalation Center to Backend

**File:** `frontend-nextjs/app/escalation-center/page.tsx`

**Current:** Uses mock data (4 sample cases)

**To connect to backend:**

```tsx
// In useEffect or async function:
const loadCases = async () => {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const queryParams = new URLSearchParams();
    
    if (selectedTeam !== 'All Teams') queryParams.append('team', selectedTeam);
    if (selectedStatus !== 'All Statuses') queryParams.append('status', selectedStatus);
    if (searchTerm) queryParams.append('search', searchTerm);
    
    const response = await fetch(
      `${apiUrl}/api/escalations?${queryParams}`
    );
    const data = await response.json();
    setFilteredCases(data.cases);
  } catch (err) {
    console.error('Failed to load cases:', err);
  }
};
```

**Expected API response:**
```json
{
  "cases": [
    {
      "id": "1",
      "caseNumber": "E-1004",
      "question": "...",
      "reason": "...",
      "risk": "HIGH",
      "confidence": 63,
      "assignedTeam": "Legal Team",
      "status": "pending",
      "createdAt": "2026-01-15",
      "conversation": [...],
      "policiesApplied": [...],
      "sqlValidation": {...},
      "reasoning": "..."
    }
  ]
}
```

---

## 5. Connect Observability Dashboard to Backend

**File:** `frontend-nextjs/app/observability/page.tsx`

**Current:** Uses mock data with realistic metrics

**To connect to backend:**

```tsx
// In useEffect:
const loadObservability = async () => {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/observability`);
    
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    
    const data = await response.json();
    setData(data);
  } catch (err) {
    console.error('Failed to load observability:', err);
    // Falls back to mock data
  }
};
```

**Expected API response:**
```json
{
  "totalQueries": 1245,
  "avgConfidence": 92,
  "avgLatency": 2.1,
  "escalationRate": 8,
  "avgCost": 0.045,
  "intentDistribution": [...],
  "riskDistribution": [...],
  "queryTypeDistribution": [...],
  "latencyTrend": [...],
  "confidenceTrend": [...],
  "langfuseTraces": [...]
}
```

---

## 6. Connect Evaluation Page to Backend

**File:** `frontend-nextjs/app/evaluation/page.tsx`

**Current:** Displays mock evaluation results

**To connect to backend:**

```tsx
// When file is uploaded and user clicks "Run Evaluation":
const handleRunEvaluation = async () => {
  if (!selectedFile) return;
  
  setEvaluationRunning(true);
  
  try {
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/evaluation`, {
      method: 'POST',
      body: formData,
    });
    
    const result = await response.json();
    setEvaluationResult(result);
  } catch (err) {
    console.error('Evaluation failed:', err);
  } finally {
    setEvaluationRunning(false);
  }
};
```

**Expected API response:**
```json
{
  "timestamp": "2026-01-20T14:30:00Z",
  "queryCount": 50,
  "metrics": [
    {
      "name": "Task Success Rate (TSR)",
      "value": 94,
      "target": 90,
      "unit": "%",
      "status": "pass"
    }
  ],
  "detailedResults": [
    {
      "queryId": "Q-001",
      "query": "...",
      "expected": "...",
      "actual": "...",
      "match": true,
      "confidence": 94,
      "latency": 2.1
    }
  ]
}
```

---

## 7. ResponseFormatter Component Usage

Use in your query results or any response display:

```tsx
import ResponseFormatter from '@/app/components/ResponseFormatter';

<ResponseFormatter 
  result={response}
  onEscalate={() => handleEscalation(response)}
/>
```

**Props:**
- `result: AskResponse` - Your query response object
- `onEscalate?: () => void` - Callback when escalation button clicked

**Expected result structure:**
```ts
{
  query: string;
  result: string | { result: string };
  confidence_score: number;
  risk: { risk_level: string; reason?: string };
  route: 'rag' | 'sql' | 'hybrid';
  sources: Array<string | { source: string; section?: string; page?: number }>;
  sql_validation?: string | { query: string; status: string; result: any };
  recommendation?: string;
  escalate?: boolean;
  escalation_reason?: string;
  intent?: { intent: string };
}
```

---

## 8. Environment Variables

Ensure your `.env.local` has the API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Or for production:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## 9. Testing Without Backend

All components work with mock data for testing:

1. **Policy Explorer** - Shows 7 policies
2. **Escalation Center** - Shows 4 sample cases
3. **Observability** - Shows realistic metrics
4. **Evaluation** - Shows sample results
5. **Response Formatter** - Display only (needs real response)

You can:
- Test UI/UX without backend
- Verify responsive design
- Check styling and interactions
- Prepare demo before APIs are ready

---

## 10. Deployment Checklist

- [ ] All components render without errors
- [ ] Sidebar displays on all pages with correct active states
- [ ] ResponseFormatter shows in query results
- [ ] Policy Explorer loads and searches work
- [ ] Escalation Center filters and expandable cases work
- [ ] Observability displays charts correctly
- [ ] Evaluation page accepts file uploads
- [ ] API endpoints are connected and working
- [ ] Error handling works (timeout, network errors, etc.)
- [ ] Mobile responsiveness verified
- [ ] Performance is acceptable (< 3s page loads)

---

## 11. Common Issues & Solutions

**Issue:** Sidebar not showing  
**Solution:** Verify `Sidebar` is imported in RootLayout and `md:ml-64` is added to main content

**Issue:** API responses return 404  
**Solution:** Check `NEXT_PUBLIC_API_URL` env variable and backend route paths

**Issue:** Charts not rendering  
**Solution:** Verify ResponsiveContainer has parent with defined height

**Issue:** Mobile menu not closing  
**Solution:** Ensure `onClick={() => setIsOpen(false)}` is on all navigation links

---

## 12. Performance Tips

1. **Lazy load images** - Use Next.js Image component
2. **Memoize components** - Use React.memo for chart components
3. **Paginate large lists** - Escalation cases and audit logs
4. **Debounce search** - Add 300ms debounce to search inputs
5. **Cache API responses** - Use SWR or React Query for better caching

---

## 13. Next Features to Consider

After Phase 7:
- Real-time updates with WebSockets
- Dark mode toggle
- Export reports (PDF, CSV)
- Advanced filtering and sorting
- User preferences/settings
- Keyboard shortcuts
- Accessibility improvements

---

## 📞 Quick Reference

| Page | File | Status | Backend Ready |
|------|------|--------|---|
| Policy Explorer | `/policy-explorer/page.tsx` | ✅ | No, needs `/api/knowledge-base/policies` |
| Escalation Center | `/escalation-center/page.tsx` | ✅ | No, needs `/api/escalations` |
| Observability | `/observability/page.tsx` | ✅ | No, needs `/api/observability` |
| Evaluation | `/evaluation/page.tsx` | ✅ | No, needs `/api/evaluation` |
| Response Formatter | `/components/ResponseFormatter.tsx` | ✅ | Uses existing response |
| Sidebar | `/components/Sidebar.tsx` | ✅ | No backend needed |

---

**All Phase 7 components are production-ready. Integrate with your backend and you're done! 🎉**

