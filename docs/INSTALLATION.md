# ICGL Installation & Runtime Setup

## Prerequisites

- Python 3.10+ (matches `pyproject.toml`)
- pip (or Poetry)
- OpenAI account/key for real LLM use (`OPENAI_API_KEY`)

## Install (dev mode)

```bash
pip install -e .
```

## Environment (.env)

Create `.env` in the project root:

```
OPENAI_API_KEY=your-api-key-here
```

Runtime guard will abort if this key is missing.

## Runtime Integrity

1) Repair and preflight checks (locks, Qdrant, Merkle):

```bash
icgl runtime repair
```

1) Start API (governed, no mock fallback):

```bash
python -m icgl.api.server
```

## Conversational UI (no CLI needed)

1) With the server running, open `src/icgl/ui/chat.html` in your browser.
2) Chat naturally (analyze decisions, run experiments, approve/reject).  
   - Live updates stream via `/ws/chat`.
   - All actions stay under ICGL governance; no silent execution.

## Troubleshooting

- **Missing OPENAI_API_KEY**: RIG aborts early. Set the key in `.env`.
- **Qdrant lock in use**: Stop other Python/Qdrant processes, then `icgl runtime repair`.
- **Merkle reset**: `icgl runtime repair` will back up and re-init the Merkle chain if needed.
