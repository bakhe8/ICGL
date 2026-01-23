"""
ICGL Capability Checker API Endpoints
======================================

Provides REST API endpoints for agent capability checking and management.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agents.capability_checker import (
    CapabilityChecker,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])


# --- Request/Response Models ---


class CheckCapabilityRequest(BaseModel):
    """Request to check if capability exists."""

    capability: str


class SuggestAgentRequest(BaseModel):
    """Request to suggest agent creation."""

    agent_name: str
    capabilities: List[str]


class CapabilityCheckResponse(BaseModel):
    """Response from capability check."""

    exists: bool
    agents_with_capability: List[str]
    recommendation: str
    rationale: str
    target_agent: Optional[str] = None


# --- Endpoints ---


@router.get("/list")
async def list_agents() -> Dict[str, Any]:
    """
    List all registered agents with their capabilities.

    Returns:
        Dictionary containing agents list and metadata
    """
    try:
        # Prefer live registry for accuracy (17 agents) with metadata fallback
        from api.server import get_icgl
        from backend.agents.metadata import get_agent_metadata

        icgl = get_icgl()
        registry_agents = icgl.registry.list_agents()
        agents_list = [
            get_agent_metadata(a.value if hasattr(a, "value") else str(a))
            for a in registry_agents
        ]

        agents_md_path = (
            Path(__file__).parent.parent / "backend" / "agents" / "AGENTS.md"
        )

        return {
            "total": len(agents_list),
            "agents": agents_list,
            "registry_path": str(agents_md_path),
            "has_registry": agents_md_path.exists(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/gaps")
async def list_capability_gaps() -> Dict[str, Any]:
    """
    List known capability gaps from the registry.

    Returns:
        Dictionary containing gaps with priority levels
    """
    try:
        checker = CapabilityChecker()
        gaps = checker.list_gaps()

        # Organize by priority
        critical_gaps = []
        medium_gaps = []
        enhancement_gaps = []

        for gap_name, priority in gaps.items():
            gap_info = {"name": gap_name, "priority": priority}

            if priority == "CRITICAL":
                critical_gaps.append(gap_info)
            elif priority == "MEDIUM":
                medium_gaps.append(gap_info)
            else:
                enhancement_gaps.append(gap_info)

        return {
            "total_gaps": len(gaps),
            "critical": critical_gaps,
            "medium": medium_gaps,
            "enhancements": enhancement_gaps,
            "all_gaps": gaps,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list gaps: {str(e)}")


@router.post("/check-capability")
async def check_capability(req: CheckCapabilityRequest) -> CapabilityCheckResponse:
    """
    Check if a specific capability already exists in the system.

    Args:
        req: CheckCapabilityRequest with capability name

    Returns:
        CapabilityCheckResponse with recommendation
    """
    try:
        checker = CapabilityChecker()
        result = checker.check_capability_exists(req.capability)

        return CapabilityCheckResponse(
            exists=result.exists,
            agents_with_capability=result.agents_with_capability,
            recommendation=result.recommendation.value,
            rationale=result.rationale,
            target_agent=result.target_agent,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Capability check failed: {str(e)}"
        )


@router.post("/suggest-agent")
async def suggest_agent_creation(req: SuggestAgentRequest) -> CapabilityCheckResponse:
    """
    Analyze if new agent should be created or existing one enhanced.

    Args:
        req: SuggestAgentRequest with agent name and capabilities

    Returns:
        CapabilityCheckResponse with detailed recommendation
    """
    try:
        checker = CapabilityChecker()
        result = checker.suggest_agent_creation(req.agent_name, req.capabilities)

        return CapabilityCheckResponse(
            exists=result.exists,
            agents_with_capability=result.agents_with_capability,
            recommendation=result.recommendation.value,
            rationale=result.rationale,
            target_agent=result.target_agent,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Agent suggestion failed: {str(e)}"
        )


@router.get("/capability/{capability_name}")
async def get_agent_by_capability(capability_name: str) -> Dict[str, Any]:
    """
    Find agent that provides a specific capability.

    Args:
        capability_name: Name of capability to search for

    Returns:
        Agent information if found
    """
    try:
        checker = CapabilityChecker()
        agent = checker.get_agent_by_capability(capability_name)

        if not agent:
            return {
                "found": False,
                "message": f"No agent found with capability '{capability_name}'",
            }

        return {
            "found": True,
            "agent": {
                "id": agent.id,
                "file": agent.file,
                "role": agent.role,
                "capabilities": agent.capabilities,
                "status": agent.status,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Capability search failed: {str(e)}"
        )
