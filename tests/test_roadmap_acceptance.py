import json
import asyncio
import pytest

from icgl.sentinel.sentinel import Sentinel
from icgl.kb.schemas import ADR
from icgl.memory.interface import Document, SearchResult
from icgl.core.observability import SystemObserver
from icgl.utils.repo_map import build_repo_map
from icgl.api.server import is_auto_write_enabled
from icgl.agents.engineer import EngineerAgent
from icgl.agents.base import Agent, AgentRole, AgentResult
from icgl.core.llm import LLMResponse


class _FakeVectorStore:
    async def initialize(self):
        return None

    async def add_document(self, doc):
        return None

    async def save(self):
        return None

    async def search(self, query: str, limit: int = 5):
        # Return a highly similar ADR to trigger S-11 drift warning
        return [
            SearchResult(
                document=Document(
                    id="ADR-OLD",
                    content="ACCEPTED ADR about similar topic",
                    metadata={"title": "Legacy ADR"},
                ),
                score=0.9,
            )
        ]


def test_cycle3_sentinel_drift_and_observability(tmp_path):
    async def _run():
        sentinel = Sentinel(vector_store=_FakeVectorStore())
        adr = ADR(
            id="ADR-TEST",
            title="New ADR",
            status="DRAFT",
            context="Testing drift detection",
            decision="Test decision",
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )

        alerts = await sentinel.scan_adr_detailed_async(adr, kb=None)
        assert any(getattr(a, "rule_id", "") == "S-11" for a in alerts)

    asyncio.run(_run())

    # Observability: intervention + metric are persisted
    obs_dir = tmp_path / "logs"
    observer = SystemObserver(log_dir=obs_dir)
    observer.record_intervention(adr_id="ADR-X", original_rec="APPROVE", action="REJECT", reason="safety")
    observer.record_metric(agent_id="agent-x", role="architect", latency=12.3, confidence=0.8, success=False)

    intervention_file = obs_dir / "interventions.jsonl"
    metrics_file = obs_dir / "agent_metrics.jsonl"
    assert intervention_file.exists() and metrics_file.exists()
    assert intervention_file.read_text().strip() != ""
    assert metrics_file.read_text().strip() != ""


class _FakeMemory:
    async def search(self, query: str, limit: int = 5):
        return [
            SearchResult(
                document=Document(
                    id="lesson-1",
                    content="Human rejected auto-deploy without approval",
                    metadata={"type": "lesson"},
                ),
                score=0.95,
            ),
            SearchResult(
                document=Document(
                    id="policy-1",
                    content="Policy text",
                    metadata={"type": "policy"},
                ),
                score=0.7,
            ),
        ]


class _StubLLM:
    def __init__(self, capture):
        self.capture = capture

    async def generate(self, request):
        self.capture["system_prompt"] = request.system_prompt
        return LLMResponse(content="ok", provider="stub")


class _DummyAgent(Agent):
    def __init__(self, llm_provider, memory):
        super().__init__(agent_id="dummy", role=AgentRole.ARCHITECT, llm_provider=llm_provider)
        self.memory = memory

    async def _analyze(self, problem, kb):
        return AgentResult(agent_id=self.agent_id, role=self.role, analysis="noop", confidence=1.0)


def test_cycle6_active_learning_from_interventions():
    capture = {}
    agent = _DummyAgent(llm_provider=_StubLLM(capture), memory=_FakeMemory())

    async def _run():
        await agent._ask_llm("Test prompt needing lessons")

    asyncio.run(_run())
    assert "CRITICAL MEMORY" in capture.get("system_prompt", "")


def test_cycle7_9_guardrails(tmp_path, monkeypatch):
    # Path traversal blocked
    eng = EngineerAgent(repo_path=tmp_path)
    result = eng.write_file("../evil.txt", "data")
    assert "Security Violation" in result

    # Auto-write gating via env toggle helper
    monkeypatch.delenv("ICGL_ENABLE_AUTO_WRITE", raising=False)
    assert is_auto_write_enabled() is False
    monkeypatch.setenv("ICGL_ENABLE_AUTO_WRITE", "true")
    assert is_auto_write_enabled() is True


def test_cycle8_repo_map_builder(tmp_path):
    repo_root = tmp_path / "repo"
    (repo_root / "subdir").mkdir(parents=True)
    (repo_root / "subdir" / "a.py").write_text("print('a')", encoding="utf-8")
    (repo_root / "README.md").write_text("# sample", encoding="utf-8")

    repo_map = build_repo_map(repo_root)
    assert repo_map["stats"]["total_files"] >= 2
    assert repo_map["stats"]["total_dirs"] >= 1
    assert any(n["type"] == "file" for n in repo_map["nodes"])
    assert any(e["from"] == "." or e["from"] == "subdir" for e in repo_map["edges"])
