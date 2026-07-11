#!/bin/bash

# Multi-Agent System Test Script
# Run this after starting the FastAPI server to test all agent types

BASE_URL="http://localhost:8000"
TOKEN_URL="$BASE_URL/api/token"
ASK_URL="$BASE_URL/api/ask"
DEMO_URL="$BASE_URL/api/observability/demo-agents"
OBS_URL="$BASE_URL/api/observability"

echo "============================================"
echo "Multi-Agent System Demo Test"
echo "============================================"
echo ""

# Step 1: Get token
echo "Step 1: Getting demo token..."
TOKEN_RESPONSE=$(curl -s -X GET "$TOKEN_URL")
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"
echo ""

# Step 2: View demo endpoint
echo "Step 2: Viewing demo endpoint..."
echo "GET $DEMO_URL"
curl -s -X GET "$DEMO_URL" | python -m json.tool | head -50
echo ""
echo "... (truncated)"
echo ""

# Step 3: Test RAG Query
echo "============================================"
echo "Step 3: Testing RAG Agent (Policy Retrieval)"
echo "============================================"
echo ""
echo "Query: 'What is the data retention policy?'"
echo ""
RAG_RESPONSE=$(curl -s -X POST "$ASK_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the data retention policy?"}')

echo "Response:"
echo $RAG_RESPONSE | python -m json.tool 2>/dev/null || echo $RAG_RESPONSE

# Extract agent info
AGENTS_USED=$(echo $RAG_RESPONSE | grep -o '"agents_used":\[[^]]*\]')
AGENT_DETAILS=$(echo $RAG_RESPONSE | grep -o '"agent_details":\[[^]]*}.*\]')
echo ""
echo "Agents Used: $AGENTS_USED"
echo ""

# Step 4: Test SQL Query
echo ""
echo "============================================"
echo "Step 4: Testing SQL Agent (Database Query)"
echo "============================================"
echo ""
echo "Query: 'How many vendors do we have?'"
echo ""
SQL_RESPONSE=$(curl -s -X POST "$ASK_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vendors do we have?"}')

echo "Response:"
echo $SQL_RESPONSE | python -m json.tool 2>/dev/null || echo $SQL_RESPONSE

AGENTS_USED=$(echo $SQL_RESPONSE | grep -o '"agents_used":\[[^]]*\]')
echo ""
echo "Agents Used: $AGENTS_USED"
echo ""

# Step 5: Test Hybrid Query
echo ""
echo "============================================"
echo "Step 5: Testing Hybrid Mode (Both Agents)"
echo "============================================"
echo ""
echo "Query: 'Which vendors comply with our encryption policy?'"
echo ""
HYBRID_RESPONSE=$(curl -s -X POST "$ASK_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which vendors comply with our encryption policy?"}')

echo "Response:"
echo $HYBRID_RESPONSE | python -m json.tool 2>/dev/null || echo $HYBRID_RESPONSE

AGENTS_USED=$(echo $HYBRID_RESPONSE | grep -o '"agents_used":\[[^]]*\]')
echo ""
echo "Agents Used: $AGENTS_USED"
echo ""

# Step 6: View observability stats
echo ""
echo "============================================"
echo "Step 6: Viewing Observability Stats"
echo "============================================"
echo ""
echo "GET $OBS_URL"
OBS_RESPONSE=$(curl -s -X GET "$OBS_URL")
MULTI_AGENT_SUMMARY=$(echo $OBS_RESPONSE | grep -o '"multi_agent_summary":{[^}]*}')
echo ""
echo "Multi-Agent Summary:"
echo $MULTI_AGENT_SUMMARY | python -m json.tool 2>/dev/null || echo $MULTI_AGENT_SUMMARY
echo ""

echo ""
echo "============================================"
echo "Demo Complete!"
echo "============================================"
echo ""
echo "Key Points Demonstrated:"
echo "✓ RAG Agent - Retrieved from PDF documents"
echo "✓ SQL Agent - Queried database"
echo "✓ Hybrid Mode - Used both agents in parallel"
echo "✓ Agent Details - Latency, confidence, and data source visible"
echo "✓ Observability - Routing statistics tracked"
echo ""
echo "For full trace visualization, check LangFuse dashboard:"
echo "https://cloud.langfuse.com"
echo ""
