"""
ICGL Agent Capability Checker
==============================

Prevents agent duplication by checking existing capabilities before creating new agents.
Enforces disciplined agent ecosystem expansion.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class AgentRecommendation(Enum):
    """Recommendation for agent creation."""

    CREATE_NEW = "create_new"
    ENHANCE_EXISTING = "enhance_existing"
    USE_EXISTING = "use_existing"


@dataclass
class CapabilityCheckResult:
    """Result of capability existence check."""

    exists: bool
    agents_with_capability: List[str]
    recommendation: AgentRecommendation
    rationale: str
    target_agent: Optional[str] = None  # Which agent to enhance/use


@dataclass
class AgentManifestEntry:
    """Entry in the agent manifest."""

    id: str
    file: str
    role: str
    capabilities: List[str]
    status: str
    enhancements: List[Dict[str, Any]] = field(default_factory=list)


class CapabilityChecker:
    """
    Prevents agent duplication by checking existing capabilities.

    Reads from backend/agents/manifest.yaml (if exists) or parses AGENTS.md

    Usage:
        checker = CapabilityChecker()
        result = checker.check_capability_exists("test_generation")

        if result.recommendation == AgentRecommendation.CREATE_NEW:
            # Proceed with new agent creation
        elif result.recommendation == AgentRecommendation.ENHANCE_EXISTING:
            # Enhance the target agent instead
    """

    def __init__(self, manifest_path: Optional[Path] = None):
        """
        Initialize capability checker.

        Args:
            manifest_path: Path to manifest.yaml (optional)
        """
        self.manifest_path = manifest_path or Path(__file__).parent / "manifest.yaml"
        self.agents: Dict[str, AgentManifestEntry] = {}
        self._load_manifest()

    def _load_manifest(self):
        """Load agent manifest from YAML (or use hardcoded data)."""
        # For now, use hardcoded known agents
        # TODO: Load from manifest.yaml when created

        self.agents = {
            "architect": AgentManifestEntry(
                id="architect",
                file="architect.py",
                role="ARCHITECT",
                capabilities=[
                    "structural_analysis",
                    "design_patterns",
                    "coupling_analysis",
                    "architecture_review",
                ],
                status="active",
            ),
            "builder": AgentManifestEntry(
                id="builder",
                file="builder.py",
                role="BUILDER",
                capabilities=[
                    "code_generation",
                    "pattern_learning",  # NEW
                    "self_verification",  # NEW
                    "file_creation",
                ],
                status="active",
            ),
            "engineer": AgentManifestEntry(
                id="engineer",
                file="engineer.py",
                role="ENGINEER",
                capabilities=["gitops_execution", "code_deployment", "file_writing"],
                status="active",
            ),
            "policy": AgentManifestEntry(
                id="policy",
                file="policy.py",
                role="POLICY",
                capabilities=[
                    "policy_compliance",
                    "rule_enforcement",
                    "violation_detection",
                ],
                status="active",
            ),
            "sentinel": AgentManifestEntry(
                id="sentinel",
                file="sentinel_agent.py",
                role="SENTINEL",
                capabilities=[
                    "risk_detection",
                    "drift_monitoring",
                    "real_time_analysis",
                ],
                status="active",
            ),
            "documentation": AgentManifestEntry(
                id="documentation",
                file="documentation_agent.py",
                role="DOCUMENTATION",
                capabilities=[
                    "documentation_generation",
                    "content_analysis",
                    "quality_assessment",
                ],
                status="active",
            ),
            "refactoring": AgentManifestEntry(
                id="refactoring",
                file="refactoring.py",
                role="REFACTORING",
                capabilities=[
                    "code_smell_detection",
                    "pattern_application",
                    "debt_reduction",
                    "structural_optimization",
                ],
                status="active",
            ),
            "testing": AgentManifestEntry(
                id="testing",
                file="testing.py",
                role="TESTING",
                capabilities=[
                    "test_generation",
                    "unit_testing",
                    "coverage_analysis",
                ],
                status="active",
            ),
            "verification": AgentManifestEntry(
                id="verification",
                file="verification.py",
                role="VERIFICATION",
                capabilities=[
                    "deep_verification",
                    "security_audit",
                    "quality_gate",
                ],
                status="active",
            ),
            "mediator": AgentManifestEntry(
                id="mediator",
                file="mediator.py",
                role="MEDIATOR",
                capabilities=[
                    "conflict_resolution",
                    "consensus_building",
                    "active_intervention",
                ],
                status="active",
            ),
            "capability_checker": AgentManifestEntry(
                id="capability_checker",
                file="capability_checker.py",
                role="CAPABILITY_CHECKER",
                capabilities=[
                    "gap_analysis",
                    "redundancy_prevention",
                    "ecosystem_governance",
                ],
                status="active",
            ),
        }

    def check_capability_exists(self, capability: str) -> CapabilityCheckResult:
        """
        Check if capability already exists in any agent.

        Args:
            capability: Capability to check (e.g., "test_generation")

        Returns:
            CapabilityCheckResult with recommendation
        """
        agents_with_capability = []

        # Normalize capability for comparison
        cap_normalized = capability.lower().replace(" ", "_")

        for agent_id, agent in self.agents.items():
            for agent_cap in agent.capabilities:
                if cap_normalized in agent_cap.lower() or agent_cap.lower() in cap_normalized:
                    agents_with_capability.append(agent_id)
                    break

        if not agents_with_capability:
            return CapabilityCheckResult(
                exists=False,
                agents_with_capability=[],
                recommendation=AgentRecommendation.CREATE_NEW,
                rationale=f"No existing agent has '{capability}' capability. Safe to create new agent.",
            )

        if len(agents_with_capability) == 1:
            agent_id = agents_with_capability[0]
            return CapabilityCheckResult(
                exists=True,
                agents_with_capability=agents_with_capability,
                recommendation=AgentRecommendation.ENHANCE_EXISTING,
                rationale=f"Agent '{agent_id}' already has related capability. Consider enhancing it instead of creating new agent.",
                target_agent=agent_id,
            )

        # Multiple agents
        return CapabilityCheckResult(
            exists=True,
            agents_with_capability=agents_with_capability,
            recommendation=AgentRecommendation.USE_EXISTING,
            rationale=f"Multiple agents ({', '.join(agents_with_capability)}) have related capabilities. Review before creating new agent.",
            target_agent=agents_with_capability[0],
        )

    def suggest_agent_creation(self, proposed_name: str, proposed_capabilities: List[str]) -> CapabilityCheckResult:
        """
        Analyze if new agent is needed or existing one can be enhanced.

        Args:
            proposed_name: Name of proposed agent
            proposed_capabilities: List of capabilities for new agent

        Returns:
            CapabilityCheckResult with detailed recommendation
        """
        overlaps = []

        for capability in proposed_capabilities:
            result = self.check_capability_exists(capability)
            if result.exists:
                overlaps.extend(result.agents_with_capability)

        if not overlaps:
            return CapabilityCheckResult(
                exists=False,
                agents_with_capability=[],
                recommendation=AgentRecommendation.CREATE_NEW,
                rationale=f"Agent '{proposed_name}' with capabilities {proposed_capabilities} has no overlap. Safe to create.",
            )

        # Count overlap frequency
        overlap_counts: Dict[str, int] = {}
        for agent_id in overlaps:
            overlap_counts[agent_id] = overlap_counts.get(agent_id, 0) + 1

        # Find agent with most overlap
        most_overlap_agent = max(overlap_counts.items(), key=lambda x: x[1])
        agent_id, overlap_count = most_overlap_agent

        if overlap_count >= len(proposed_capabilities) * 0.5:
            # > 50% overlap - suggest enhancement
            return CapabilityCheckResult(
                exists=True,
                agents_with_capability=list(set(overlaps)),
                recommendation=AgentRecommendation.ENHANCE_EXISTING,
                rationale=f"Agent '{agent_id}' already covers {overlap_count}/{len(proposed_capabilities)} proposed capabilities. Consider enhancing '{agent_id}' instead of creating '{proposed_name}'.",
                target_agent=agent_id,
            )
        else:
            # < 50% overlap - new agent acceptable
            return CapabilityCheckResult(
                exists=True,
                agents_with_capability=list(set(overlaps)),
                recommendation=AgentRecommendation.CREATE_NEW,
                rationale=f"Partial overlap with {list(set(overlaps))}, but {proposed_name} has unique capabilities. Creating new agent is justified.",
            )

    def list_gaps(self) -> Dict[str, str]:
        """
        List known capability gaps from AGENTS.md.

        Returns:
            Dict of gap_name -> priority
        """
        return {
            "test_generation": "ACTIVE",
            "deep_verification": "ACTIVE",
            "code_refactoring": "ACTIVE",
            "performance_analysis": "MEDIUM",
            "advanced_learning": "ENHANCEMENT",  # Enhance Base.Agent
        }

    def get_agent_by_capability(self, capability: str) -> Optional[AgentManifestEntry]:
        """Get first agent that has given capability."""
        result = self.check_capability_exists(capability)
        if result.exists and result.agents_with_capability:
            agent_id = result.agents_with_capability[0]
            return self.agents.get(agent_id)
        return None


# Convenience function for quick checks
def check_before_creating_agent(
    proposed_capabilities: List[str],
) -> CapabilityCheckResult:
    """
    Quick check before creating new agent.

    Usage:
        result = check_before_creating_agent(["test_generation", "coverage_analysis"])
        if result.recommendation == AgentRecommendation.CREATE_NEW:
            print("✅ Safe to create TestingAgent")
        else:
            print(f"⚠️ {result.rationale}")
    """
    checker = CapabilityChecker()
    return checker.suggest_agent_creation(proposed_name="NewAgent", proposed_capabilities=proposed_capabilities)
