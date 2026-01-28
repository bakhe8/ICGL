import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.core.agents.core.base import AgentRole, MockAgent, Problem


@pytest.mark.asyncio
async def test_agent_shield_llm_failure():
    """
    Verify that Agent.analyze (The Shield) correctly catches LLM failures
    and returns a valid fallback result instead of crashing.
    """
    # 1. Create agent with failing LLM
    agent = MockAgent(agent_id="failing-agent", role=AgentRole.ARCHITECT)

    # 2. Mock _analyze to raise a TimeoutError (simulating LLM failure)
    with patch.object(agent, "_analyze", side_effect=asyncio.TimeoutError("LLM Request Timed Out")):
        problem = Problem(title="Test Fail", context="None")
        kb = MagicMock()

        # 3. Execute (should be caught by the shield in Agent.analyze)
        result = await agent.analyze(problem, kb)

        # 4. Verify
        assert result.confidence == 0.0
        assert "LLM Request Timed Out" in result.analysis
        assert any("Check Logs" in r for r in result.recommendations)
        print("✅ Agent Shield successfully caught LLM failure.")


@pytest.mark.asyncio
async def test_icgl_kb_corrupt_recovery(tmp_path):
    """
    Test how the engine handles a missing or corrupt DB file.
    """
    from src.core.governance.icgl import ICGL

    # Path to non-existent dir (to trigger error)
    bad_path = "/non/existent/path/kb.db"

    # The initialization should either handle gracefully or raise a clear error
    # Our current ICGL might raise RuntimeError if KB fails
    with pytest.raises(Exception):
        ICGL(db_path=bad_path, enforce_runtime_guard=False)

    print("✅ System correctly identified invalid database path.")
