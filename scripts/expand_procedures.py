import asyncio
import sys
from pathlib import Path

# Add src
sys.path.append(str(Path.cwd() / "src"))

from icgl.governance.procedure_engine import ProcedureEngine
from icgl.kb import PersistentKnowledgeBase

async def expand_operations():
    print("🚀 EXPANDING OPERATIONS")
    print("=======================")
    
    # 1. Initialize Engine
    # Note: We need to make sure PersistentKnowledgeBase loads/saves procedures
    # Only in-memory KB was patched in previous steps. 
    # To truly persist, we'd need to update StorageBackend and PersistentKnowledgeBase load/save logic.
    # For this demo, we will use the in-memory aspect to show "Runtime Awareness".
    
    # Let's monkey-patch PersistentKB for this run if needed (or assume it inherits form base KB)
    # The base KnowledgeBase has the methods, so persistent should inherit them. 
    # But storage needs to know how to save them to sqlite or json. 
    # Currently it won't save to disk, but it will live in the 'Engine' memory if singleton.
    
    engine = ProcedureEngine()
    
    # 2. Create the first official SOP
    print("\n📝 Authoring SOP-OPS-01: Agent Onboarding...")
    sop = engine.create_sop(
        title="New Agent Onboarding Protocol",
        code="SOP-OPS-01",
        type="SOP",
        steps=[
            "1. Define Agent Role and Responsibilities in `src/icgl/agents`.",
            "2. Inherit from `BaseAgent` class.",
            "3. Register Agent in `AgentRegistry`.",
            "4. Create Unit Tests in `tests/agents`.",
            "5. Update `KB` with new Agent Capabilities."
        ],
        tools=["CodeSpecialist", "ArchitectAgent"]
    )
    
    if sop:
        print(f"✅ SOP Registered: {sop.code}")
        print("   Steps:")
        for step in sop.steps:
            print(f"   - {step}")
            
    # 3. Verify Retrieval
    print("\n🔍 Verifying Registry...")
    retrieved = engine.get_procedure("SOP-OPS-01")
    if retrieved:
        print(f"   ✅ Confirmed: System is aware of {retrieved.title}")
    else:
        print("   ❌ Verification Failed.")

if __name__ == "__main__":
    asyncio.run(expand_operations())
