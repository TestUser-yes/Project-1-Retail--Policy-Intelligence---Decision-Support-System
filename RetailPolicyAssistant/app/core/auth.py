"""Authentication and authorization module."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.authentication import AuthCredentials
import os
from app.config import get_config

# Get configuration
_config = get_config()
SECRET_KEY = _config.auth.secret_key
ALGORITHM = _config.auth.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = _config.auth.access_token_expire_minutes

security = HTTPBearer()


class User:
    """User model for demo purposes."""

    def __init__(self, user_id: str, username: str, email: str, role: str = "user"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role  # "admin", "user", "compliance_officer"


def create_access_token(user_id: str, username: str, email: str, role: str = "user"):
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials = Depends(security)) -> User:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

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
    """Generate demo token for testing."""
    config = get_config()
    return create_access_token(
        user_id=config.auth.demo_user_id,
        username=config.auth.demo_username,
        email=config.auth.demo_email,
        role=config.auth.demo_role
    )


def get_admin_token() -> str:
    """Generate admin token for testing."""
    config = get_config()
    return create_access_token(
        user_id=config.auth.admin_user_id,
        username=config.auth.admin_username,
        email=config.auth.admin_email,
        role=config.auth.admin_role
    )
