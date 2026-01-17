# ICGL System Overview

The Iterative Co-Governance Loop (ICGL) system is a governance-first intelligence platform designed to facilitate long-lived decisions through a collaborative, multi-agent approach. It integrates various components, including policy engines, knowledge bases, and human-in-the-loop mechanisms, to ensure that decisions are made transparently, efficiently, and with accountability.

## Key Features

- **Governance-First Approach**: Ensures that all decisions are made with governance at the forefront.
- **Multi-Agent Collaboration**: Facilitates the interaction between multiple agents to achieve a common goal.
- **Human-in-the-Loop**: Incorporates human judgment into the decision-making process, ensuring that decisions are ethical and considerate.
- **Knowledge Base Integration**: Utilizes a comprehensive knowledge base to inform decisions and store outcomes.

## Quick Installation

```bash
pip install icgl
```

## Basic Usage Example

```python
from icgl import orchestrator

# Initialize the orchestrator
orch = orchestrator.Orchestrator()

# Execute a decision loop
result = orch.execute_decision_loop()
print(result)
```

This example demonstrates how to initialize the ICGL orchestrator and execute a basic decision loop.