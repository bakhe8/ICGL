flowchart TB

%% =========================
%% UI LAYER
%% =========================
UI["Sovereign UI<br/>Council Hub · Pulse · Alerts"]

%% =========================
%% API & ROUTING
%% =========================
API["API Router<br/>server.py<br/>/api/*"]

%% =========================
%% CONTEXT + NEXUS
%% =========================
CTX["Context Assembler<br/>ai_context/<br/>Memory · ADRs · Logs"]
NEXUS["Nexus Gateway<br/>Central Catalyst<br/>AI ↔ Agent Bridge"]

%% =========================
%% CORE GOVERNANCE
%% =========================
ORCH["Governance Orchestrator<br/>ICGL"]
EVAL["Sovereign Evaluator Gate<br/>Purpose · KPIs · Risk"]
SIGN["Decision Signer & Policy Gate"]

%% =========================
%% AGENT MESH
%% =========================
ARCH["Architect"]
GUARD["Guardian Sentinel"]
STEWARD["Knowledge Steward"]
UIUX["UI/UX Agent"]

BUILDER["Builder"]
DEVOPS["DevOps"]
TESTING["Testing"]
REFACTOR["Refactoring"]

%% =========================
%% EXECUTION & VERIFICATION
%% =========================
EXEC["Execution Layer<br/>Builder · Refactor · DevOps"]
VERIFY["Verification Layer<br/>Testing · File Impact"]

%% =========================
%% MEMORY & OBSERVABILITY
%% =========================
MEM["Institutional Memory Kernel<br/>ADRs · Invariants · Lessons"]
OBS["Observability & Metrics<br/>CPU · Latency · Errors"]

%% =========================
%% FLOWS
%% =========================
UI --> API
API --> CTX
API --> NEXUS

CTX --> ORCH
NEXUS --> ORCH

ORCH --> ARCH
ORCH --> GUARD
ORCH --> STEWARD
ORCH --> UIUX

ARCH --> BUILDER
GUARD --> DEVOPS
STEWARD --> ORCH
UIUX --> ORCH

BUILDER --> EXEC
DEVOPS --> EXEC
REFACTOR --> EXEC

EXEC --> VERIFY
VERIFY --> EVAL
EVAL --> SIGN
SIGN --> MEM

MEM --> CTX
MEM --> OBS
OBS --> EVAL

%% =========================
%% PEER CONSULTATION
%% =========================
ARCH -. consult .-> GUARD
GUARD -. consult .-> STEWARD
STEWARD -. consult .-> ARCH
UIUX -. consult .-> BUILDER
REFACTOR -. consult .-> TESTING
TESTING -. consult .-> REFACTOR
