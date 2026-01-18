"""
Activate HR Department and Start the Sovereign Heartbeat

This script:
1. Initializes the HR Department (WorkforceManager)
2. Registers all existing agents
3. Schedules periodic tasks
4. Starts the Heartbeat Service
5. Brings the system to life
"""

import asyncio
from icgl.hr import WorkforceManager, AgentScheduler, HeartbeatService
from icgl.agents import MonitorAgent, ArchivistAgent, SecretaryAgent
from icgl.utils.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("🏛️ Activating HR Department...")
    
    # 1. Initialize HR Department
    workforce = WorkforceManager()
    scheduler = AgentScheduler(workforce_manager=workforce)
    heartbeat = HeartbeatService(workforce_manager=workforce, interval_seconds=300)  # 5 minutes
    
    # 2. Register ALL Agents
    logger.info("📋 Registering all agents in the system...")
    
    # === Core Operational Agents ===
    
    # MonitorAgent - System health monitoring (every 5 minutes)
    monitor = MonitorAgent("SovereignMonitor")
    workforce.register_agent(monitor, schedule="*/5 * * * *", enabled=True)
    
    # ArchivistAgent - Document management (hourly with CEO reporting)
    archivist = ArchivistAgent("SovereignArchivist")
    workforce.register_agent(archivist, schedule="0 * * * *", enabled=True)
    
    # SecretaryAgent - Executive assistant (always available, on-demand)
    secretary = SecretaryAgent("SovereignSecretary")
    workforce.register_agent(secretary, schedule=None, enabled=True)
    
    # SentinelAgent - Security and policy enforcement (every 10 minutes)
    from icgl.agents.sentinel_agent import SentinelAgent
    sentinel = SentinelAgent("SovereignSentinel")
    workforce.register_agent(sentinel, schedule="*/10 * * * *", enabled=True)
    
    # === Governance Agents ===
    
    # PolicyAgent - Policy enforcement (on-demand)
    from icgl.agents.policy import PolicyAgent
    policy_agent = PolicyAgent("PolicyEnforcer")
    workforce.register_agent(policy_agent, schedule=None, enabled=True)
    
    # === Development Agents ===
    
    # DocumentationAgent - Code documentation (on-demand)
    from icgl.agents.documentation_agent import DocumentationAgent
    doc_agent = DocumentationAgent("DocumentationSpecialist")
    workforce.register_agent(doc_agent, schedule=None, enabled=True)
    
    # BuilderAgent - Code generation (on-demand)
    builder = BuilderAgent("CodeBuilder")
    workforce.register_agent(builder, schedule=None, enabled=True)
    
    # ArchitectAgent - System architecture (on-demand)
    architect = ArchitectAgent("SystemArchitect")
    workforce.register_agent(architect, schedule=None, enabled=True)
    
    # EngineerAgent - Code execution (on-demand)
    from icgl.agents.engineer import EngineerAgent
    engineer = EngineerAgent("SystemEngineer")
    workforce.register_agent(engineer, schedule=None, enabled=True)
    
    # === Coordination Agents ===
    
    # MediatorAgent - Agent coordination (on-demand)
    from icgl.agents.mediator import MediatorAgent
    mediator = MediatorAgent("AgentMediator")
    workforce.register_agent(mediator, schedule=None, enabled=True)
    
    # === Knowledge Agents ===
    
    # ConceptGuardian - Knowledge base integrity (daily)
    from icgl.agents.guardian import ConceptGuardian
    guardian = ConceptGuardian("KnowledgeGuardian")
    workforce.register_agent(guardian, schedule="0 0 * * *", enabled=True)
    
    # FailureAgent - Error analysis (on-demand)
    from icgl.agents.failure import FailureAgent
    failure_agent = FailureAgent("FailureAnalyst")
    workforce.register_agent(failure_agent, schedule=None, enabled=True)
    
    # 3. Schedule Tasks
    logger.info("📅 Scheduling tasks...")
    
    # Example: MonitorAgent periodic check
    async def monitor_task():
        logger.info("🔍 MonitorAgent: Performing system check...")
        # In real implementation, call monitor.analyze() with proper context
    
    scheduler.schedule_task(
        task_id="monitor_system_check",
        cron_expression="*/5 * * * *",  # Every 5 minutes
        task_func=monitor_task,
        agent_id="SovereignMonitor"
    )
    
    # Archivist hourly audit with automatic CEO reporting
    async def archivist_audit_and_report():
        logger.info("📚 ArchivistAgent: Performing KB audit and submitting report to CEO...")
        try:
            # Get KB instance
            from icgl.kb import PersistentKnowledgeBase
            kb = PersistentKnowledgeBase()
            
            # Submit report through Secretary to CEO
            report = await archivist.submit_report_to_ceo(kb, secretary_agent=secretary)
            
            # Log the report submission
            logger.info(f"✅ Report submitted to CEO via SecretaryAgent")
            logger.info(f"   Priority: {report.get('priority')}")
            logger.info(f"   Summary: {report.get('summary_ar', '')[:100]}...")
            
            # TODO: In production, this should trigger a notification to CEO dashboard
            
        except Exception as e:
            logger.error(f"❌ Archivist audit failed: {e}")
    
    scheduler.schedule_task(
        task_id="archivist_audit_and_report",
        cron_expression="0 * * * *",  # Every hour
        task_func=archivist_audit_and_report,
        agent_id="SovereignArchivist"
    )
    
    # 4. Start Services
    logger.info("🚀 Starting HR services...")
    workforce.start()
    
    # Print status
    status = workforce.get_status_report()
    logger.info(f"✅ Workforce Status: {status['enabled_agents']}/{status['total_agents']} agents active")
    
    # 5. Start Heartbeat (this will run forever)
    logger.info("💓 Starting Sovereign Heartbeat...")
    logger.info("   Press Ctrl+C to stop")
    
    try:
        # Run scheduler and heartbeat concurrently
        await asyncio.gather(
            scheduler.run(),
            heartbeat.start()
        )
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down HR Department...")
        scheduler.stop()
        heartbeat.stop()
        workforce.stop()
        logger.info("✅ HR Department stopped gracefully")


if __name__ == "__main__":
    asyncio.run(main())
