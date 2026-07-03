"""Role-Based Access Control (RBAC) and Permission Management

Defines roles, permissions, and enforcement mechanisms for access control.
"""

from typing import List, Set, Dict, Callable
from fastapi import Depends, HTTPException, status
from app.core.auth import User, get_current_user


# Permission definitions
class Permission:
    """Permission constants."""
    # Query permissions
    ASK_POLICY_QUESTION = "ask:policy"
    ASK_VENDOR_QUESTION = "ask:vendor"
    ASK_HYBRID_QUESTION = "ask:hybrid"

    # View permissions
    VIEW_QUERY_HISTORY = "view:query_history"
    VIEW_COSTS = "view:costs"
    VIEW_AUDIT_LOG = "view:audit_log"

    # Admin permissions
    MANAGE_USERS = "admin:users"
    MANAGE_ROLES = "admin:roles"
    VIEW_SYSTEM_METRICS = "admin:metrics"


# Role definitions
class Role:
    """Role definitions with associated permissions."""

    ROLES = {
        "user": {
            "description": "Standard user",
            "permissions": {
                Permission.ASK_POLICY_QUESTION,
                Permission.ASK_VENDOR_QUESTION,
                Permission.ASK_HYBRID_QUESTION,
                Permission.VIEW_QUERY_HISTORY,
            }
        },
        "compliance_officer": {
            "description": "Compliance specialist with elevated permissions",
            "permissions": {
                Permission.ASK_POLICY_QUESTION,
                Permission.ASK_VENDOR_QUESTION,
                Permission.ASK_HYBRID_QUESTION,
                Permission.VIEW_QUERY_HISTORY,
                Permission.VIEW_COSTS,
                Permission.VIEW_AUDIT_LOG,
            }
        },
        "admin": {
            "description": "System administrator with full access",
            "permissions": {
                Permission.ASK_POLICY_QUESTION,
                Permission.ASK_VENDOR_QUESTION,
                Permission.ASK_HYBRID_QUESTION,
                Permission.VIEW_QUERY_HISTORY,
                Permission.VIEW_COSTS,
                Permission.VIEW_AUDIT_LOG,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.VIEW_SYSTEM_METRICS,
            }
        },
    }

    @classmethod
    def get_permissions(cls, role: str) -> Set[str]:
        """Get all permissions for a role.

        Args:
            role: Role name

        Returns:
            Set of permission strings
        """
        if role not in cls.ROLES:
            return set()
        return cls.ROLES[role].get("permissions", set())

    @classmethod
    def list_roles(cls) -> List[str]:
        """List all available roles."""
        return list(cls.ROLES.keys())

    @classmethod
    def get_role_description(cls, role: str) -> str:
        """Get role description."""
        if role not in cls.ROLES:
            return "Unknown role"
        return cls.ROLES[role].get("description", "")


class PermissionValidator:
    """Validates user permissions."""

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has permission.

        Args:
            user: User object
            permission: Permission to check

        Returns:
            True if user has permission
        """
        user_permissions = Role.get_permissions(user.role)
        return permission in user_permissions

    @staticmethod
    def has_any_permission(user: User, permissions: List[str]) -> bool:
        """Check if user has ANY of the permissions.

        Args:
            user: User object
            permissions: List of permissions

        Returns:
            True if user has any permission
        """
        user_permissions = Role.get_permissions(user.role)
        return any(p in user_permissions for p in permissions)

    @staticmethod
    def has_all_permissions(user: User, permissions: List[str]) -> bool:
        """Check if user has ALL of the permissions.

        Args:
            user: User object
            permissions: List of permissions

        Returns:
            True if user has all permissions
        """
        user_permissions = Role.get_permissions(user.role)
        return all(p in user_permissions for p in permissions)

    @staticmethod
    def assert_permission(user: User, permission: str) -> None:
        """Assert user has permission, raise if not.

        Args:
            user: User object
            permission: Permission to check

        Raises:
            HTTPException: If user doesn't have permission
        """
        if not PermissionValidator.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )


# FastAPI Dependencies for permission-based access

def require_permission(permission: str) -> Callable:
    """Create a dependency that requires a specific permission.

    Args:
        permission: Permission string

    Returns:
        Dependency function
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        PermissionValidator.assert_permission(current_user, permission)
        return current_user
    return permission_checker


def require_role(*allowed_roles: str) -> Callable:
    """Create a dependency that requires specific roles.

    Args:
        *allowed_roles: Role names

    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role: {current_user.role}"
            )
        return current_user
    return role_checker


def require_admin() -> Callable:
    """Require admin role."""
    return require_role("admin")


def require_compliance_or_admin() -> Callable:
    """Require compliance officer or admin."""
    return require_role("compliance_officer", "admin")


# Access control helpers

def check_resource_access(user: User, resource_owner_id: str) -> bool:
    """Check if user can access a resource.

    Args:
        user: User object
        resource_owner_id: ID of resource owner

    Returns:
        True if user can access (owner or admin)
    """
    return user.user_id == resource_owner_id or user.role == "admin"


def assert_resource_access(user: User, resource_owner_id: str) -> None:
    """Assert user can access resource, raise if not.

    Args:
        user: User object
        resource_owner_id: ID of resource owner

    Raises:
        HTTPException: If access denied
    """
    if not check_resource_access(user, resource_owner_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not resource owner"
        )


# Audit logging helper
def log_access_check(user: User, permission: str, granted: bool, resource: str = None) -> Dict:
    """Create an audit log entry for access checks.

    Args:
        user: User object
        permission: Permission checked
        granted: Whether access was granted
        resource: Optional resource identifier

    Returns:
        Dict suitable for audit logging
    """
    return {
        "user_id": user.user_id,
        "role": user.role,
        "permission": permission,
        "granted": granted,
        "resource": resource,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


from datetime import datetime, timezone
