'use client';

import { Copy, ChevronDown, ExternalLink } from 'lucide-react';
import { useState } from 'react';

const CodeBlock = ({ code, language = 'json' }: { code: string; language?: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative bg-gray-900 rounded-lg p-4 overflow-x-auto">
      <button
        onClick={handleCopy}
        className="absolute top-3 right-3 p-2 hover:bg-gray-800 rounded transition"
        title="Copy to clipboard"
      >
        <Copy className="w-4 h-4 text-gray-400" />
      </button>
      <pre className="text-gray-300 text-sm font-mono">
        <code>{code}</code>
      </pre>
      {copied && <span className="absolute top-3 right-12 text-xs text-green-400">Copied!</span>}
    </div>
  );
};

const CollapsibleSection = ({ title, children }: { title: string; children: React.ReactNode }) => {
  const [open, setOpen] = useState(true);

  return (
    <div className="border-2 border-slate-200 rounded-lg mb-4">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition font-semibold text-gray-900"
      >
        <span>{title}</span>
        <ChevronDown className={`w-5 h-5 transition ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div className="p-4 border-t-2 border-slate-200 bg-slate-50">{children}</div>}
    </div>
  );
};

export default function APIDocs() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">API Documentation</h1>
          <p className="text-lg text-gray-600 mb-4">
            Complete guide to the Retail Policy Intelligence API for developers
          </p>
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <strong>Base URL:</strong> <code className="bg-white px-2 py-1 rounded">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</code>
            </p>
          </div>
        </div>

        {/* Overview */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Overview</h2>
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <p className="text-gray-700 mb-4">
              The Retail Policy Intelligence API provides intelligent policy compliance, vendor management, and escalation workflows powered by advanced AI agents. The API uses RESTful principles and returns JSON responses.
            </p>
            <h3 className="text-lg font-bold text-gray-900 mb-3">Key Features</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li><strong>Intelligent Routing:</strong> Automatically classifies queries and routes to appropriate handlers (RAG, SQL, Hybrid)</li>
              <li><strong>Risk Assessment:</strong> Comprehensive risk scoring with escalation detection</li>
              <li><strong>Cost Tracking:</strong> Real-time cost monitoring with budget management</li>
              <li><strong>SLO Monitoring:</strong> Service Level Objective tracking with latency metrics</li>
              <li><strong>Conversation Memory:</strong> Multi-turn conversation support with context awareness</li>
              <li><strong>Audit Trails:</strong> Complete audit logging for compliance</li>
            </ul>
          </div>
        </section>

        {/* Authentication */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Authentication</h2>
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <p className="text-gray-700 mb-4">
              The API uses JWT (JSON Web Token) authentication. All requests (except `/token` and `/health`) require a Bearer token in the Authorization header.
            </p>

            <h3 className="font-bold text-gray-900 mb-3">Getting a Token</h3>
            <p className="text-gray-700 mb-3">Call the `/token` endpoint to get an access token:</p>
            <CodeBlock
              code={`curl -X GET ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/token

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}`}
            />

            <h3 className="font-bold text-gray-900 mb-3 mt-6">Using the Token</h3>
            <p className="text-gray-700 mb-3">Include the token in all subsequent requests:</p>
            <CodeBlock
              code={`curl -X POST ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ask \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is our return policy?",
    "conversation_id": "conv-uuid-here"
  }'`}
            />
          </div>
        </section>

        {/* Endpoints */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Endpoints</h2>

          {/* GET /health */}
          <CollapsibleSection title="GET /health - Health Check">
            <p className="text-gray-700 mb-4">Returns the system health status.</p>
            <p className="font-semibold text-gray-900 mb-2">Response Example:</p>
            <CodeBlock
              code={`{
  "status": "healthy",
  "version": "4.0",
  "system": "Retail Policy AI",
  "agents": "active",
  "db": "connected",
  "timestamp": "2026-07-03"
}`}
            />
          </CollapsibleSection>

          {/* POST /ask */}
          <CollapsibleSection title="POST /ask - Submit Query (Requires Auth)">
            <p className="text-gray-700 mb-4">
              Submits a policy query for intelligent processing. This is the main endpoint that handles all query processing including intent detection, risk assessment, routing, and escalation.
            </p>

            <p className="font-semibold text-gray-900 mb-2">Request Schema:</p>
            <CodeBlock
              code={`{
  "query": "string (required, 3-10000 chars)",
  "conversation_id": "string (optional, UUID format)"
}`}
            />

            <p className="font-semibold text-gray-900 mb-2 mt-4">Response Schema:</p>
            <CodeBlock
              code={`{
  "query": "What is our return policy?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "intent": {
    "intent": "PolicyCompliance",
    "reason": "Query asks about specific retail policy"
  },
  "route": "rag",
  "result": {
    "result": "Our return policy allows for 30-day returns..."
  },
  "risk": {
    "risk_level": "Low",
    "reason": "Standard policy query, no escalation triggers"
  },
  "escalate": false,
  "escalation_reason": "",
  "latency_seconds": 1.68,
  "cost_usd": 0.0042,
  "budget_remaining_usd": 99.9958,
  "budget_percent_used": 0.004,
  "slo_metrics": {
    "latency_ms": 1680,
    "target_latency_ms": 2000,
    "slo_status": "pass"
  },
  "validation_passed": true
}`}
            />

            <p className="font-semibold text-gray-900 mb-2 mt-4">Example Request:</p>
            <CodeBlock
              code={`curl -X POST ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ask \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is our data retention policy?",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'`}
            />
          </CollapsibleSection>

          {/* GET /conversations/:id/history */}
          <CollapsibleSection title="GET /conversations/:id/history - Get Conversation History (Requires Auth)">
            <p className="text-gray-700 mb-4">
              Retrieves the complete message history for a specific conversation. Only accessible to the conversation owner or admins.
            </p>

            <p className="font-semibold text-gray-900 mb-2">Path Parameters:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4">
              <li><code className="bg-slate-100 px-1 rounded">conversation_id</code>: The UUID of the conversation</li>
            </ul>

            <p className="font-semibold text-gray-900 mb-2">Response Schema:</p>
            <CodeBlock
              code={`{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "What is our return policy?"
    },
    {
      "role": "assistant",
      "content": "Our return policy allows for 30-day returns..."
    }
  ]
}`}
            />

            <p className="font-semibold text-gray-900 mb-2 mt-4">Example Request:</p>
            <CodeBlock
              code={`curl -X GET ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/conversations/550e8400-e29b-41d4-a716-446655440000/history \\
  -H "Authorization: Bearer YOUR_TOKEN"`}
            />
          </CollapsibleSection>
        </section>

        {/* Query Routes */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Query Routes</h2>
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6 space-y-4">
            <div className="border-l-4 border-blue-600 pl-4">
              <h3 className="font-bold text-gray-900">RAG (Retrieval-Augmented Generation)</h3>
              <p className="text-gray-700 text-sm">
                Used for policy-based questions. Retrieves relevant policy documents and generates answers based on actual policy content.
              </p>
            </div>
            <div className="border-l-4 border-green-600 pl-4">
              <h3 className="font-bold text-gray-900">SQL (Database Query)</h3>
              <p className="text-gray-700 text-sm">
                Used for vendor and compliance data queries. Executes database queries to retrieve specific information about vendors, pricing, compliance status.
              </p>
            </div>
            <div className="border-l-4 border-amber-600 pl-4">
              <h3 className="font-bold text-gray-900">Hybrid (Combined)</h3>
              <p className="text-gray-700 text-sm">
                Uses both RAG and SQL for complex queries that require policy information combined with structured data.
              </p>
            </div>
          </div>
        </section>

        {/* Error Codes */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Error Codes</h2>
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <table className="w-full text-sm">
              <thead className="border-b-2 border-slate-200">
                <tr>
                  <th className="text-left py-2 px-3 font-semibold">Code</th>
                  <th className="text-left py-2 px-3 font-semibold">Meaning</th>
                  <th className="text-left py-2 px-3 font-semibold">Solution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr>
                  <td className="py-2 px-3 font-mono text-red-600">400</td>
                  <td className="py-2 px-3">Bad Request</td>
                  <td className="py-2 px-3 text-sm">Query validation failed. Check query length (3-10000 chars)</td>
                </tr>
                <tr>
                  <td className="py-2 px-3 font-mono text-red-600">401</td>
                  <td className="py-2 px-3">Unauthorized</td>
                  <td className="py-2 px-3 text-sm">Missing or invalid token. Get a new token from /token</td>
                </tr>
                <tr>
                  <td className="py-2 px-3 font-mono text-red-600">403</td>
                  <td className="py-2 px-3">Forbidden</td>
                  <td className="py-2 px-3 text-sm">Insufficient permissions for this action</td>
                </tr>
                <tr>
                  <td className="py-2 px-3 font-mono text-red-600">429</td>
                  <td className="py-2 px-3">Too Many Requests</td>
                  <td className="py-2 px-3 text-sm">Rate limit exceeded. Default: 50 queries/hour per user</td>
                </tr>
                <tr>
                  <td className="py-2 px-3 font-mono text-red-600">500</td>
                  <td className="py-2 px-3">Internal Server Error</td>
                  <td className="py-2 px-3 text-sm">Server error. Check backend health and try again</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Rate Limits */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Rate Limiting</h2>
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <table className="w-full text-sm mb-4">
              <thead className="border-b-2 border-slate-200">
                <tr>
                  <th className="text-left py-2 px-3 font-semibold">Limit</th>
                  <th className="text-left py-2 px-3 font-semibold">Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr>
                  <td className="py-2 px-3">Per-user /ask limit</td>
                  <td className="py-2 px-3 font-mono">50 queries/hour</td>
                </tr>
                <tr>
                  <td className="py-2 px-3">Global /ask limit</td>
                  <td className="py-2 px-3 font-mono">1000 queries/hour</td>
                </tr>
              </tbody>
            </table>
            <p className="text-gray-600 text-sm">
              Rate limit information is included in the response headers: <code className="bg-slate-100 px-1 rounded">X-RateLimit-Limit</code> and <code className="bg-slate-100 px-1 rounded">X-RateLimit-Remaining</code>
            </p>
          </div>
        </section>

        {/* Cost Tracking */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Cost Tracking</h2>
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <p className="text-gray-700 mb-4">
              The API tracks costs for each query. The `cost_usd` field in the response shows the cost for that specific query.
            </p>
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 mb-4">
              <p className="text-sm text-blue-900">
                <strong>Budget Information:</strong> Each response includes <code className="bg-white px-1 rounded">budget_remaining_usd</code> and <code className="bg-white px-1 rounded">budget_percent_used</code> for real-time budget monitoring.
              </p>
            </div>
            <h3 className="font-bold text-gray-900 mb-2">Default Limits</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1">
              <li>Max per query: $1.00</li>
              <li>Daily budget: $100</li>
              <li>Monthly budget: $2,000</li>
            </ul>
          </div>
        </section>

        {/* Code Examples */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Code Examples</h2>

          <CollapsibleSection title="JavaScript / TypeScript">
            <CodeBlock
              code={`import axios from 'axios';

const API_URL = '${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}';

async function askPolicy(query) {
  // Get token
  const tokenRes = await axios.get(\`\${API_URL}/token\`);
  const token = tokenRes.data.access_token;

  // Submit query
  const response = await axios.post(
    \`\${API_URL}/ask\`,
    {
      query: query,
      conversation_id: crypto.randomUUID()
    },
    {
      headers: {
        'Authorization': \`Bearer \${token}\`,
        'Content-Type': 'application/json'
      }
    }
  );

  console.log('Response:', response.data);
  return response.data;
}

// Usage
askPolicy('What is our return policy?');`}
            />
          </CollapsibleSection>

          <CollapsibleSection title="Python">
            <CodeBlock
              code={`import requests
import uuid

API_URL = '${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}'

def ask_policy(query):
    # Get token
    token_res = requests.get(f'{API_URL}/token')
    token = token_res.json()['access_token']

    # Submit query
    response = requests.post(
        f'{API_URL}/ask',
        json={
            'query': query,
            'conversation_id': str(uuid.uuid4())
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )

    print('Response:', response.json())
    return response.json()

# Usage
ask_policy('What is our return policy?')`}
            />
          </CollapsibleSection>

          <CollapsibleSection title="cURL">
            <CodeBlock
              code={`# Step 1: Get token
TOKEN=$(curl -s ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/token | jq -r '.access_token')

# Step 2: Submit query
curl -X POST ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ask \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is our return policy?",
    "conversation_id": "'$(uuidgen)'"
  }' | jq .`}
            />
          </CollapsibleSection>
        </section>

        {/* Interactive Testing */}
        <section className="mb-12">
          <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-6">
            <h3 className="font-bold text-gray-900 mb-2">Interactive API Testing</h3>
            <p className="text-gray-700 text-sm mb-4">
              For interactive API testing and exploration, visit the Swagger UI:
            </p>
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition"
            >
              Open Swagger UI
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </section>

        {/* Support */}
        <section className="mb-12 text-center">
          <div className="bg-white rounded-lg border-2 border-slate-200 p-8">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Need Help?</h3>
            <p className="text-gray-700 mb-4">
              For questions or issues, please contact the development team or check the system health dashboard.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
