import json
from collections import Counter
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/agents", tags=["Agents Portfolio"])


# Helper to load run logs
def load_all_runs():
    """Scans data/logs/idea_runs.jsonl and runs/*.json"""
    runs = []

    # Check detailed JSON runs first (richer data)
    runs_dir = Path("runs")
    if runs_dir.exists():
        for run_file in runs_dir.glob("*.json"):
            try:
                with open(run_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    runs.append(data)
            except Exception:
                continue

    return runs


def match_agent(agent_results, agent_id):
    """
    Finds an agent's contribution in a list of results using loose matching.
    Matches if:
    - ID equals, contains, or is contained by query.
    - Role equals, contains, or is contained by query.
    """
    for r in agent_results:
        r_id = r.get("agent_id", "").lower()
        r_role = r.get("role", "").lower()
        query = agent_id.lower()

        # Check ID
        if r_id and (r_id == query or r_id in query or query in r_id):
            return r
        # Check Role
        if r_role and (r_role == query or r_role in query or query in r_role):
            return r

    return None


@router.get("/{agent_id}/history")
async def get_agent_history(agent_id: str):
    """
    Returns the work history of a specific agent.
    """
    all_runs = load_all_runs()
    history = []

    for run in all_runs:
        agent_results = run.get("synthesis", {}).get("agent_results", [])

        contribution = match_agent(agent_results, agent_id)

        if contribution:
            history.append(
                {
                    "run_id": run.get("adr", {}).get("id"),
                    "title": run.get("adr", {}).get("title"),
                    "timestamp": run.get("timestamp"),
                    "role": contribution.get("role"),
                    "summary": contribution.get("analysis", "")[:200] + "...",
                    "confidence": contribution.get("confidence", 0.0),
                    "verdict": "APPROVED"
                    if not contribution.get("concerns")
                    else "WARN",
                    "concerns_count": len(contribution.get("concerns", [])),
                    "tags": extract_tags(contribution.get("analysis", "")),
                }
            )

    # Sort by date desc
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"history": history}


@router.get("/{agent_id}/stats")
async def get_agent_stats(agent_id: str):
    """
    Returns calculated analytics for the agent.
    """
    all_runs = load_all_runs()
    contributions = []

    for run in all_runs:
        res = run.get("synthesis", {}).get("agent_results", [])
        match = match_agent(res, agent_id)
        if match:
            contributions.append(match)

    if not contributions:
        return {
            "total_runs": 0,
            "approval_rate": 0,
            "strictness": 0,
            "top_keywords": [],
        }

    total = len(contributions)
    # Approval rate: Low concern count
    approvals = sum(1 for c in contributions if not c.get("concerns"))
    avg_confidence = sum(c.get("confidence", 0) for c in contributions) / total

    # Extract keywords
    text_blob = " ".join([c.get("analysis", "") for c in contributions])
    keywords = extract_keywords(text_blob)

    return {
        "total_runs": total,
        "approval_rate": round(approvals / total, 2),
        "strictness": round(1.0 - avg_confidence, 2),
        "strictness_real": round(
            sum(1 for c in contributions if len(c.get("concerns", [])) > 0) / total, 2
        ),
        "top_keywords": keywords[:5],
    }


def extract_tags(text: str):
    """Simple tag extraction based on keywords."""
    tags = []
    keywords = [
        "security",
        "policy",
        "code",
        "architecture",
        "frontend",
        "backend",
        "database",
        "documentation",
    ]
    text_lower = text.lower()
    for k in keywords:
        if k in text_lower:
            tags.append(k)
    return tags


@router.get("/{agent_id}/role")
async def get_agent_role(agent_id: str):
    """
    Returns the dynamic role definition (System Prompt) from the live agent instance.
    """
    # Lazy import to avoid circular dependency
    from api.server_shared import get_icgl

    try:
        icgl = get_icgl()
        registry = icgl.registry

        # Try to find the agent
        target_agent = None

        # 1. Try generic get_agent via string (if enhanced registry supported it)
        # 2. Try iterating registry (registry._agents is Dict[AgentRole, Agent])

        # Search by ID or Role Value matching
        for role_enum, agent in registry._agents.items():
            if (
                agent.agent_id == agent_id
                or role_enum.value == agent_id
                or agent_id in role_enum.value
            ):  # Loose match
                target_agent = agent
                break

        if not target_agent:
            return {
                "role_definition": "Agent active but instance not found in registry memory."
            }

        # Dynamic retrieval
        prompt = target_agent.get_system_prompt()

        return {
            "agent_id": target_agent.agent_id,
            "role_name": target_agent.role.value,
            "role_definition": prompt,
        }

    except Exception as e:
        return {
            "error": str(e),
            "role_definition": "Could not retrieve role definition.",
        }


def extract_keywords(text: str):
    """Extract most common words (ignoring stops)."""
    words = text.lower().split()
    stops = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "of",
        "to",
        "in",
        "on",
        "for",
        "with",
        "this",
        "that",
        "it",
    }
    filtered = [w for w in words if w.isalnum() and w not in stops and len(w) > 3]
    return Counter(filtered).most_common(10)
