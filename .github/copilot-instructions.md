# Copilot / AI Agent Instructions for ICGL

This file tells AI coding agents how this repository is structured and which conventions to follow.

Summary
- Multi-agent backend lives in `agents/` (core: `agents/base.py`, `agents/registry.py`).
- FastAPI API surfaces are under `api/` and the backend app runs via `python -m api.main` or `uvicorn api.server:app --reload` (port 5173 in dev tasks).
- Frontend lives under `frontend/` / `web-app`; usual `npm` dev flow is available in workspace tasks.
- Config lives in `config.yaml` (LLM defaults, vector store path, token budgets).

Key patterns and conventions
- Agent model: read `agents/base.py` first. Important classes: `Agent`, `AgentRole`, `Problem`, `IntentContract`, `AgentResult`, `FileChange`.
- Job contracts: agents must obey `allowed_scopes` and use `verify_contract(file_path)` before changing files.
- LLM usage: prefer agent helper `_ask_llm()` which enforces system prompts, lesson recall, and token-budget tracking.
- Memory APIs: `recall()` and `recall_lessons()` are the supported helpers for agent memory access.
- Generation vetting: BuilderAgent (see `agents/agents/AGENTS.md`) implements `_learn_patterns()` and `_verify_output()` — generated code should match repository style and pass AST-based checks when possible.

Build / test / debug commands
- Run backend dev server (task): `uvicorn api.server:app --host 127.0.0.1 --port 5173 --reload`.
- Start the API via the provided task: `python -m api.main` (workspace task `Run API`).
- Run tests: `pytest -q` (tests configured in `pyproject.toml` and `pytest.ini`; test paths include `tests`, `backend/tests`).
- Python toolchain: project uses Poetry in `pyproject.toml` (python ^3.14). Lint rules: Ruff line-length 120.

What to check before editing files
- Confirm `Agent.verify_contract()` allows touching the target path.
- Review `agents/agents/AGENTS.md` for existing agent responsibilities to avoid duplicates.
- Ensure generated Python targets match `pyproject.toml` conventions (py312 target in Ruff) and pass basic AST syntax checks.

Integration points & important files to inspect
- `agents/base.py` — core agent lifecycle, LLM helpers, memory helpers, and result model.
- `agents/registry.py` — agent lifecycle and channel routing.
- `agents/agents/AGENTS.md` — canonical registry of agents and recent enhancements (BuilderAgent behavior).
- `config.yaml` — LLM defaults (model, temperature), vector store path, auto-apply flags.
- `pyproject.toml` / `package.json` — dependency and lint/test conventions.

Project-specific guidance for AI agents
- Prefer enhancing existing agents over creating new ones. Check `AGENTS.md` gap list before proposing new agents.
- When proposing code changes, populate `AgentResult.file_changes` and include an `IntentContract` with `allowed_files`, `forbidden_zones`, and `success_criteria`.
- Use the Agent `analyze()` wrapper pattern for observability — return structured `AgentResult` (confidence, recommendations, concerns).
- If making runtime changes (APIs, routes), run local server task and unit tests; include short mental checklist in commit message.

Examples (short)
- Verify permission before change:

  from agents.base import Agent

  if not agent.verify_contract("agents/new_agent.py"):
      raise PermissionError("Agent not allowed to modify this path")

- Return a minimal AgentResult:

  return AgentResult(agent_id="builder.v1", role=AgentRole.BUILDER, analysis="Generated patch", file_changes=[FileChange(path="foo.py", content=content)])

If something is unclear
- Ask: which agent owns this capability? Refer to `agents/agents/AGENTS.md`.
- Ask: is this change safe to auto-apply? Check `config.yaml: auto_apply` and the `IntentContract` `risk_level`.

Contact / next steps
- After making changes, run `pytest -q` and the local API task. Provide a short changelog entry and update `agents/agents/AGENTS.md` if you modify agent responsibilities.

---
Please review — tell me if any agent workflows or external integrations are missing. I can iterate.
