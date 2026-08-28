from enum import Enum
from typing import List, Dict, Set


class Role(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


# Permissions mapped to each role
ROLE_PERMISSIONS: Dict[Role, Set[str]] = {
    Role.VIEWER: {
        "read:findings",
        "read:scans",
        "read:dashboard",
        "read:profile",
    },
    Role.ANALYST: {
        "read:findings",
        "read:scans",
        "read:dashboard",
        "read:profile",
        "create:scan",
        "trigger:investigation",
    },
    Role.ADMIN: {
        "read:findings",
        "read:scans",
        "read:dashboard",
        "read:profile",
        "create:scan",
        "trigger:investigation",
        "manage:users",
        "manage:roles",
        "manage:fingerprints",
    },
}


def has_permission(user_role: str, permission: str) -> bool:
    try:
        role_enum = Role(user_role.lower())
        return permission in ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        return False
