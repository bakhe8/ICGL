# Agents Core

Shim package that currently re-exports `modules.agents` while the agent domain
is extracted into a standalone library.

Intended contents after extraction:
- Shared agent utilities, base types, prompts.
- Agent registry helpers and dependency injection surface.

Using the shim now keeps imports stable (`import agents_core as agents`) while we
slice out the real implementation.
