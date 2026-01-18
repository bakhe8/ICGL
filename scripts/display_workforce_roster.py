"""
Display Complete Workforce Roster
Shows all registered agents in HR Department
"""

import asyncio
from icgl.hr import WorkforceManager
from icgl.agents import *
from icgl.agents.sentinel_agent import SentinelAgent
from icgl.agents.policy import PolicyAgent
from icgl.agents.documentation_agent import DocumentationAgent
from icgl.agents.engineer import EngineerAgent
from icgl.agents.mediator import MediatorAgent
from icgl.agents.guardian import ConceptGuardian
from icgl.agents.failure import FailureAgent


async def main():
    print("\n" + "="*80)
    print("📋 سجل الموظفين الكامل (Complete Workforce Roster)")
    print("="*80 + "\n")
    
    # Initialize WorkforceManager
    workforce = WorkforceManager()
    
    # Register all agents (same as in activate_hr_department.py)
    agents_to_register = [
        (MonitorAgent("SovereignMonitor"), "*/5 * * * *", "System Health Monitoring"),
        (ArchivistAgent("SovereignArchivist"), "0 * * * *", "Document Management"),
        (SecretaryAgent("SovereignSecretary"), None, "Executive Assistant"),
        (SentinelAgent("SovereignSentinel"), "*/10 * * * *", "Security & Policy Enforcement"),
        (PolicyAgent("PolicyEnforcer"), None, "Policy Enforcement"),
        (DocumentationAgent("DocumentationSpecialist"), None, "Code Documentation"),
        (BuilderAgent("CodeBuilder"), None, "Code Generation"),
        (ArchitectAgent("SystemArchitect"), None, "System Architecture"),
        (EngineerAgent("SystemEngineer"), None, "Code Execution"),
        (MediatorAgent("AgentMediator"), None, "Agent Coordination"),
        (ConceptGuardian("KnowledgeGuardian"), "0 0 * * *", "Knowledge Base Integrity"),
        (FailureAgent("FailureAnalyst"), None, "Error Analysis"),
    ]
    
    for agent, schedule, description in agents_to_register:
        workforce.register_agent(agent, schedule=schedule, enabled=True)
    
    # Get status report
    status = workforce.get_status_report()
    
    print(f"إجمالي الموظفين: {status['total_agents']}")
    print(f"الموظفون النشطون: {status['enabled_agents']}")
    print(f"الموظفون المعطلون: {status['disabled_agents']}")
    print("\n" + "-"*80 + "\n")
    
    # Display roster
    print("الموظفون المسجلون:\n")
    
    scheduled = []
    on_demand = []
    
    for agent_info in status['agents']:
        if agent_info['schedule']:
            scheduled.append(agent_info)
        else:
            on_demand.append(agent_info)
    
    print("🕐 الموظفون المجدولون (Scheduled Agents):")
    print("-" * 80)
    for i, agent in enumerate(scheduled, 1):
        print(f"{i}. {agent['agent_id']}")
        print(f"   الدور: {agent['role']}")
        print(f"   الجدول: {agent['schedule']}")
        print(f"   الحالة: {'✅ نشط' if agent['enabled'] else '❌ معطل'}")
        print()
    
    print("\n📞 الموظفون عند الطلب (On-Demand Agents):")
    print("-" * 80)
    for i, agent in enumerate(on_demand, 1):
        print(f"{i}. {agent['agent_id']}")
        print(f"   الدور: {agent['role']}")
        print(f"   الحالة: {'✅ جاهز' if agent['enabled'] else '❌ معطل'}")
        print()
    
    print("="*80)
    print(f"\n✅ جميع الموظفين ({status['total_agents']}) مسجلون في إدارة شؤون الموظفين")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
