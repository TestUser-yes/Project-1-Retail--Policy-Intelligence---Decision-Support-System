from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import router
from app.core.rate_limit import get_rate_limiter


app = FastAPI(
    title="Retail Policy Intelligence System",
    version="4.0 - Full Feature Implementation",
    description="Intelligent policy compliance system with auth, cost tracking, memory, RBAC, guardrails, caching, and rate limiting",
)

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


# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

app.include_router(router)

