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

# Request tracing middleware
@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    """Log all requests to Langfuse."""
    start_time = time.time()
    tracer = get_tracer()

    # Extract user info from header if available
    auth_header = request.headers.get("Authorization", "")
    user_id = auth_header.split()[-1][:20] if auth_header else "anonymous"

    # Create trace for request
    trace = tracer.create_trace(
        name=f"http-{request.method}-{request.url.path}",
        user_id=user_id,
        metadata={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        }
    )

    response = await call_next(request)
    latency_ms = (time.time() - start_time) * 1000

    # Log response details
    tracer.create_span(
        trace,
        "http-response",
        input_data={"method": request.method, "path": request.url.path},
        output_data={"status_code": response.status_code, "latency_ms": latency_ms},
    )

    response.headers["X-Trace-ID"] = str(trace)
    tracer.flush()

    return response


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Check rate limits on each request."""
    # Skip rate limiting for public endpoints
    if request.url.path in ["/health", "/token", "/docs", "/openapi.json"]:
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


# Enable CORS for Next.js frontend (development mode)
# In production, replace with actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server (primary)
        "http://127.0.0.1:3000",  # Next.js localhost
        "http://localhost:5173",  # Vite dev server (fallback)
        "http://127.0.0.1:5173",  # Vite localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

app.include_router(router)
app.include_router(dashboard_router)

