import re
import inspect
from typing import List, Any, Type
from ..utils.logging_config import get_logger
from ..agents.base import Agent, AgentResult

logger = get_logger(__name__)

class AdministrationGuard:
    """
    🛡️ P-ADM-01: Administrative Reliability Guard.
    
    Prevents bureaucratic friction by enforcing strict standards on 
    Administrative Agents and their execution environment.
    """

    @staticmethod
    def validate_agent_integrity(agent_class: Type[Agent]) -> List[str]:
        """
        Verifies that an agent class implements the required abstract methods
        and adheres to docstring standards.
        """
        issues = []
        
        # 1. Check abstract implementation
        abstract_methods = getattr(agent_class, "__abstractmethods__", set())
        if abstract_methods:
            issues.append(f"Missing implementation for abstract methods: {list(abstract_methods)}")

        # 2. Check docstring standards
        if not agent_class.__doc__ or "Responsibility" not in agent_class.__doc__:
            issues.append("Agent class must have a docstring containing 'Responsibility' section.")
            
        return issues

    @staticmethod
    def check_environment_sync(command: str) -> List[str]:
        """
        Ensures build commands are cross-platform compatible.
        Specific to preventing Linux '&&' usage in Windows environments (P-ADM-01 violation).
        """
        issues = []
        if "&&" in command:
            issues.append("⚠️ P-ADM-01 Violation: Found Linux-style '&&'. Use ';' for cross-platform compatibility.")
        
        return issues

    @staticmethod
    def audit_agent_result(result: AgentResult) -> bool:
        """
        Ensures agent responses are not empty or nonsensical.
        """
        if not result.analysis or len(result.analysis) < 10:
            logger.warning(f"Agent {result.agent_id} provided suspicious empty analysis.")
            return False
        return True
