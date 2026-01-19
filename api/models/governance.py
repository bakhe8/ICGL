from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

ProposalState = Literal["open", "draft", "discussion", "ready", "decision", "archived"]
DecisionState = Literal["pending", "approved", "rejected", "deferred"]
ConflictState = Literal["open", "resolved", "archived"]


class ProposalPayload(BaseModel):
    title: str
    description: str
    author: str = "operator"
    reason: str
    impact: str
    risks: str
    alternatives: Optional[str] = None
    cost_or_complexity: Optional[str] = None
    execution_plan: Optional[str] = None
    consultation_notes: Optional[str] = None
    state: ProposalState = "open"
    tags: List[str] = []


class ProposalRecord(ProposalPayload):
    id: str
    created_at: datetime
    updated_at: datetime
    assigned_agents: List[str] = []
    comments: List[str] = []


class ProposalUpdate(BaseModel):
    state: Optional[ProposalState] = None
    comment: Optional[str] = None
    tags: Optional[List[str]] = None
    assigned_agents: Optional[List[str]] = None


class DecisionPayload(BaseModel):
    proposal_id: str
    decision: DecisionState
    rationale: str
    signed_by: str = "operator"


class ConflictPayload(BaseModel):
    title: str
    description: str
    proposals: List[str] = []
    involved_agents: List[str] = []
    state: ConflictState = "open"


class ConflictUpdate(BaseModel):
    state: Optional[ConflictState] = None
    resolution: Optional[str] = None
    comment: Optional[str] = None
