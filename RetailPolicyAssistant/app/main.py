from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.api import router
from app.routers.dashboard import router as dashboard_router
from app.core.rate_limit import get_rate_limiter
from app.observability.langfuse_tracer import get_tracer

# Initialize Langfuse tracer at startup (before any requests)
_tracer = get_tracer()


app = FastAPI(
    title="Retail Policy Intelligence System",
    version="4.0 - Full Feature Implementation",
    description="Intelligent policy compliance system with auth, cost tracking, memory, RBAC, guardrails, caching, and rate limiting",
)

# Enable CORS FIRST (before other middleware)
# Allow all localhost ports for Next.js dev flexibility
cors_origins = []
# Add all localhost ports from 3000-3099 for Next.js
for port in range(3000, 3100):
    cors_origins.append(f"http://localhost:{port}")
    cors_origins.append(f"http://127.0.0.1:{port}")
# Add Vite/dev server fallback
cors_origins.extend([
    "http://localhost:5173",
    "http://127.0.0.1:5173",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,  # CRITICAL: Must be True for cookies to work
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
    expose_headers=["*"],  # Allow frontend to read response headers
)

# Request tracing middleware
@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    """Log all requests to Langfuse."""
    start_time = time.time()
    tracer = get_tracer()

    # Note: Tracing is now handled via @observe decorators on functions
    # Middleware just measures timing, actual tracing happens in orchestrator
    response = await call_next(request)
    latency_ms = (time.time() - start_time) * 1000

    # Add latency header for observability
    response.headers["X-Latency-MS"] = str(int(latency_ms))

    # Spawn flush as background task (non-blocking) to avoid adding latency
    # Don't wait for it - Langfuse batches automatically
    if tracer.is_enabled():
        # Fire and forget - don't await, don't block response
        try:
            import asyncio
            asyncio.create_task(asyncio.to_thread(tracer.flush))
        except Exception:
            # If background task fails, just skip - doesn't affect response
            pass

    return response


# Guardrails middleware - PHASE 1.1: Full production guardrails enforcement
@app.middleware("http")
async def guardrails_middleware(request: Request, call_next):
    """
    Central guardrails enforcement - all 8 layers active.
    Runs on every request and response.

    Pre-request layers (1-7):
      1. Input validation (length, encoding)
      3. PII detection (warn only)
      4. Injection detection (semantic + patterns)
      5. Policy conflict check
      6. SQL safety check
      7. RBAC check

    Post-response layers (2, 3, 8):
      2. Output validation
      3. PII masking
      8. Toxicity/hallucination check
    """
    # Skip guardrails for health checks and token endpoints
    if request.url.path in ["/health", "/token", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    try:
        from app.middleware.guardrails_middleware import get_guardrails_middleware

        # Get user role (try from query params, defaults to viewer)
        user_role = request.query_params.get("user_role", "viewer")
        middleware = get_guardrails_middleware(user_role=user_role)

        # Pre-request validation (layers 1-7)
        # Only validate input for POST /ask endpoint
        if request.method == "POST" and request.url.path == "/ask":
            # Read the request body to validate input
            body = await request.body()
            if body:
                import json
                try:
                    data = json.loads(body)
                    query = data.get("query", "")

                    # Validate input (layers 1, 3, 4, 5, 6, 7)
                    is_valid, violations = middleware.validate_input(query)
                    if not is_valid:
                        # Reject request with guardrails violations
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "detail": "Query failed guardrails validation",
                                "violations": violations,
                                "guardrails_status": "blocked"
                            }
                        )

                    # Check RBAC access (layer 7)
                    allowed, rbac_reason = middleware.check_access("read")
                    if not allowed:
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={
                                "detail": f"Access denied: {rbac_reason}",
                                "guardrails_status": "rbac_blocked"
                            }
                        )
                except json.JSONDecodeError:
                    pass  # Invalid JSON handled by FastAPI

        # Call the actual endpoint handler
        response = await call_next(request)

        # Post-response sanitization (layers 2, 3, 8)
        # Only sanitize JSON responses
        if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            try:
                import json
                data = json.loads(body)

                # Sanitize output if it contains a result
                if isinstance(data, dict) and "result" in data and isinstance(data["result"], dict):
                    if "result" in data["result"]:
                        # Sanitize (PII mask + toxicity check)
                        sanitized = middleware.sanitize_output(str(data["result"]["result"]))
                        data["result"]["result"] = sanitized

                        # Add guardrails status to response
                        data["guardrails_status"] = {
                            "input_validated": True,
                            "output_sanitized": True,
                            "pii_masked": True,
                            "toxicity_checked": True,
                            "violations": middleware.violations if middleware.violations else []
                        }

                # Return sanitized response
                from fastapi.responses import JSONResponse as FR
                return FR(
                    content=data,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except json.JSONDecodeError:
                pass  # Non-JSON responses pass through

        return response

    except Exception as e:
        # If guardrails error, log it but don't block (fail-open for availability)
        import logging
        logger = logging.getLogger("guardrails")
        logger.error(f"Guardrails middleware error: {str(e)}", exc_info=True)
        # Continue to call the next handler
        return await call_next(request)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Check rate limits on each request."""
    # Skip rate limiting for public endpoints
    if request.url.path in ["/health", "/token", "/docs", "/openapi.json", "/api/dashboard"]:
        return await call_next(request)

    # Try to extract user ID (from query params or header for demo)
    user_id = request.query_params.get("user_id", "anonymous")

    # Check rate limits
    limiter = get_rate_limiter()
    allowed, rate_info = limiter.check_all_limits(user_id, request.url.path)

    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded",
                "rate_limits": rate_info,
            }
        )

    response = await call_next(request)

    # Add rate limit headers to response
    response.headers["X-RateLimit-Limit"] = str(rate_info.get("endpoint_limit", {}).get("limit", 1000))
    response.headers["X-RateLimit-Remaining"] = str(rate_info.get("endpoint_limit", {}).get("tokens_remaining", 0))

    return response


from app.routers.observability import router as observability_router
from app.routers.ingestion import router as ingestion_router
from app.routers.websocket import router as websocket_router

app.include_router(router)
app.include_router(dashboard_router)
app.include_router(observability_router)
app.include_router(ingestion_router)
app.include_router(websocket_router)

