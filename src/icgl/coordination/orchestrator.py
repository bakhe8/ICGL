import asyncio
from typing import Dict, Any, Optional, List
from ..kb import PersistentKnowledgeBase, OperationalRequest, uid, now
from ..observability import get_ledger, ObservabilityEvent, EventType
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class CoordinationOrchestrator:
    """
    🏛️ Inter-Department Coordination Protocol (IDCP) Enforcer.
    
    Acts as the ONLY authorized gateway for Agents to request 
    resources from other departments.
    """
    
    def __init__(self, kb: Optional[PersistentKnowledgeBase] = None):
        self.kb = kb or PersistentKnowledgeBase()
        self.ledger = get_ledger()

    async def submit_request(
        self, 
        requester: str, 
        department: str, 
        requirement: str, 
        rationale: str,
        urgency: str = "MEDIUM",
        expected_output: str = "",
        risk_level: str = "LOW"
    ) -> str:
        """
        1️⃣ Need Detection & 2️⃣ Formal Request stages.
        """
        request = OperationalRequest(
            id=uid(),
            requester_id=requester,
            target_department=department,
            requirement=requirement,
            rationale=rationale,
            urgency=urgency,
            expected_output=expected_output,
            risk_level=risk_level,
            status="PENDING"
        )
        
        # Log to KB for Traceability
        self.kb.add_request(request)
        
        # Log to Observability
        if self.ledger:
            self.ledger.log(ObservabilityEvent(
                event_id=uid(),
                event_type=EventType.AGENT_INVOKED,
                timestamp=now(),
                trace_id=uid(),
                span_id="idcp-submit",
                actor_type="agent",
                actor_id=requester,
                action="submit_operational_request",
                target=department,
                input_payload=request.__dict__,
                status="success"
            ))
            
        logger.info(f"🏛️ IDCP: Formal Request {request.id} submitted from {requester} to {department}")
        return request.id

    async def fulfill_request(self, request_id: str, department_agent: str, output_data: str):
        """
        3️⃣ Department Fulfillment stage.
        """
        if request_id not in self.kb.requests:
            raise ValueError(f"Request {request_id} not found in KB")
            
        request = self.kb.requests[request_id]
        request.response_data = output_data
        request.status = "APPROVED" # Provisional approval by department
        request.updated_at = now()
        
        logger.info(f"🏛️ IDCP: Request {request_id} fulfilled by {department_agent}. Awaiting Governance.")

    async def verify_governance(self, request_id: str, signed_by: str, adr_id: str):
        """
        4️⃣ Governance Elevation stage.
        
        ADR-CANONICAL-001 Compliance:
        Establishes automatic bidirectional linkage between OperationalRequest and ADR.
        """
        if request_id not in self.kb.requests:
            raise ValueError(f"Request {request_id} not found in KB")
            
        # Automatic Request-ADR Binding (ADR-CANONICAL-001 §3.1)
        request = self.kb.requests[request_id]
        request.governance_adr_id = adr_id
        
        self.kb.update_request_status(request_id, "FULFILLED", adr_id=adr_id)
        logger.info(f"🏛️ IDCP: Request {request_id} SIGNED and APPROVED by {signed_by}. Execution authorized.")
        logger.info(f"✅ ADR-CANONICAL-001: Automatic linkage established: Request {request_id} ↔ ADR {adr_id}")

    def get_pending_requests(self) -> List[OperationalRequest]:
        return [r for r in self.kb.requests.values() if r.status == "PENDING"]
    
    def validate_adr_request_binding(self, adr_id: str) -> bool:
        """
        ADR-CANONICAL-001 §3.1: Mechanical validation.
        Prevents ADR approval if no valid originating request exists.
        """
        for request in self.kb.requests.values():
            if request.governance_adr_id == adr_id:
                return True
        logger.warning(f"⚠️ ADR-CANONICAL-001 Violation: ADR {adr_id} has no linked OperationalRequest")
        return False
