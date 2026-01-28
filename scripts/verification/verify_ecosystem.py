import os
import sys

# Add shared to path
sys.path.append(os.getcwd())

print("--- EXPORT VERIFICATION ---")
try:
    from shared.python.llm.prompts import ARCHITECT_SYSTEM_PROMPT

    print(f"✅ ARCHITECT_SYSTEM_PROMPT found (length: {len(ARCHITECT_SYSTEM_PROMPT)})")
except ImportError as e:
    print(f"❌ ARCHITECT_SYSTEM_PROMPT FAILED: {e}")
except AttributeError as e:
    print(f"❌ ARCHITECT_SYSTEM_PROMPT FAILED: {e}")

try:
    import dataclasses

    from shared.python.agents.base import AgentResult

    fields = [f.name for f in dataclasses.fields(AgentResult)]
    if "risk_pre_mortem" in fields:
        print("✅ AgentResult.risk_pre_mortem found")
    else:
        print("❌ AgentResult.risk_pre_mortem MISSING")
    if "intent" in fields:
        print("✅ AgentResult.intent found")
    else:
        print("❌ AgentResult.intent MISSING")
except Exception as e:
    print(f"❌ AgentResult check failed: {e}")

try:
    from shared.python.agents.registry import AgentRegistry

    registry = AgentRegistry()
    if hasattr(registry, "run_and_synthesize"):
        print("✅ AgentRegistry.run_and_synthesize found")
    else:
        print("❌ AgentRegistry.run_and_synthesize MISSING")
except Exception as e:
    print(f"❌ AgentRegistry check failed: {e}")
