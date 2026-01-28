from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AgentEntry(BaseModel):
    id: str
    role: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class AgentsList(BaseModel):
    total: int
    agents: List[AgentEntry]


class GapsList(BaseModel):
    gaps: List[Dict[str, Any]] = []


class AgentRoleResp(BaseModel):
    id: str
    role: Optional[str] = None


class AgentHistoryResp(BaseModel):
    history: List[Dict[str, Any]] = []


class AgentStatsResp(BaseModel):
    stats: Dict[str, Any] = {}


class ADRSummary(BaseModel):
    id: str
    title: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class ExecutiveQueue(BaseModel):
    queue: List[ADRSummary] = []


class TransactionItem(BaseModel):
    id: Optional[str]
    type: Optional[str]
    detail: Optional[Dict[str, Any]]


class TransactionsList(BaseModel):
    transactions: List[TransactionItem]
    count: int


class PulsePayload(BaseModel):
    type: str
    stats: Dict[str, Any]


class SecretaryLogsResp(BaseModel):
    logs: List[Dict[str, Any]]
    status: Optional[str] = "ok"


class SentinelMetricsResp(BaseModel):
    metrics: Dict[str, Any]


class TrafficResp(BaseModel):
    traffic: List[Dict[str, Any]]


class OperationResult(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None


class StatusResp(BaseModel):
    status: str


class DocsTreeResp(BaseModel):
    roots: List[Dict[str, Any]] = []


class DocsContentResp(BaseModel):
    path: str
    content: str
    mime: str


class DocsSaveResp(BaseModel):
    status: str
    path: Optional[str] = None


class ProposalsList(BaseModel):
    proposals: List[ADRSummary]


class ProposalResp(BaseModel):
    proposal: Optional[Dict[str, Any]] = None


class DecisionsResp(BaseModel):
    decisions: List[Dict[str, Any]] = []


class TimelineResp(BaseModel):
    timeline: List[Dict[str, Any]] = []


class LatestAdrResp(BaseModel):
    adr: Optional[Dict[str, Any]] = None


class ConflictsResp(BaseModel):
    conflicts: List[Dict[str, Any]] = []


class HealthResp(BaseModel):
    api: str
    env_loaded: bool
    db_lock: Optional[str] = None
    engine_ready: bool
    db_error: Optional[str] = None


class GenericDataResp(BaseModel):
    data: Dict[str, Any] = {}


class ListDataResp(BaseModel):
    items: List[Dict[str, Any]] = []


class ObservabilityStatsResp(BaseModel):
    stats: Dict[str, Any] = {}


class TracesResp(BaseModel):
    traces: List[Dict[str, Any]] = []
    count: int = 0


class TraceDetailsResp(BaseModel):
    trace_id: str
    event_count: int
    events: List[Dict[str, Any]] = []


class EventsResp(BaseModel):
    events: List[Dict[str, Any]] = []
    count: int = 0
