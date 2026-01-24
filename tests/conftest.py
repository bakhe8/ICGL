import os
import warnings

import pytest

from backend.core.runtime_guard import RuntimeIntegrityGuard


@pytest.fixture(autouse=True, scope="session")
def rig_repair_before_tests():
    os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY") or "test-key")
    guard = RuntimeIntegrityGuard()
    guard.repair()
    guard.check()
    guard.release()
    yield


@pytest.fixture(autouse=True)
def stub_llm(monkeypatch):
    """
    Keep runtime strict in production, but stub LLM calls in tests to avoid
    external dependencies. This does not re-enable any mock fallback in the
    codebase; it only patches methods during test execution.
    """
    from icgl import llm
    from icgl.core.llm import LLMProvider, LLMResponse

    class _StubProvider(LLMProvider):
        async def generate(self, request):
            return LLMResponse(content="stubbed", provider="stub")

    def _fake_init(self, api_key=None):
        self.api_key = api_key or "test-key"
        self.client = object()
        self.mock_mode = False

    async def _fake_generate_json(
        self, system_prompt: str, user_prompt: str, config=None
    ):
        return {
            "analysis": "stubbed analysis",
            "risks": ["stub risk"],
            "recommendations": ["stub recommendation"],
            "confidence_score": 0.9,
            "file_changes": [],
        }

    async def _fake_embedding(self, text: str, model: str = "text-embedding-3-small"):
        return [0.0] * 1536

    monkeypatch.setenv("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY") or "test-key")
    monkeypatch.setattr(
        "icgl.agents.registry.AgentRegistry._init_llm_provider",
        lambda self: _StubProvider(),
        raising=False,
    )
    monkeypatch.setattr(llm.client.LLMClient, "__init__", _fake_init, raising=False)
    monkeypatch.setattr(
        llm.client.LLMClient, "generate_json", _fake_generate_json, raising=False
    )
    monkeypatch.setattr(
        llm.client.LLMClient, "get_embedding", _fake_embedding, raising=False
    )

    # Silence third-party deprecations that are noise on Python 3.14+
    warnings.filterwarnings(
        "ignore",
        message=".*asyncio.iscoroutinefunction.*",
        category=DeprecationWarning,
        module="starlette.*",
    )
    warnings.filterwarnings(
        "ignore",
        message=".*import python_multipart.*",
        category=PendingDeprecationWarning,
        module="starlette.*",
    )
