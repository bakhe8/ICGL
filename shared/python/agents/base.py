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
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from enum import Enum

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
    """
    agent_id: str
    role: AgentRole
    analysis: str
    recommendations: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    confidence: float = 0.8
    references: List[str] = field(default_factory=list)
    file_changes: List["FileChange"] = field(default_factory=list)
    file_changes: List["FileChange"] = field(default_factory=list)
    
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
    
    def __init__(self, agent_id: str, role: AgentRole, llm_provider: Optional["LLMProvider"] = None):
        self.agent_id = agent_id
        self.role = role
        self.llm = llm_provider
        self.memory: Optional["VectorStore"] = None
        self.observer: Optional[Any] = None # Injected typed SystemObserver
    
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
                error_code=error_msg
            )
            
        return result

    def _fallback_result(self, reason: str) -> AgentResult:
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=f"⚠️ Analysis Failed: {reason}",
            recommendations=["Check Logs"],
            concerns=["Execution Error"],
            confidence=0.0
        )
        

    
    async def _ask_llm(self, prompt: str, system_prompt: str = None) -> str:
        """
        Helper to query the assigned LLM provider.
        Now includes Active Learning: auto-recalls relevant lessons.
        """
        if not self.llm:
            return f"[No LLM Configured] Mock analysis for prompt: {prompt[:50]}..."
            
        # 1. Active Learning Retrieval
        # We search primarily using the prompt context
        lessons = await self.recall_lessons(prompt)
        
        final_system_prompt = system_prompt or self.get_system_prompt()
        
        if lessons:
             warning = "\n\n⚠️ CRITICAL MEMORY (PAST MISTAKES):\nThe following past proposals were REJECTED by the human. DO NOT REPEAT THEM:\n"
             for l in lessons:
                 warning += f"- {l}\n"
             final_system_prompt += warning
             print(f"   🎓 [{self.agent_id}] Recalled {len(lessons)} pertinent lessons.")

        from ..core.llm import LLMRequest
        
        req = LLMRequest(
            prompt=prompt,
            system_prompt=final_system_prompt,
            temperature=0.3 
        )
        
        response = await self.llm.generate(req)
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
        return [res.document.content for res in results if res.document.metadata.get("type") in ["adr", "concept", "policy", "manual"]]

    async def recall_lessons(self, query: str, limit: int = 3) -> List[str]:
        """
        Specific recall for 'lesson' type documents (Interventions).
        """
        if not hasattr(self, "memory") or not self.memory:
            return []
            
        # Search all
        results = await self.memory.search(query, limit=limit * 2) # Fetch more to filter
        
        lessons = []
        for res in results:
            if res.document.metadata.get("type") == "lesson":
                lessons.append(res.document.content)
                
        return lessons[:limit]
    
    def get_system_prompt(self) -> str:
        """
        Returns the system prompt for this agent.
        Override to customize agent behavior.
        """
        return f"You are a {self.role.value} analysis agent for Consensus AI."


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
            confidence=0.7
        )
