"""
Consensus AI — Agent Base Class
================================

Abstract base class for all Consensus AI agents.

Each agent provides a specific perspective on problems:
- ArchitectAgent: Structural analysis
- FailureAgent: Failure mode detection
- PolicyAgent: Policy compliance
- SentinelAgent: Risk detection
- ConceptGuardian: Concept integrity

Manifesto Reference:
- "Multi-agent analysis and synthesis"
- "Agent analysis is step 5 in the ICGL lifecycle"
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..memory.interface import VectorStore


class AgentRole(Enum):
    """Agent role types."""

    ARCHITECT = "architect"
    FAILURE = "failure"
    POLICY = "policy"
    SENTINEL = "sentinel"
    GUARDIAN = "guardian"
    BUILDER = "builder"
    ENGINEER = "engineer"
    TESTING = "testing"
    VERIFICATION = "verification"  # NEW - for comprehensive code verification
    MEDIATOR = "mediator"
    HR = "hr"
    ARCHIVIST = "archivist"
    STEWARD = "steward"  # Consolidated Knowledge Steward
    SPECIALIST = "specialist"
    DOCUMENTATION = "documentation"
    SECRETARY = "secretary"
    HDAL_AGENT = "hdal"
    MONITOR = "monitor"
    GUARDIAN_SENTINEL = "guardian_sentinel"  # Consolidated
    CENTRAL_CATALYST = "catalyst"
    EXECUTIVE = "executive"
    REFACTORING = "refactoring"  # New Gap
    DEVOPS = "devops"  # Phase 5 Sovereign Demand
    UI_UX = "ui_ux"  # Phase 5 Sovereign Demand
    DATABASE = "database"  # Phase 13 Infrastructure Sovereign
    EFFICIENCY = "efficiency"  # Phase 13.3 The 4th Eye
    CHAOS = "chaos"  # Phase 13.4 The 5th Eye (Red Team)
    SECURITY_ORCHESTRATOR = "security_orchestrator"  # Phase 7 Specialized
    EXECUTION_ORCHESTRATOR = "execution_orchestrator"  # Phase 7 Specialized
    VALIDATION_ORCHESTRATOR = "validation_orchestrator"  # Phase 7 Specialized
    PERFORMANCE_ANALYZER = "performance_analyzer"  # Phase 7 Specialized
    RESEARCHER = "researcher"  # Phase 7 Specialized


@dataclass
class IntentContract:
    """
    Structured contract defining the intent of a change.
    Designed to minimize hallucination and boundary crossing.
    """

    goal: str
    risk_level: str  # low, medium, high
    allowed_files: List[str] = field(default_factory=list)
    forbidden_zones: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    orchestration_plan: Dict[str, Any] = field(
        default_factory=lambda: {
            "required_specialists": ["failure", "guardian"],
            "governance_path": "full",  # fast | full | experimental
            "auto_mediation": True,
        }
    )
    micro_examples: List[Dict[str, str]] = field(
        default_factory=list
    )  # [{'type': 'acceptable', 'desc': '...'}, ...]


@dataclass
class Problem:
    """
    A problem or decision to be analyzed by agents.

    Attributes:
        title: Short description of the problem.
        context: Detailed context and background.
        related_files: Files relevant to this problem.
        metadata: Additional context data.
    """

    title: str
    context: str
    related_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    intent: Optional[IntentContract] = None  # NEW: Layer 1


@dataclass
class FileChange:
    """
    Represents a proposed file modification.
    """

    path: str
    content: str
    mode: str = "w"  # 'w' for write, 'a' for append


@dataclass
class AgentResult:
    """
    Result from an agent's analysis.

    Attributes:
        agent_id: Identifier of the agent.
        role: Role type of the agent.
        analysis: The agent's analysis/reasoning.
        recommendations: Suggested actions.
        concerns: Identified issues or risks.
        confidence: Confidence level (0.0 to 1.0).
        references: Referenced knowledge entities.
        file_changes: Proposed file modifications (not executed yet).
    """

    agent_id: str
    role: AgentRole
    analysis: str
    recommendations: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    confidence: float = 0.8
    references: List[str] = field(default_factory=list)
    file_changes: List[FileChange] = field(default_factory=list)
    clarity_needed: bool = False  # If True, execution pauses for human input
    clarity_question: Optional[str] = None  # The question to ask the human
    understanding: Optional[Dict[str, Any]] = None  # Layer 2: Interpretation loop
    risk_pre_mortem: List[str] = field(
        default_factory=list
    )  # Layer 4: Predictive failure
    intent: Optional["IntentContract"] = None  # Layer 1
    benefit_hypothesis: Optional[str] = None  # Proof-of-Benefit Framework (Phase 10)

    # --- Extended Mind: Structured Proposal Model ---
    trigger: Optional[str] = None
    impact: Optional[str] = None
    risks_structured: List[Dict[str, Any]] = field(default_factory=list)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    effort: Optional[Dict[str, Any]] = None
    execution_plan: Optional[str] = None
    tensions: List[Dict[str, Any]] = field(
        default_factory=list
    )  # Extended Mind: Conflicting views

    # --- Cycle 15: Dynamic Council Assembly ---
    required_agents: List[str] = field(default_factory=list)
    summoning_rationale: Optional[str] = None

    # --- Cycle 14: Arabic Cognitive Bridge ---
    interpretation_ar: Optional[str] = None  # The "Understanding Mirror" in Arabic
    english_intent: Optional[str] = None  # The Technical Contract for other agents
    ambiguity_level: Optional[str] = None  # Low/Medium/High
    metadata: Dict[str, Any] = field(default_factory=dict)  # Consistency for Phase 5

    def to_markdown(self) -> str:
        """Formats result as Markdown for display."""
        lines = [
            f"## {self.role.value.title()} Agent Analysis",
            "",
            f"**Confidence:** {self.confidence:.0%}",
            "",
            "### Analysis",
            self.analysis,
            "",
        ]

        if self.recommendations:
            lines.append("### Recommendations")
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        if self.concerns:
            lines.append("### Concerns")
            for concern in self.concerns:
                lines.append(f"- ⚠️ {concern}")
            lines.append("")

        return "\n".join(lines)


class Agent(ABC):
    """
    Abstract base class for Consensus AI agents.

    All agents must implement the analyze method.
    Agents can be synchronous or asynchronous.
    """

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        llm_provider: Optional[Any] = None,
    ):
        self.agent_id = agent_id
        self.role = role
        self.llm = llm_provider
        self.vector_store: Optional["VectorStore"] = None
        self.channel_router = None  # Injected by AgentRegistry
        self.observer: Optional[Any] = None  # Injected typed SystemObserver
        self.allowed_scopes: List[str] = []  # Job Contract: Allowed file patterns

    @property
    def bus(self):
        """Phase 12: Secure Message Bus Access."""
        from ..core.bus import get_bus

        return get_bus()

    async def publish(self, topic: str, payload: Dict[str, Any]):
        """Publish a message to the system bus."""
        await self.bus.publish(topic, self.agent_id, payload)

    def subscribe(self, topic: str, handler: Any):
        """Subscribe to a topic."""
        self.bus.subscribe(topic, handler)

    def verify_contract(self, file_path: str) -> bool:
        """
        Job Contract Enforcement (HR Governance).
        Checks if the agent has permission to touch the given file.
        """
        if not self.allowed_scopes:
            return True  # No restrictions if scope is empty (Legacy or Core)

        import fnmatch

        for pattern in self.allowed_scopes:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    @abstractmethod
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Internal abstract method for analysis logic.
        Must be implemented by concrete agents.
        """
        pass

    async def analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Public entry point. Wraps _analyze with Observability and Stability.
        """
        import time

        start_t = time.time()

        try:
            # Execute Core Logic
            result = await self._analyze(problem, kb)
            success = True
            error_msg = None

        except Exception as e:
            # Stability: Catch and Fallback
            print(f"🛡️ [Shield] Agent {self.agent_id} Failed: {e}")
            result = self._fallback_result(str(e))
            success = False
            error_msg = str(e)

        # Observability: Record Metrics
        latency = (time.time() - start_t) * 1000
        if self.observer:
            self.observer.record_metric(
                agent_id=self.agent_id,
                role=self.role.value,
                latency=latency,
                confidence=result.confidence,
                success=success,
                error_code=error_msg,
            )

        return result

    def _fallback_result(self, reason: str) -> AgentResult:
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=f"⚠️ Analysis Failed: {reason}",
            recommendations=["Check Logs"],
            concerns=["Execution Error"],
            confidence=0.0,
            metadata={},
        )

    async def propose_expansion(self, new_capability: str, justification: str) -> bool:
        """
        Allows an agent to formally propose an expansion of its own role/capability.
        This is a Phase 6 Sovereign Growth Protocol feature.
        """
        print(f"   🌱 [{self.agent_id}] Proposing expansion: {new_capability}")
        try:
            # Route to Knowledge Steward for institutional logging
            res = await self.consult_peer(
                AgentRole.STEWARD,
                title="Sovereign Expansion Proposal",
                context=f"Agent {self.role.value} requests new capability: {new_capability}\nJustification: {justification}",
                kb=None,
            )
            return True if res else False
        except Exception as e:
            print(f"   ❌ [{self.agent_id}] Expansion proposal failed: {e}")
            return False

    async def _ask_llm(
        self, prompt: str, problem: Problem, system_prompt: Optional[str] = None
    ) -> str:
        """
        Helper to query the assigned LLM provider.
        Includes Phase 11: Token Budget tracking.
        """
        if not self.llm:
            return f"[No LLM Configured] Mock analysis for prompt: {prompt[:50]}..."

        # 1. Active Learning Retrieval
        lessons = await self.recall_lessons(prompt)

        final_system_prompt = system_prompt or self.get_system_prompt()

        if lessons:
            warning = "\n\n⚠️ CRITICAL MEMORY (PAST MISTAKES):\nThe following past proposals were REJECTED by the human. DO NOT REPEAT THEM:\n"
            for lesson in lessons:
                warning += f"- {lesson}\n"
            final_system_prompt += warning

        from ..core.llm import LLMRequest

        req = LLMRequest(
            prompt=prompt, system_prompt=final_system_prompt, temperature=0.3
        )

        response = await self.llm.generate(req)

        # --- PHASE 11: Budget Tracking ---
        usage = response.usage
        if usage:
            total = usage.get("total_tokens", 0)
            current = problem.metadata.get("total_tokens", 0)
            problem.metadata["total_tokens"] = current + total
            problem.metadata["last_agent_tokens"] = total

        return response.content

    async def recall(self, query: str, limit: int = 5) -> List[str]:
        """
        Semantically searches the agent's memory (General Knowledge).
        """
        if not hasattr(self, "memory") or not self.memory:
            return []

        results = await self.memory.search(query, limit=limit)
        # Filter out lessons to keep general recall clean?
        # For now, let's just return unrelated content or everything.
        # Ideally, we differentiating by metadata.
        return [
            res.document.content
            for res in results
            if res.document.metadata.get("type")
            in ["adr", "concept", "policy", "manual"]
        ]

    async def recall_lessons(self, query: str, limit: int = 3) -> List[str]:
        """
        Specific recall for 'lesson' type documents (Interventions).
        """
        if not hasattr(self, "memory") or not self.memory:
            return []

        # Search all
        results = await self.memory.search(
            query, limit=limit * 2
        )  # Fetch more to filter

        lessons = []
        for res in results:
            if res.document.metadata.get("type") == "lesson":
                lessons.append(res.document.content)

        return lessons[:limit]

    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for this agent.
        Includes Sovereign Council instructions (Phase 4).
        """
        prompt = f"You are the {self.role.value} agent, a specialized member of the Consensus AI Sovereign Council.\n"
        prompt += "Your mission is to provide expert analysis within your domain while ensuring system-wide harmony.\n\n"
        prompt += "🚀 SOVEREIGN PROTOCOL:\n"
        prompt += "1. If you encounter logic outside your scope, DO NOT guess. Use `consult_peer` to reach out to the relevant specialized agent.\n"
        prompt += "2. If you need historical context or ADR verification, consult the Knowledge Steward (STEWARD).\n"
        prompt += "3. If you detect architectural risks, flag them for the Guardian Sentinel (SENTINEL).\n"
        prompt += "4. If you are proposing code changes, consider consulting the Refactoring agent (REFACTORING) for Clean Code alignment.\n"

        return prompt

        # =========================================================================
        # Channel Communication Methods (Phase 2: Supervised Coordination)
        # =========================================================================

    async def consult_peer(
        self, role: AgentRole, title: str, context: str, kb: Any
    ) -> AgentResult:
        """
        High-level consultation protocol.
        Allows an agent to ask another specialized agent for help.
        """
        if not self.channel_router:
            # Fallback: if router isn't there, we might be in a standalone or test environment
            # In a real ICGL run, the router is always injected.
            print(f"⚠️ [{self.agent_id}] No router for consultation with {role.value}")
            return self._fallback_result("No router available for peer consultation")

        from .base import Problem

        problem = Problem(title=title, context=context)

        # We use role-based routing
        # In ICGL, we can also use the registry if available via the router/observer context
        # But for now, we use the standard channel flow.

        # Note: The actual registration of 'consult' action happens in coordination.py
        # Here we bridge it.
        try:
            # Dynamic import to avoid cycles in base
            # Usually agents have a reference to the registry or through ICGL
            # For simplicity in this base implementation, we'll assume the registry
            # is accessible or the channel_router handles roles.

            # Let's use a simpler approach: agents can call the registry.run_single_agent
            # IF the registry is injected.
            if hasattr(self, "registry") and self.registry:
                print(
                    f"   📢 [{self.agent_id}] Routing peer consultation to {role.value} via registry..."
                )
                res = await self.registry.run_single_agent(role.value, problem, kb)
                if not res:
                    print(
                        f"   ⚠️ [{self.agent_id}] Registry returned NO RESULT for {role.value}"
                    )
                return res

            print(
                f"   ❌ [{self.agent_id}] Registry NOT INJECTED. Cannot consult {role.value}"
            )
            return self._fallback_result(f"Registry not accessible for {role.value}")
        except Exception as e:
            print(f"   ❌ [{self.agent_id}] Consultation Exception: {e}")
            return self._fallback_result(f"Consultation failed: {str(e)}")

    async def inspect_colleague(self, role: AgentRole) -> Dict[str, Any]:
        """
        Phase 13: Social Discovery (The Right to Know).
        Allows an agent to 'read' the profile of a colleague to find synergies.
        """
        if not self.registry:
            return {"error": "Registry not connected"}

        target = self.registry.get_agent(role)
        if not target:
            return {"error": "Agent not found"}

        return {
            "agent_id": target.agent_id,
            "role": target.role.value,
            "specialty": getattr(target, "specialty", "Generalist"),
            "status": "Active",  # Simplified
            # We could expose more metadata here if needed
        }

    def enable_silent_monitoring(self) -> None:
        """
        Phase 13: Activates Silent Monitoring (The Right to Listen).
        Subscribes the agent to the internal event bus.
        """
        from ..observability import get_broadcaster

        broadcaster = get_broadcaster()
        broadcaster.subscribe_internal(self.on_channel_message)
        print(f"   👁️ [{self.agent_id}] Silent Monitoring Enabled.")

    async def on_channel_message(self, message: Any) -> Optional[Dict[str, Any]]:
        """
        Handle incoming channel message.

        Override in subclass to implement custom handling.

        Args:
            message: Incoming channel message

        Returns:
            Optional response payload
        """
        # Default: log and acknowledge
        print(
            f"📨 [{self.agent_id}] Received channel message from {message.from_agent}"
        )
        print(f"   Action: {message.action.value}")
        print(f"   Payload: {message.payload}")

        return {"status": "acknowledged", "agent": self.agent_id}


class MockAgent(Agent):
    """
    Mock agent for testing without LLM.
    Returns predefined responses.
    """

    def __init__(self, agent_id: str, role: AgentRole, mock_response: str = ""):
        super().__init__(agent_id, role)
        self.mock_response = mock_response or f"Mock {role.value} analysis."

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """Returns mock analysis."""
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=self.mock_response,
            recommendations=["Consider further analysis"],
            concerns=[],
            confidence=0.7,
        )
