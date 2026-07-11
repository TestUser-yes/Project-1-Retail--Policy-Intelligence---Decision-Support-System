from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.api import router
from app.routers.dashboard import router as dashboard_router
from app.core.rate_limit import get_rate_limiter
from app.observability.langfuse_tracer import get_tracer


app = FastAPI(
    title="Retail Policy Intelligence System",
    version="4.0 - Full Feature Implementation",
    description="Intelligent policy compliance system with auth, cost tracking, memory, RBAC, guardrails, caching, and rate limiting",
)

# Enable CORS FIRST (before other middleware)
# Allow all localhost:30xx ports since Next.js auto-assigns ports
import re
cors_origins = []
# Add all localhost ports from 3000-3099 for Next.js dev flexibility
for port in range(3000, 3100):
    cors_origins.append(f"http://localhost:{port}")
    cors_origins.append(f"http://127.0.0.1:{port}")
# Add Vite fallback
cors_origins.extend([
    "http://localhost:5173",
    "http://127.0.0.1:5173",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
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

app.include_router(router)
app.include_router(dashboard_router)
app.include_router(observability_router)
app.include_router(ingestion_router)

