import asyncio
import sys
from pathlib import Path

# Add src
sys.path.append(str(Path.cwd() / "src"))

from icgl.kb import PersistentKnowledgeBase, Policy, OperationalRequest, uid, now

async def operationalize_autonomy():
    print("🧠 OPERATIONALIZING AGENT FOUNDATIONAL AUTONOMY")
    print("===============================================")
    
    kb = PersistentKnowledgeBase()
    
    # 1. Register Policy P-OPS-05
    policy_05 = Policy(
        id=uid(),
        code="P-OPS-05",
        title="Agent Foundational Autonomy",
        rule="Each Agent is responsible for fulfilling its operational needs via formal governed requests.",
        severity="MEDIUM",
        enforced_by=["ICGL Orchestrator", "Sentinel"]
    )
    
    kb.add_policy(policy_05)
    print(f"✅ Policy Registered: {policy_05.code} - {policy_05.title}")
    
    # 2. Simulate an Agent Request (MonitorAgent needs a new tool)
    request = OperationalRequest(
        id=uid(),
        requester_id="MonitorAgent",
        target_department="Engineering",
        requirement="Real-time Incident Notification Slack Hook",
        rationale="Required to fulfill P-GM-02 (Proactive Governance) for immediate stakeholder alert."
    )
    
    kb.add_request(request)
    print(f"\n📨 FORMAL REQUEST ISSUED:")
    print(f"   From: {request.requester_id}")
    print(f"   To:   {request.target_department}")
    print(f"   Need: {request.requirement}")
    print(f"   Log:  {request.id}")
    
    # 3. Verification of Governance Submission
    print(f"\n⚖️ Governance Status: {request.status}")
    print("   (System successfully documented the request. Ready for ADR elevation).")

if __name__ == "__main__":
    asyncio.run(operationalize_autonomy())
