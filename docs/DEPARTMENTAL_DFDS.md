# 📊 Departmental Data Flow Diagrams (DFD) Submission

**To:** Office of the CEO  
**From:** System Architect  
**Date:** 2026-01-17  
**Status:** CANONICAL ARCHITECTURE - CYCLE 2026.2 (IDCP Active)  

Per your directive and strategic feedback, these data flows have been formally established. They incorporate explicit Rejection Traceability, Authority Constraints for persistence, and governed write-access for the file system.

---

## 1. Governance Department (HDAL & Orchestrator)

**Responsibility:** Decision making, Policy enforcement, and Cycle management.

```mermaid
graph TD
    User([User / CEO]) -->|Proposal / Intent| API[API Gateway]
    API -->|ADR Draft| Orch[ICGL Orchestrator]
    
    subgraph Governance Core
        Orch -->|Check Compliance| Enforcer[Policy Enforcer]
        Enforcer --x|Violation| Reject[Reject Proposal]
        
        Enforcer -->|Valid| Sentinel[Sentinel Scanner]
        Sentinel -->|Risk Analysis| Agents[Agent Swarm]
        Agents -->|Synthesis & Recommendation| HDAL[HDAL Authority]
    end
    
    HDAL -->|Request Signature| User
    User -->|Decision| HDAL
    
    HDAL -->|Finalized ADR| KB[(Knowledge Base)]
    Reject -->|Log Reason & Feedback| KB
    Reject -->|Notify Failure| User
    
    style Reject fill:#422,stroke:#f66,color:#fff
```

---

## 2. Knowledge Base Department (Archives)

**Responsibility:** Storing Truth, Policies, Memories, and Procedures.

```mermaid
graph LR
    Input[Incoming Entity] -->|Validate Schema| Validator{Schema Validator}
    
    Validator --x|Invalid| Error[Return Error]
    Validator -->|Valid| Persist[Persistence Layer]
    
    subgraph Storage
        Persist -->|SQL| SQLite[(SQLite DB)]
        Persist -->|Vectors| Qdrant[(Vector Memory)]
    end
    
    subgraph Access
        Query[Search/Get] --> Cache[Memory Cache]
        Cache -.->|Miss| SQLite
        Cache -.->|Semantic| Qdrant
    end
    
    SQLite --> Output[Data Object]
    Qdrant --> Output

    %% Authority Note
    subgraph Authority_Constraint [ ]
        direction LR
        Note1[<b>AUTHORITY:</b> Only Governance Core<br/>can Persist Canonical Records]
    end
    Authority_Constraint --- Persist
    style Authority_Constraint fill:#221,stroke:#660,stroke-dasharray: 5 5
```

---

## 3. Operations Department (Agents & Coordination)

**Responsibility:** Execution, self-sufficiency via protocol, and inter-department requests.

```mermaid
graph TD
    subgraph Agent_Layer
        A1[Agent A]
        A2[Agent B]
    end

    A1 -->|1. Need Detected| Orch[Coordination Orchestrator]
    Orch -->|2. Formal Request| Dept{Target Department}
    
    subgraph Departments
        Dept -->|Ops| SOP_Lib[(SOP Library)]
        Dept -->|Eng| Build[Engineering/Builder]
        Dept -->|KB| Archives[(Archives)]
    end
    
    Dept -->|3. Fulfillment| Orch
    Orch -->|4. Governance Elevation| Gov[HDAL / Governance]
    Gov -->|5. Approval| Orch
    Orch -->|6. Controlled Execution| A1

    %% Blocks
    A1 -.-x|DIRECT ACCESS BLOCKED| Dept
    A1 -.-x|DIRECT ACCESS BLOCKED| Gov
```

**IDCP Constraints:**

- **Zero-Bypass:** Every agent need MUST flow through the Orchestrator.
- **Traceability:** Every request is logged in the KB before execution.
- **Authority:** No department fulfills until Governance signs the result mapping.

---

## 4. Security & Compliance Department (Sentinel)

**Responsibility:** Drift detection, Integrity checks, and Real-time monitoring.

```mermaid
graph TD
    Stream[System Events] --> Monitor{Sentinel Monitor}
    
    subgraph Analysis
        Monitor -->|Check Invariants| Integrity[Integrity Guard]
        Monitor -->|Check Policy| Policy[Policy Engine]
        Monitor -->|Check Drift| Drift[Drift Detector]
    end
    
    Integrity --x|Corruption| Lockdown[System Lockdown]
    Policy --x|Violation| Block[Block Action]
    Drift -->|Warning| Dashboard[CEO Dashboard]
    
    Block -->|Log| Audit[(Audit Log)]
```

---

## 5. Interface Department (Cockpit & API)

**Responsibility:** User interaction, Visualization, and Command intake.

```mermaid
graph LR
    CEO([CEO / User]) -->|HTTP/WS| Fast[FastAPI Server]
    
    subgraph Interface Layer
        Fast -->|State Push| WS[WebSocket Manager]
        Fast -->|Command| Router[Request Router]
    end
    
    WS -->|Realtime Data| UI[Sovereign Cockpit]
    Router -->|Invoke| Engine[ICGL Engine]
    Engine -->|Status Update| WS
```

---

**Action Required:**
Please review these flows. If approved, they will become the "Canonical Architecture" for the next cycle.
