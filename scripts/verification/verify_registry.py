import asyncio

from shared.python.agents.base import AgentRole, MockAgent
from shared.python.agents.registry import AgentRegistry


async def main():
    print("Initializing Unit Test for AgentRegistry...")

    # 1. Instantiate Registry with Bypass
    class TestRegistry(AgentRegistry):
        def _init_llm_provider(self):
            return None  # Mock provider

    registry = TestRegistry()

    # 2. Register Mock Agents
    agent_arch = MockAgent(agent_id="agent-architect", role=AgentRole.ARCHITECT)
    agent_sent = MockAgent(agent_id="agent-sentinel", role=AgentRole.SENTINEL)

    # Manually populate registry
    registry._agents[AgentRole.ARCHITECT] = agent_arch
    registry._agents[AgentRole.SENTINEL] = agent_sent

    print("\n--- Testing get_agent with various keys ---")

    test_cases = [
        (AgentRole.ARCHITECT, True, "Enum Key"),
        ("agent-architect", True, "String Agent ID"),
        ("architect", True, "String Role Value"),
        (AgentRole.SENTINEL, True, "Enum Key (Sentinel)"),
        ("agent-sentinel", True, "String Agent ID (Sentinel)"),
        ("unknown", False, "Unknown ID"),
    ]

    for key, expected, desc in test_cases:
        result = registry.get_agent(key)
        found = result is not None
        icon = "✅" if found == expected else "❌"
        print(f"{icon} [{desc}] Key: '{key}' -> Found: {found}")


if __name__ == "__main__":
    asyncio.run(main())
