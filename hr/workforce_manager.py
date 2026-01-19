import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from ..utils.logging_config import get_logger
from ..agents.base import Agent, AgentRole

logger = get_logger(__name__)

@dataclass
class AgentRegistration:
    """Registration record for an agent in the workforce."""
    agent: Agent
    role: AgentRole
    schedule: Optional[str] = None  # Cron-like schedule
    enabled: bool = True
    last_run: Optional[datetime] = None
    run_count: int = 0
    failure_count: int = 0


class WorkforceManager:
    """
    إدارة شؤون الموظفين (HR Department)
    
    Responsibilities:
    - Agent lifecycle management (start/stop/restart)
    - Health monitoring
    - Performance tracking
    - Coordination with scheduler
    
    This is the missing piece that activates the dormant system.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentRegistration] = {}
        self.running = False
        logger.info("🏛️ WorkforceManager initialized")
    
    def register_agent(
        self, 
        agent: Agent, 
        schedule: Optional[str] = None,
        enabled: bool = True
    ) -> None:
        """
        Register an agent with the workforce.
        
        Args:
            agent: The agent instance
            schedule: Cron-like schedule (e.g., "*/5 * * * *" for every 5 min)
            enabled: Whether the agent is active
        """
        registration = AgentRegistration(
            agent=agent,
            role=agent.role,
            schedule=schedule,
            enabled=enabled
        )
        
        self.agents[agent.agent_id] = registration
        logger.info(f"✅ Agent registered: {agent.agent_id} ({agent.role.value})")
        
        if schedule:
            logger.info(f"   📅 Schedule: {schedule}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the workforce."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"❌ Agent unregistered: {agent_id}")
    
    def enable_agent(self, agent_id: str) -> None:
        """Enable a disabled agent."""
        if agent_id in self.agents:
            self.agents[agent_id].enabled = True
            logger.info(f"✅ Agent enabled: {agent_id}")
    
    def disable_agent(self, agent_id: str) -> None:
        """Disable an agent (soft stop)."""
        if agent_id in self.agents:
            self.agents[agent_id].enabled = False
            logger.info(f"⏸️ Agent disabled: {agent_id}")
    
    def get_status_report(self) -> Dict:
        """
        Generate a comprehensive status report of all agents.
        
        Returns:
            Dictionary with workforce statistics and agent statuses
        """
        total = len(self.agents)
        enabled = sum(1 for a in self.agents.values() if a.enabled)
        disabled = total - enabled
        
        agent_statuses = []
        for agent_id, reg in self.agents.items():
            agent_statuses.append({
                "agent_id": agent_id,
                "role": reg.role.value,
                "enabled": reg.enabled,
                "schedule": reg.schedule,
                "last_run": reg.last_run.isoformat() if reg.last_run else None,
                "run_count": reg.run_count,
                "failure_count": reg.failure_count,
                "success_rate": (
                    (reg.run_count - reg.failure_count) / reg.run_count * 100
                    if reg.run_count > 0 else 0
                )
            })
        
        return {
            "total_agents": total,
            "enabled_agents": enabled,
            "disabled_agents": disabled,
            "running": self.running,
            "agents": agent_statuses
        }
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        reg = self.agents.get(agent_id)
        return reg.agent if reg else None
    
    def list_agents(self, role: Optional[AgentRole] = None) -> List[Agent]:
        """
        List all agents, optionally filtered by role.
        
        Args:
            role: Optional role filter
            
        Returns:
            List of agent instances
        """
        agents = [reg.agent for reg in self.agents.values()]
        
        if role:
            agents = [a for a in agents if a.role == role]
        
        return agents
    
    def record_run(self, agent_id: str, success: bool = True) -> None:
        """Record an agent execution."""
        if agent_id in self.agents:
            reg = self.agents[agent_id]
            reg.last_run = datetime.now()
            reg.run_count += 1
            
            if not success:
                reg.failure_count += 1
                logger.warning(f"⚠️ Agent {agent_id} execution failed")
    
    def start(self) -> None:
        """Start the workforce manager."""
        self.running = True
        logger.info("🚀 WorkforceManager started")
    
    def stop(self) -> None:
        """Stop the workforce manager."""
        self.running = False
        logger.info("🛑 WorkforceManager stopped")
