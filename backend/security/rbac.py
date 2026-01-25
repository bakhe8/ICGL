from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class Permission:
    resource: str
    action: str  # read, write, execute


@dataclass
class Role:
    name: str
    permissions: Set[str] = field(default_factory=set)

    def add_perm(self, resource: str, action: str):
        self.permissions.add(f"{resource}:{action}")


class AccessControl:
    """
    Implements Sovereign Alignment (Mandate 4: RBAC).
    Controls who can do what.
    """

    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, str] = {}  # user_id -> role_name
        self._bootstrap()

    def _bootstrap(self):
        # 1. Sovereign (Root)
        sovereign = Role("sovereign")
        sovereign.add_perm("*", "*")
        self.roles["sovereign"] = sovereign

        # 2. Agent (Standard)
        agent = Role("agent")
        agent.add_perm("bus", "publish")
        agent.add_perm("kb", "read")
        self.roles["agent"] = agent

        # 3. Executive (High Privilege)
        exec_role = Role("executive")
        exec_role.add_perm("fs", "write")
        exec_role.add_perm("bus", "publish")
        self.roles["executive"] = exec_role

    def check_access(self, role_name: str, resource: str, action: str) -> bool:
        if role_name not in self.roles:
            return False

        role = self.roles[role_name]

        # Superuser check
        if "*:*" in role.permissions:
            return True

        perm = f"{resource}:{action}"
        return perm in role.permissions


# Global Access Controller
rbac = AccessControl()
