# System Architecture of ICGL

The ICGL system is designed with a modular architecture that integrates various components to facilitate a governance-first approach to decision-making.

## System Components

- **CLI (`cli.py`)**: Provides a command-line interface for interacting with the ICGL system.
- **Policy Engine**: Enforces hard constraints before any voting or synthesis occurs.
- **Knowledge Base (KB)**: Acts as the source of truth, storing concepts, policies, and decision outcomes.
- **Human-in-the-Loop (HDAL)**: Incorporates human judgment into the decision-making process.

## Component Interactions

Components interact through a well-defined API, ensuring seamless communication and data flow between modules.

## Data Flow

Data flows from the CLI to the Policy Engine, then to the Knowledge Base, and finally through the Human-in-the-Loop mechanism, where decisions are made.

## Design Patterns

The ICGL system utilizes design patterns such as Singleton for the Policy Engine and Observer for event handling, ensuring efficient and scalable architecture.