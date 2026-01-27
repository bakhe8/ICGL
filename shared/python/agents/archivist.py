"""
Archivist Agent - Documentation and ADR Lifecycle Steward
=========================================================

The Archivist Agent manages architectural decision records, documentation
lifecycle, and knowledge base maintenance for the system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem
from shared.python.kb.schemas import now


class DocumentationType(Enum):
    """Types of documentation managed by Archivist."""

    ADR = "adr"  # Architectural Decision Record
    DESIGN_DOC = "design"
    API_DOC = "api"
    RUNBOOK = "runbook"
    POLICY = "policy"


class DocumentStatus(Enum):
    """Lifecycle status of documents."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class DocumentRecord:
    """Represents a managed document."""

    def __init__(
        self,
        doc_id: str,
        title: str,
        doc_type: DocumentationType,
        content: str,
        author: str,
    ):
        self.doc_id = doc_id
        self.title = title
        self.doc_type = doc_type
        self.content = content
        self.author = author
        self.created_at = now()
        self.updated_at = now()
        self.status = DocumentStatus.DRAFT
        self.version = 1
        self.tags: List[str] = []


class ArchivistAgent(Agent):
    """
    Archivist Agent: Documentation workspace and ADR lifecycle steward.

    Responsibilities:
    - Manage ADR (Architectural Decision Record) lifecycle
    - Detect documentation gaps and inconsistencies
    - Track document versions and history
    - Ensure knowledge base completeness
    - Facilitate documentation review workflows
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="archivist",
            role=AgentRole.ARCHIVIST,
            llm_provider=llm_provider,
        )
        self.documents: Dict[str, DocumentRecord] = {}
        self.documentation_gaps: List[Dict[str, str]] = []

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Analyzes problems from documentation and knowledge perspective.

        Focus areas:
        - Documentation gaps and requirements
        - ADR needs for architectural decisions
        - Knowledge base updates required
        - Historical context and precedent
        """

        # Detect if this requires an ADR
        needs_adr = self._detect_adr_needed(problem)

        # Identify documentation gaps
        gaps = await self._identify_documentation_gaps(problem)

        # Check for existing precedent
        precedent = self._check_precedent(problem)

        # Generate documentation recommendation
        doc_recommendation = await self._generate_doc_recommendation(problem, needs_adr)

        # Build comprehensive analysis
        analysis = f"""
=== DOCUMENTATION ASSESSMENT ===
ADR Required: {"Yes - Architectural decision detected" if needs_adr else "No"}
Documentation Gaps Identified: {len(gaps)}
Historical Precedent: {precedent}

=== DOCUMENTATION RECOMMENDATION ===
{doc_recommendation}

=== IDENTIFIED GAPS ===
{self._format_gaps(gaps)}

=== ARCHIVAL STRATEGY ===
{self._get_archival_strategy(needs_adr)}
"""

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "Create ADR for this decision" if needs_adr else "Document decision rationale",
                "Update relevant design documentation",
                "Archive decision in knowledge base",
                f"Tag with: {', '.join(self._generate_tags(problem))}",
            ],
            concerns=[
                "Lacks proper documentation trail" if not precedent else "Should reference existing precedent",
                "May create knowledge gap if not documented",
                "Future maintainers need context",
            ],
            confidence=0.85,
        )

    def _detect_adr_needed(self, problem: Problem) -> bool:
        """Detect if an ADR (Architectural Decision Record) is needed."""
        adr_indicators = [
            "architecture",
            "design decision",
            "technology choice",
            "framework",
            "pattern",
            "structure",
            "database",
            "api design",
            "security model",
            "deployment strategy",
        ]

        context_lower = problem.context.lower()
        return any(indicator in context_lower for indicator in adr_indicators)

    async def _identify_documentation_gaps(self, problem: Problem) -> List[Dict[str, str]]:
        """Identify documentation gaps using LLM analysis."""
        prompt = f"""
Analyze this problem and identify what documentation is missing or needs updating.

Problem: {problem.title}
Context: {problem.context}

List 2-3 specific documentation gaps. For each gap, provide:
- Type (e.g., "API Documentation", "Design Doc", "Runbook")
- Description (one sentence)

Format as a concise list.
"""

        try:
            response = await self._ask_llm(prompt)
            # Parse response into structured gaps
            gaps = []
            for line in response.strip().split("\n"):
                if line.strip():
                    gaps.append({"description": line.strip(), "severity": "medium"})
            return gaps[:3]  # Limit to 3
        except Exception:
            # Fallback gaps
            return [
                {
                    "description": "Decision rationale documentation needed",
                    "severity": "medium",
                }
            ]

    def _check_precedent(self, problem: Problem) -> str:
        """Check for existing precedent in documentation."""
        # In real implementation, this would search the KB
        # For now, simple keyword check
        if "similar" in problem.context.lower() or "like" in problem.context.lower():
            return "Related precedent may exist - recommend review"
        return "No clear precedent found - this appears to be a new decision"

    async def _generate_doc_recommendation(self, problem: Problem, needs_adr: bool) -> str:
        """Generate documentation recommendation."""
        if needs_adr:
            return """
Recommend creating a comprehensive ADR with:
1. Context: Why this decision is needed
2. Decision: What was decided
3. Consequences: Implications and trade-offs
4. Alternatives Considered: What options were evaluated
5. References: Related decisions and documentation
"""
        else:
            return """
Recommend documenting this decision with:
1. Brief context and rationale
2. Key outcomes and implications
3. Links to related documentation
4. Tags for future discoverability
"""

    def _format_gaps(self, gaps: List[Dict[str, str]]) -> str:
        """Format documentation gaps for display."""
        if not gaps:
            return "✅ No critical gaps identified"

        formatted = []
        for i, gap in enumerate(gaps, 1):
            severity = gap.get("severity", "medium")
            icon = "🔴" if severity == "high" else "🟡"
            formatted.append(f"{icon} {i}. {gap['description']}")

        return "\n".join(formatted)

    def _get_archival_strategy(self, needs_adr: bool) -> str:
        """Get archival strategy based on decision type."""
        if needs_adr:
            return """
1. Draft ADR using standard template
2. Submit for peer review
3. Update after feedback
4. Archive in ADR repository
5. Link from relevant design docs
6. Add to decision index
"""
        else:
            return """
1. Create decision log entry
2. Update affected documentation
3. Archive in knowledge base
4. Tag appropriately for search
"""

    def _generate_tags(self, problem: Problem) -> List[str]:
        """Generate relevant tags for this documentation."""
        tags = []
        context_lower = problem.context.lower()

        tag_keywords = {
            "security": "security",
            "performance": "performance",
            "architecture": "architecture",
            "infrastructure": "infrastructure",
            "api": "api",
            "database": "database",
            "frontend": "frontend",
            "backend": "backend",
        }

        for keyword, tag in tag_keywords.items():
            if keyword in context_lower:
                tags.append(tag)

        # Always add governance tag
        tags.append("governance")

        return tags[:5]  # Limit to 5 tags

    def create_adr(self, title: str, context: str, decision: str, consequences: str, author: str) -> DocumentRecord:
        """Create a new ADR."""
        doc_id = f"ADR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        content = f"""
# {title}

## Status
Draft

## Context
{context}

## Decision
{decision}

## Consequences
{consequences}

## Date
{now()}
"""

        adr = DocumentRecord(
            doc_id=doc_id,
            title=title,
            doc_type=DocumentationType.ADR,
            content=content,
            author=author,
        )

        self.documents[doc_id] = adr
        return adr

    def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing document."""
        if doc_id not in self.documents:
            return False

        doc = self.documents[doc_id]
        doc.updated_at = now()
        doc.version += 1

        if "content" in updates:
            doc.content = updates["content"]
        if "status" in updates:
            doc.status = updates["status"]
        if "tags" in updates:
            doc.tags = updates["tags"]

        return True

    def get_active_adrs(self) -> List[DocumentRecord]:
        """Get all active (non-deprecated) ADRs."""
        return [
            doc
            for doc in self.documents.values()
            if doc.doc_type == DocumentationType.ADR and doc.status != DocumentStatus.DEPRECATED
        ]

    def search_documentation(self, query: str) -> List[DocumentRecord]:
        """Search documentation by title or content."""
        query_lower = query.lower()
        results = []

        for doc in self.documents.values():
            if query_lower in doc.title.lower() or query_lower in doc.content.lower():
                results.append(doc)

        return results
