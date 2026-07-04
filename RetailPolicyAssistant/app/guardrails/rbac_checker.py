"""RBAC Checker - Layer 7: Role-Based Access Control."""


class RBACChecker:
    """Checks role-based access control."""

    ROLE_PERMISSIONS = {
        "admin": ["read", "write", "delete", "approve"],
        "compliance_officer": ["read", "write", "approve"],
        "viewer": ["read"],
    }

    def __init__(self, user_role: str = "viewer"):
        self.user_role = user_role

    def check(self, action: str) -> dict:
        """Check if user has permission."""
        permissions = self.ROLE_PERMISSIONS.get(self.user_role, [])
        allowed = action in permissions

        return {
            "allowed": allowed,
            "role": self.user_role,
            "available_actions": permissions,
        }
