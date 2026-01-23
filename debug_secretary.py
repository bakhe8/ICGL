import asyncio

from api.server import get_icgl
from backend.agents.base import AgentRole


async def debug_secretary():
    print("--- Debugging Secretary ---")
    try:
        icgl = get_icgl()
        print(f"ICGL Initialized: {icgl}")

        # Check Registry
        secretary = icgl.registry.get_agent(AgentRole.SECRETARY)
        if not secretary:
            secretary = icgl.registry.get_agent("secretary")

        print(f"Secretary Agent: {secretary}")

        if secretary:
            print(f"Has _log_relay_event: {hasattr(secretary, '_log_relay_event')}")
            print(f"Current Log Length: {len(getattr(secretary, 'relay_log', []))}")

            # Force log
            secretary._log_relay_event(
                event_type="DEBUG_TEST",
                summary="Forced Debug Log",
                technical_details="Manual injection via script",
                stakeholders=["Debugger"],
                priority="high",
            )
            print("Forced log entry.")
            print(f"New Log Length: {len(getattr(secretary, 'relay_log', []))}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_secretary())
