import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

# Dummy env load
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-test"

try:
    from src.api.deps import get_icgl

    print("--- Booting ICGL ---")
    icgl = get_icgl()
    print(f"ICGL initialized: {icgl}")

    if icgl:
        print(f"Registry: {icgl.registry}")
        agents = icgl.registry.list_agents()
        print(f"Agents Found: {len(agents)}")
        for role in agents:
            agent = icgl.registry.get_agent(role)
            print(f"- {role}: {agent.agent_id} ({type(agent).__name__})")

        # Test serialization simulation
        serialized = []
        for role in agents:
            agent = icgl.registry.get_agent(role)
            serialized.append(
                {
                    "id": getattr(agent, "agent_id", str(role)),
                    "role": str(role),
                    "name": getattr(agent, "name", str(role)),
                }
            )
        print(f"Serialized Sample: {serialized[0] if serialized else 'None'}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
