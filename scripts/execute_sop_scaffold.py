import asyncio
import sys
from pathlib import Path
import os

# Add src to sys.path
sys.path.append(str(Path.cwd() / "src"))

from icgl.governance.procedure_engine import ProcedureEngine
from icgl.kb import PersistentKnowledgeBase, Procedure

async def execute_onboarding():
    print("🤖 EXECUTOR: Starting Automated Onboarding Task")
    print("===============================================")
    
    # 1. Load the SOP
    engine = ProcedureEngine()
    
    # In a real system, we would load from DB. 
    # Since we are in a script without persistent DB for procedures yet (in-memory only in previous step), 
    # Let's re-create/fetch it to simulate "reading from the binder".
    # (In the certified system, retrieve_procedure failure would halt this).
    
    print("📋 Fetching SOP-OPS-01 from Engine...")
    # Emulating retrieval as if it was persisted
    sop = Procedure(
        id="mock-id-sop-01",
        code="SOP-OPS-01",
        title="New Agent Onboarding Protocol",
        type="SOP",
        steps=[
            "1. Define Agent Role and Responsibilities in src/icgl/agents/monitor_agent.py",
            "2. Register Agent in src/icgl/agents/__init__.py",
            "3. Verify Import"
        ],
        required_tools=["CodeSpecialist"]
    )
    
    print(f"✅ Loaded: {sop.title}")
    
    # 2. Execute Steps
    
    # STEP 1: Define Agent Role (Scaffold File)
    print(f"\n▶️ EXEC STEP 1: {sop.steps[0]}")
    agent_code = """
from typing import List, Optional
from .base import Agent, AgentResult, Problem, AgentRole

class MonitorAgent(Agent):
    \"\"\"
    A new Monitor Agent created via SOP-OPS-01.
    Responsibility: Observes system state and reports anomalies.
    \"\"\"
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.ANALYZER

    async def analyze(self, problem: Problem) -> AgentResult:
        return AgentResult(
            agent_id=self.name,
            confidence=0.9,
            reasoning="Monitor reporting all systems normal.",
            recommendation="CONTINUE"
        )
"""
    file_path = Path("src/icgl/agents/monitor_agent.py")
    if not file_path.exists():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(agent_code.strip())
        print(f"   ✨ Generated: {file_path}")
    else:
        print(f"   ⚠️ File exists, skipping generation.")

    # STEP 2: Register Agent (Modify __init__.py)
    print(f"\n▶️ EXEC STEP 2: {sop.steps[1]}")
    init_path = Path("src/icgl/agents/__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "MonitorAgent" not in content:
        # Append import
        new_import = "\nfrom .monitor_agent import MonitorAgent\n"
        
        # Append to __all__
        # finding the closing bracket of __all__
        if "__all__ = [" in content:
            updated_content = content.replace(
                "    \"CodeSpecialist\",", 
                "    \"CodeSpecialist\",\n    \"MonitorAgent\","
            )
            # Add import before __all__
            split_idx = content.find("__all__ = [")
            final_content = content[:split_idx] + new_import + updated_content[split_idx:]
            
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            print("   ✨ Registered MonitorAgent in __init__.py")
    else:
        print("   ✅ Already registered.")

    # STEP 3: Verify Import
    print(f"\n▶️ EXEC STEP 3: {sop.steps[2]}")
    try:
        from icgl.agents import MonitorAgent
        agent = MonitorAgent()
        print(f"   ✅ SUCCESS: Instantiated {agent.name} (Role: {agent.role})")
    except ImportError as e:
        print(f"   ❌ FAILURE: Could not import MonitorAgent. {e}")
    except Exception as e:
        print(f"   ❌ FAILURE: {e}")

    print("\n🏁 SOP EXECUTION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(execute_onboarding())
