import dataclasses
import os
import sys

# Add shared to path
sys.path.append(os.getcwd())

print("--- DEEP SCHEMA VERIFICATION ---")

try:
    from shared.python.agents.base import AgentResult, AgentRole

    res = AgentResult(agent_id="test", role=AgentRole.ARCHITECT, analysis="test", risk_pre_mortem=["test_risk"])
    print("✅ AgentResult instantiation with risk_pre_mortem SUCCESS")

    fields = [f.name for f in dataclasses.fields(AgentResult)]
    print(f"✅ AgentResult fields: {', '.join(fields[:10])} ...")
except Exception as e:
    print(f"❌ AgentResult test FAILED: {e}")

try:
    from shared.python.governance.signing_queue import signing_queue

    if hasattr(signing_queue, "add_to_queue"):
        print("✅ signing_queue.add_to_queue found")
    else:
        print("❌ signing_queue.add_to_queue MISSING")
except Exception as e:
    print(f"❌ SigningQueue test FAILED: {e}")

try:
    from shared.python.ops.transaction import tx_manager

    if hasattr(tx_manager, "stage_file"):
        print("✅ tx_manager.stage_file found")
    else:
        print("❌ tx_manager.stage_file MISSING")
except Exception as e:
    print(f"❌ TransactionManager test FAILED: {e}")

try:
    from shared.python.agents.registry import AgentRegistry

    reg = AgentRegistry()
    if hasattr(reg, "run_and_synthesize"):
        print("✅ AgentRegistry.run_and_synthesize found")
    else:
        print("❌ AgentRegistry.run_and_synthesize MISSING")
except Exception as e:
    print(f"❌ AgentRegistry test FAILED: {e}")
