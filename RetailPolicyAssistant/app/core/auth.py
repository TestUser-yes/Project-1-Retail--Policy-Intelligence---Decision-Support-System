"""Authentication and authorization module with refresh token support."""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status
import hashlib
from app.config import get_config

# Get configuration
_config = get_config()
SECRET_KEY = _config.auth.secret_key
ALGORITHM = _config.auth.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = _config.auth.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = getattr(_config.auth, 'refresh_token_expire_days', 7)

# In-memory refresh token store (in production, use Redis or database)
_refresh_token_store: Dict[str, Dict] = {}


class User:
    """User model for demo purposes."""

    def __init__(self, user_id: str, username: str, email: str, role: str = "user"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role  # "admin", "user", "compliance_officer"


def create_access_token(user_id: str, username: str, email: str, role: str = "user", expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with expiration."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "exp": expire,
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str, username: str, email: str, role: str = "user") -> str:
    """Create JWT refresh token with longer expiration."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "exp": expire,
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Store refresh token metadata for revocation support
    token_hash = hashlib.sha256(encoded_jwt.encode()).hexdigest()
    _refresh_token_store[token_hash] = {
        "user_id": user_id,
        "issued_at": datetime.utcnow(),
        "expires_at": expire,
        "active": True,
    }

    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type matches
        if payload.get("type") != token_type:
            raise JWTError("Token type mismatch")

        # For refresh tokens, check if revoked
        if token_type == "refresh":
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if token_hash not in _refresh_token_store:
                raise JWTError("Refresh token not found or revoked")

            token_data = _refresh_token_store[token_hash]
            if not token_data.get("active"):
                raise JWTError("Refresh token has been revoked")

        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def refresh_access_token(refresh_token: str) -> str:
    """Create new access token from refresh token."""
    payload = verify_token(refresh_token, token_type="refresh")

    user_id = payload.get("user_id")
    username = payload.get("username")
    email = payload.get("email")
    role = payload.get("role", "user")

    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Create new access token
    return create_access_token(user_id, username, email, role)


def revoke_refresh_token(refresh_token: str) -> bool:
    """Revoke a refresh token."""
    try:
        # Verify token is valid first
        verify_token(refresh_token, token_type="refresh")

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        if token_hash in _refresh_token_store:
            _refresh_token_store[token_hash]["active"] = False
            return True
        return False
    except HTTPException:
        return False


async def get_current_user(request) -> User:
    """Get current user from JWT token - supports both Bearer auth and secure cookies.

    Priority order:
    1. Authorization: Bearer <token> header (for API clients)
    2. access_token cookie (for browser/frontend)
    """
    token = None

    # Try to get token from Authorization header (Bearer auth)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]

    # If no header token, try to get from secure cookie
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token, token_type="access")

    user_id = payload.get("user_id")
    username = payload.get("username")
    email = payload.get("email")
    role = payload.get("role", "user")

    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return User(user_id=user_id, username=username, email=email, role=role)


def get_demo_token() -> str:
    """Generate demo access token for testing."""
    config = get_config()
    return create_access_token(
        user_id=config.auth.demo_user_id,
        username=config.auth.demo_username,
        email=config.auth.demo_email,
        role=config.auth.demo_role
    )


def get_demo_refresh_token() -> str:
    """Generate demo refresh token for testing."""
    config = get_config()
    return create_refresh_token(
        user_id=config.auth.demo_user_id,
        username=config.auth.demo_username,
        email=config.auth.demo_email,
        role=config.auth.demo_role
    )


def get_admin_token() -> str:
    """Generate admin access token for testing."""
    config = get_config()
    return create_access_token(
        user_id=config.auth.admin_user_id,
        username=config.auth.admin_username,
        email=config.auth.admin_email,
        role=config.auth.admin_role
    )


def get_admin_refresh_token() -> str:
    """Generate admin refresh token for testing."""
    config = get_config()
    return create_refresh_token(
        user_id=config.auth.admin_user_id,
        username=config.auth.admin_username,
        email=config.auth.admin_email,
        role=config.auth.admin_role
    )
