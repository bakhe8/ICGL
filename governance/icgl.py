import asyncio
from typing import List, Optional, Dict, Any
from agents.base import Problem, AgentRole, AgentResult
from api.services.consensus_service import ConsensusService
from utils.logging_config import get_logger

logger = get_logger(__name__)

class ICGL:
    """
    ICGL (Iterative Co-Governance Loop) Orchestrator.
    Handles the orchestration of multi-agent analysis and lifecycle of architectural decisions.
    """
    
    def __init__(self):
        self.consensus = ConsensusService()
        self.active_agents = [
            AgentRole.ARCHITECT,
            AgentRole.POLICY,
            AgentRole.SENTINEL
        ]

    async def run_governance_cycle(self, adr_data: Any, human_id: str = "operator"):
        """
        Executes a full multi-agent governance cycle for a given ADR.
        """
        from agents import AgentRegistry
        registry = AgentRegistry()
        
        # 1. Prepare Problem
        problem = Problem(
            title=adr_data.title,
            context=adr_data.context,
            metadata={
                "decision": adr_data.decision,
                "author": adr_data.author if hasattr(adr_data, "author") else "operator"
            }
        )
        
        logger.info(f"🔄 Starting ICGL Cycle for: {problem.title}")
        
        # 2. Parallel Agent Analysis
        analysis_tasks = []
        for role in self.active_agents:
            analysis_tasks.append(registry.run_agent(role, problem, kb=self.consensus))
            
        results: List[AgentResult] = await asyncio.gather(*analysis_tasks)
        
        # 3. Synthesis (Simple for now)
        concerns = []
        recommendations = []
        for res in results:
            if res:
                concerns.extend(res.concerns)
                recommendations.extend(res.recommendations)
                
        logger.info(f"✅ ICGL Cycle Analysis Complete. Found {len(concerns)} concerns and {len(recommendations)} recommendations.")
        
        # 4. Update ADR with analysis results (Mocked persistence update for now)
        # In a real system, we'd record these in the ADR record.
        
        return {
            "status": "analyzed",
            "results": results,
            "concerns": concerns,
            "recommendations": recommendations
        }

    async def propose_and_run(self, title: str, context: str, decision: str, human_id: str = "operator"):
        """
        High-level helper to propose an ADR and immediately run analysis.
        """
        adr = self.consensus.propose_adr(title, context, decision)
        # Map dict to object-like structure for the orchestrator if needed
        from types import SimpleNamespace
        adr_obj = SimpleNamespace(**adr)
        
        result = await self.run_governance_cycle(adr_obj, human_id=human_id)
        return adr, result
