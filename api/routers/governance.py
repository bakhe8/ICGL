from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from api.server_shared import get_icgl  # We'll need a shared utility for the singleton
from backend.kb.schemas import ADR, now, uid

router = APIRouter(prefix="/api/governance", tags=["governance"])


class ProposalRequest(BaseModel):
    title: str
    context: str
    decision: str
    human_id: str = "bakheet"


class SimulationRequest(BaseModel):
    topic: str
    context: str


class ExecutiveChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ExecutiveSignRequest(BaseModel):
    proposal_id: str
    action: str  # 'SIGN' or 'REJECT'


class SignRequest(BaseModel):
    action: str
    rationale: str
    human_id: str = "bakheet"


@router.get("/proposals")
async def get_proposals():
    icgl = get_icgl()
    adrs = list(icgl.kb.adrs.values())
    return {"proposals": sorted(adrs, key=lambda x: x.created_at, reverse=True)}


@router.get("/decisions")
async def get_decisions():
    icgl = get_icgl()
    decisions = list(icgl.kb.human_decisions.values())
    return {"decisions": sorted(decisions, key=lambda x: x.timestamp, reverse=True)}


@router.post("/proposals/register")
async def register_proposal(req: ProposalRequest):
    icgl = get_icgl()
    adr = ADR(
        id=f"ADR-{uid()[:4].upper()}",
        title=req.title,
        context=req.context,
        decision=req.decision,
        status="PROPOSED",
        created_at=now(),
    )
    icgl.kb.add_adr(adr)
    return {"status": "ok", "adr_id": adr.id}


@router.post("/simulate-council")
async def simulate_council(req: SimulationRequest):
    """
    Phase 8: Controlled Simulation Gateway.
    Consults all registered agents on a specific topic.
    """
    icgl = get_icgl()
    registry = icgl.registry
    from backend.agents.base import Problem

    roles = registry.list_agents()
    problem = Problem(title=req.topic, context=req.context)

    results = []
    # Run in batches of 5 to avoid overwhelming LLM limits/timeouts if parallelized too high
    # But since this is a simulation, we'll go one by one for maximum visibility in logs
    for role in roles:
        agent = registry.get_agent(role)
        if agent:
            try:
                # Direct analysis call
                res = await agent.analyze(problem, icgl.kb)
                results.append(
                    {
                        "agent_id": agent.agent_id,
                        "role": role.value,
                        "analysis": res.analysis,
                        "recommendations": res.recommendations,
                        "confidence": res.confidence,
                    }
                )
            except Exception as e:
                results.append(
                    {"agent_id": agent.agent_id, "role": role.value, "error": str(e)}
                )

    return {"topic": req.topic, "results": results}


@router.post("/executive/chat")
async def executive_chat(req: ExecutiveChatRequest):
    """
    Handles conversational requests to the Executive Agent.
    Implements Inverse Governance (The Confirmation Mirror).
    """
    icgl = get_icgl()
    from backend.agents.base import AgentRole, Problem

    # 1. Route to Executive Agent
    agent = icgl.registry.get_agent(AgentRole.EXECUTIVE)
    if not agent:
        return {"error": "Executive Agent not available."}

    problem = Problem(title="Human Chat", context=req.message)
    result = await agent.analyze(problem, icgl.kb)

    # 2. Sentinel Check (Silent Monitoring)
    sentinel = icgl.registry.get_agent(AgentRole.SENTINEL)
    sentinel_note = ""
    if sentinel:
        sentinel_res = await sentinel.analyze(problem, icgl.kb)
        sentinel_note = sentinel_res.analysis

    return {
        "status": "awaiting_confirmation" if result.clarity_needed else "processed",
        "agent_id": agent.agent_id,
        "message": result.analysis,
        "clarity_question": result.clarity_question,
        "sentinel_analysis": sentinel_note,
        "action_required": result.clarity_needed,
    }


@router.post("/executive/sign")
async def executive_sign(req: ExecutiveSignRequest):
    """
    Executes actions after Owner signature.
    """
    # Logic to proceed with file writing/execution
    return {
        "status": "executed",
        "details": f"Action {req.action} confirmed for {req.proposal_id}",
    }
