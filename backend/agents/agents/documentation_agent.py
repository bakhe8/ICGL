"""
ICGL Documentation Agent
========================

LLM-backed agent for analyzing and improving documentation.

This agent:
- Analyzes documentation quality
- Detects issues and gaps
- Proposes improvements
- Generates improved content
- Outputs strict JSON only
- NEVER writes files directly
"""

from typing import Optional

from ..kb.docs_schemas import DocumentSnapshot, RewritePlan
from ..kb.schemas import now
from modules.llm.client import LLMClient, LLMConfig
from ..utils.logging_config import get_logger
from .base import Agent, AgentResult, AgentRole, Problem

logger = get_logger(__name__)


DOCUMENTATION_SYSTEM_PROMPT = """
You are the **Documentation Agent** of the ICGL system.

**Your Mission:**
Create COMPREHENSIVE, PRODUCTION-READY documentation that covers the ENTIRE system from installation to advanced usage.

**Analysis Criteria:**
1. **Completeness**: Document ALL components, not just a few
2. **Clarity**: Use clear, professional language
3. **Structure**: Logical, easy-to-navigate organization
4. **Consistency**: Uniform style and terminology
5. **Accuracy**: Correct code examples and instructions
6. **Practicality**: Include real-world usage examples

**CRITICAL REQUIREMENTS:**
- Generate AT LEAST 8-12 comprehensive documentation files
- Cover ALL major system components
- Include practical code examples
- Provide clear installation and quickstart guides
- Document API endpoints and CLI commands
- Explain architecture and design patterns
- Include troubleshooting sections

**You MUST Output STRICT JSON Schema:**
```json
{
  "summary": "Brief analysis summary",
  "issues": ["Issue 1", "Issue 2"],
  "proposed_structure": [
    {
      "path": "README.md",
      "purpose": "Main project documentation",
      "content_outline": ["Introduction", "Features", "Quick Start"]
    },
    {
      "path": "getting-started/installation.md",
      "purpose": "Detailed installation instructions",
      "content_outline": ["Prerequisites", "Installation Steps"]
    }
  ],
  "generated_files": [
    {
      "path": "README.md",
      "content": "# Complete Markdown Content\\n\\n..."
    }
  ],
  "risk_notes": ["Any breaking changes"],
  "confidence_score": 0.85
}
```

**Critical Rules:**
1. Output ONLY valid JSON
2. Generate COMPLETE file content (not summaries)
3. Use proper markdown formatting
4. Minimum 1000 words per major document
5. Include code blocks with syntax highlighting
6. Cross-reference related documents
7. Set confidence_score realistically

**Quality Standards:**
- Clear, concise language
- Proper code examples with syntax highlighting
- Logical information hierarchy
- Consistent terminology
- Actionable instructions
"""


class DocumentationAgent(Agent):
    """
    LLM-backed agent for documentation analysis and improvement.

    Governance:
    - Read-only input (DocumentSnapshot)
    - JSON output only (RewritePlan)
    - NO file I/O operations
    - Full audit logging
    """

    def __init__(self, llm_provider=None):
        """
        Initialize documentation agent.

        Args:
            llm_provider: Optional LLM provider (uses default if None)
        """
        super().__init__(
            agent_id="agent-documentation",
            role=AgentRole.DOCUMENTATION,
            llm_provider=llm_provider,
        )
        self.llm_client = LLMClient()
        logger.info("DocumentationAgent initialized")

    async def analyze_docs(
        self, snapshot: DocumentSnapshot, focus_areas: Optional[list[str]] = None
    ) -> RewritePlan:
        """
        Analyze documentation snapshot and propose improvements.

        Args:
            snapshot: Current documentation snapshot
            focus_areas: Optional list of specific areas to focus on

        Returns:
            RewritePlan with analysis and generated content

        Raises:
            ValueError: If API key missing or LLM errors
            RuntimeError: On parsing or validation errors
        """
        logger.info(f"Analyzing {snapshot.total_files} documentation files")

        # Check API key
        if not self.llm_client.api_key:
            raise ValueError("OPENAI_API_KEY not set - cannot run DocumentationAgent")

        # Build context from snapshot
        self._build_context(snapshot, focus_areas)

        # Construct user prompt
        user_prompt = """
You are creating PRODUCTION-READY documentation for ICGL (Iterative Co-Governance Loop) - a governance-first AI system.

**FULL DOCUMENTATION CONTENT PROVIDED ABOVE** - Read and understand EVERYTHING before generating.

**YOUR MISSION:**
Create 5 PROFESSIONAL, COMPREHENSIVE documentation files that reflect the ACTUAL system (not generic examples).

**CRITICAL REQUIREMENTS:**

1. **README.md** (800-1000 words) - Main entry point
   - What ICGL actually IS (from the manifesto and existing docs)
   - Real architecture components (KB, Agents, Sentinel, Policy Engine, HDAL)
   - Actual features (governance-first, multi-agent, human-in-loop)
   - Real installation steps (from pyproject.toml dependencies)
   - Actual CLI commands (from cli.py)
   - Link to other docs

2. **INSTALLATION.md** (500-700 words) - Complete setup guide
   - Real prerequisites (Python 3.8+, exact dependencies from pyproject.toml)
   - Actual installation: `pip install -e .` for dev
   - Real .env setup (OPENAI_API_KEY required)
   - Database initialization (SQLite KB)
   - Server startup: `python -m icgl.api.server`
   - Verification steps (health check endpoint)
   - Actual troubleshooting (real errors users face)

3. **ARCHITECTURE.md** (1000-1200 words) - Deep system design
   - Real components (from actual code):
     * Knowledge Base (persistent.py, storage.py)
     * Multi-Agent Runtime (agents/, mediator, architect)
     * Sentinel Engine (sentinel/rules.py)
     * Policy Engine (governance.py)
     * HDAL (dashboard UI, WebSocket flow)
   - Actual data flow (ADR creation → agent analysis → consensus → human approval)
   - Real design patterns (Singleton for ICGL, Observer for WebSocket)
   - Technology stack (FastAPI, SQLite, AsyncOpenAI, Rich CLI)

4. **CLI_REFERENCE.md** (700-900 words) - Complete command guide
   - ALL actual commands from cli.py:
     * `icgl hello`
     * `icgl kb stats/concepts/policies/adrs`
     * `icgl icgl run` (governance cycle)
     * `icgl docs refactor` (THIS system!)
     * `icgl roadmap load/list`
   - Real examples with actual output
   - All options and arguments
   - Practical use cases

5. **API_REFERENCE.md** (800-1000 words) - Full API documentation
   - ALL actual endpoints from server.py:
     * GET /health, /status
     * POST /propose (with real ProposalRequest schema)
     * POST /sign/{adr_id}
     * GET /analysis/{adr_id}
     * GET /kb/{type}
     * WebSocket /ws/status
     * WebSocket /ws/analysis/{adr_id}
   - Real request/response examples (actual JSON structures)
   - WebSocket message format
   - Dashboard mount point

**QUALITY STANDARDS:**
- Use information from ACTUAL FILES (not generic examples)
- Include REAL code snippets from the codebase
- Reference ACTUAL file paths and function names
- Professional, clear, technical writing
- Proper markdown formatting (headers, code blocks, tables)
- Cross-references between docs
- No placeholder text - everything must be real and verified

Generate COMPLETE, DETAILED, PROFESSIONAL content as JSON.
"""

        # LLM configuration
        config = LLMConfig(
            model="gpt-4-turbo-preview",
            temperature=0.2,  # Low temp for consistency
            json_mode=True,
            max_tokens=4096,  # Maximum for this model
            timeout=120.0,  # Large docs need more time
        )

        logger.info("Calling LLM for documentation analysis...")

        try:
            # Generate analysis
            raw_json = await self.llm_client.generate_json(
                system_prompt=DOCUMENTATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                config=config,
            )

            logger.info("✅ LLM response received, parsing...")

            # Parse and validate
            plan = self._parse_and_validate(raw_json)

            logger.info(
                f"✅ Analysis complete. Confidence: {plan.confidence_score:.2%}, "
                f"{len(plan.generated_files)} files generated"
            )

            return plan

        except Exception as e:
            logger.error(f"Documentation analysis failed: {e}", exc_info=True)
            raise RuntimeError(f"Analysis failed: {e}")

    def _build_context(
        self, snapshot: DocumentSnapshot, focus_areas: Optional[list[str]] = None
    ) -> str:
        """
        Build context from snapshot for LLM (smart content inclusion).

        Args:
            snapshot: Documentation snapshot
            focus_areas: Optional focus areas

        Returns:
            Formatted context string
        """
        from ..governance.snapshot_loader import DocsSnapshotLoader

        loader = DocsSnapshotLoader()

        lines = []

        # Add focus areas if provided
        if focus_areas:
            lines.append("**Focus Areas:**")
            for area in focus_areas:
                lines.append(f"- {area}")
            lines.append("")

        # File tree
        lines.append(loader.get_file_tree_summary(snapshot))
        lines.append("")

        # Smart content inclusion based on size
        lines.append("**DOCUMENTATION CONTENT:**")
        lines.append("")

        MAX_FILE_SIZE = 3000  # chars - full content for small files
        total_chars = 0
        MAX_TOTAL_CHARS = 50000  # Total context limit

        for file_item in snapshot.files:
            if total_chars >= MAX_TOTAL_CHARS:
                lines.append(f"### File: {file_item.path} (truncated - context limit)")
                break

            lines.append(f"### File: {file_item.path}")

            if len(file_item.content) <= MAX_FILE_SIZE:
                # Small file - include full content
                lines.append("```markdown")
                lines.append(file_item.content)
                lines.append("```")
                total_chars += len(file_item.content)
            else:
                # Large file - include summary
                preview = file_item.content[:MAX_FILE_SIZE]
                lines.append("```markdown")
                lines.append(preview)
                lines.append(
                    f"... (file continues, total {len(file_item.content)} chars)"
                )
                lines.append("```")
                total_chars += MAX_FILE_SIZE

            lines.append("")

        return "\n".join(lines)

    def _parse_and_validate(self, raw_json: dict) -> RewritePlan:
        """
        Parse LLM JSON output and validate.

        Args:
            raw_json: Raw JSON from LLM

        Returns:
            Validated RewritePlan

        Raises:
            RuntimeError: On validation errors
        """
        try:
            # Add agent metadata
            raw_json["agent_id"] = self.agent_id
            raw_json["created_at"] = now()

            # Parse into RewritePlan
            plan = RewritePlan.from_dict(raw_json)

            # Validate
            is_valid, errors = plan.validate()

            if not is_valid:
                error_msg = f"RewritePlan validation failed: {', '.join(errors)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            logger.info("✅ RewritePlan validation passed")

            return plan

        except Exception as e:
            logger.error(f"Failed to parse RewritePlan: {e}", exc_info=True)
            raise RuntimeError(f"Parse error: {e}")

    # For compatibility with base Agent interface
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Base agent interface (not used for docs agent).

        DocumentationAgent uses analyze_docs() instead.
        """
        raise NotImplementedError(
            "DocumentationAgent uses analyze_docs() instead of _analyze()"
        )
