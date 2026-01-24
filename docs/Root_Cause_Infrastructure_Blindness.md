# Root Cause Analysis: The "Infrastructure Blind Spot"

## 🏗️ 1. Why was it missed? (The Diagnosis)

### A. The "Code-First" Bias (Abstraction Bias)

Current Agents (Architect, Builder, Refactor) are trained and prompted to view "Source Code" as the ultimate truth. To them, a database is just an `import sqlite3` line or a connection string. They treat data persistence as an **Implementation Detail**, not a **Sovereign Domain**. They don't "feel" the weight of data integrity or schema complexity until it breaks.

### B. Functional Fixedness (Role Rigidity)

- **Architect**: Looks for *Logical* patterns (Modules, Classes).
- **Sentinel**: Looks for *Security/Safety* patterns (Injection, Permission).
- **DevOps**: Looks for *Deployment* patterns (Docker, CI/CD).
**Result**: Everyone assumed "Data" was someone else's job. This is the classic "Tragedy of the Commons" in software engineering, replicated in AI agents.

### C. The "Silent Debt" Paradox

Bad database design (lack of FKs, poor indexing, JSON dumping) is **silent** in the early stages. It doesn't throw syntax errors. It only reveals itself as "Technical Debt" later. Agents are reactive to *Errors*, not proactive about *Future Pain* unless explicitly told to be.

## 🛡️ 2. How do we prevent this? (The Fix)

### A. Explicit Representation (The New Agent)

By forcing a `DatabaseArchitect` into the council, we give "Data" a voice. This agent won't care about clean Python code; it will care about *Clean Schemas*. It creates "tension" in the council, which is healthy.

### B. "Infrastructure Sovereignty" in the Manifesto

We must update `SED-01` to declare that **"Data Schema is as important as Code Logic."**

### C. Capability Audits (Metacognition)

We need a periodic step where the `Architect` doesn't look at the project, but looks at the **Team** (the Agents).
*Query: "Do we have the skills required to maintain this growing complexity?"*

---

# Action Plan: Creating the Database Architect

1. **Create Agent**: `backend/agents/database_architect.py`
2. **Define Role**: Guardian of `integrity`, `schemas`, and `migrations`.
3. **Integrate**: Add to `ICGL` council and `AgentRegistry`.
