# ICGL Agent Registry

**Last Updated:** 2026-01-22  
**Total Active Agents:** 14

This document serves as the **Agent Capability Registry** - the single source of truth for all agents in the ICGL system, their capabilities, and responsibilities.

---

## Purpose

This registry prevents:

- ❌ Creating duplicate agents
- ❌ Feature overlap between agents
- ❌ Confusion about agent responsibilities

And enables:

- ✅ Clear visibility of system capabilities
- ✅ Identification of gaps
- ✅ Disciplined agent ecosystem expansion

---

## Active Agents

### Core Analysis Agents

| Agent | File | Primary Responsibility | Key Capabilities | Status |
|-------|------|----------------------|------------------|--------|
| **ArchitectAgent** | `architect.py` | Structural & Design Analysis | - Coupling/cohesion analysis<br>- System boundary analysis<br>- Strategic optionality checks<br>- Repository map integration<br>- Institutional memory recall | ✅ Active |
| **PolicyAgent** | `policy.py` | Policy Compliance | - Rule of law enforcement<br>- Policy violation detection<br>- Compliance checking<br>- Policy recall from KB | ✅ Active |
| **FailureAgent** | `failure.py` | Failure Mode Detection | - Failure scenario analysis<br>- Risk identification<br>- Edge case detection | ✅ Active |
| **SentinelAgent** | `sentinel_agent.py` | Real-time Risk Detection | - System drift monitoring<br>- Risk signal detection<br>- Real-time analysis | ✅ Active |
| **GuardianAgent** | `guardian.py` | Concept Integrity | - Core concept protection<br>- Principle enforcement<br>- Integrity validation | ✅ Active |

### Construction & Deployment Agents

| Agent | File | Primary Responsibility | Key Capabilities | Status |
|-------|------|----------------------|------------------|--------|
| **BuilderAgent** | `builder.py` | Code Generation | - ✨ Code generation<br>- ✨ Pattern learning from codebase<br>- ✨ AST-based self-verification<br>- ✨ Retry logic on errors<br>- File creation/modification | ✅ Active<br>**Enhanced 2026-01-22** |
| **EngineerAgent** | `engineer.py` | Code Deployment | - GitOps execution<br>- Automated code writing<br>- File system operations<br>- Change application | ✅ Active |

### Coordination & Documentation Agents

| Agent | File | Primary Responsibility | Key Capabilities | Status |
|-------|------|----------------------|------------------|--------|
| **MediatorAgent** | `mediator.py` | Agent Coordination | - Multi-agent coordination<br>- Conflict resolution<br>- Consensus building | ✅ Active |
| **DocumentationAgent** | `documentation_agent.py` | Documentation Generation | - Documentation analysis<br>- Content generation<br>- Documentation quality assessment<br>- Rewrite planning<br>- Professional docs output | ✅ Active |

### Specialized Agents

| Agent | File | Primary Responsibility | Key Capabilities | Status |
|-------|------|----------------------|------------------|--------|
| **Specialists** | `specialists.py` | Domain-Specific Analysis | - Expert consultation<br>- Domain-specific evaluation<br>- Specialized knowledge | ✅ Active |

### Infrastructure

| Component | File | Primary Responsibility | Key Capabilities | Status |
|-----------|------|----------------------|------------------|--------|
| **AgentRegistry** | `registry.py` | Agent Management | - Agent lifecycle management<br>- Agent discovery<br>- Channel routing<br>- Coordination infrastructure | ✅ Core |
| **Agent Base** | `base.py` | Foundation Classes | - Abstract base class<br>- LLM integration<br>- Memory/recall system<br>- Observability<br>- Channel communication | ✅ Core |

---

## Recent Enhancements

### BuilderAgent Enhancement (2026-01-22)

**ADR:** `fc9cef1f-938c-423b-b41b-bfa6ec58b235`  
**Confidence:** 88.33%

**New Capabilities:**

1. `_learn_patterns()` - Learns coding conventions from existing files
2. `_verify_output()` - AST-based syntax verification
3. Retry logic - Auto-corrects errors with feedback
4. Metadata tracking - Reports verification status

**Impact:** BuilderAgent now generates higher-quality code that matches project conventions

---

## Capability Coverage Matrix

### Current Coverage

| Capability Domain | Coverage | Agent(s) | Status |
|-------------------|----------|----------|--------|
| **Code Analysis** | ✅ Excellent | Architect, Failure | Good coverage |
| **Code Generation** | ✅ Excellent | Builder (enhanced) | Enhanced 2026-01-22 |
| **Code Deployment** | ✅ Good | Engineer | Stable |
| **Risk Detection** | ✅ Excellent | Sentinel, Failure | Strong coverage |
| **Policy Enforcement** | ✅ Good | Policy, Guardian | Stable |
| **Documentation** | ✅ Good | Documentation | Comprehensive |
| **Agent Coordination** | ✅ Good | Mediator | Stable |
| **Testing** | 🔴 **CRITICAL GAP** | ❌ None | **Missing** |
| **Deep Verification** | 🟡 Partial | Builder (basic) | Needs expansion |
| **Learning/Memory** | 🟡 Partial | Base (recall methods) | Needs enhancement |
| **Refactoring** | 🔴 **GAP** | ❌ None | **Missing** |
| **Performance Analysis** | 🔴 **GAP** | ❌ None | **Missing** |

---

## Identified Gaps

### 🔴 Critical Priority

1. **TestingAgent** *(NEW - High Priority)*
   - **Missing Capability:** Automated test generation
   - **Rationale:** No existing agent generates tests
   - **Overlap Check:** ❌ None
   - **Recommendation:** CREATE_NEW
   - **Scope:**
     - Generate unit tests for functions/classes
     - Generate integration tests
     - Pytest format output
     - Coverage analysis

2. **VerificationAgent** *(NEW - High Priority)*
   - **Missing Capability:** Comprehensive code verification
   - **Rationale:** BuilderAgent has basic AST verification, but we need deeper analysis
   - **Overlap Check:** 🟡 Partial with BuilderAgent
   - **Recommendation:** CREATE_NEW (different scope)
   - **Scope:**
     - Static analysis beyond syntax
     - Type checking
     - Security vulnerability scanning
     - Code quality metrics
     - Integration testing coordination

### 🟡 Medium Priority

1. **RefactoringAgent** *(NEW - Medium Priority)*
   - **Missing Capability:** Code refactoring and optimization
   - **Rationale:** No agent specializes in code improvement
   - **Overlap Check:** ❌ None
   - **Recommendation:** CREATE_NEW
   - **Scope:**
     - Identify code smells
     - Suggest refactorings
     - Apply common patterns
     - Optimize performance

### ✅ Enhancement Opportunities (Use Existing)

1. **Advanced Learning** → **Enhance Base.Agent**
   - **Current:** Base agent has `recall()` and `recall_lessons()` methods
   - **Recommendation:** ✅ ENHANCE_EXISTING
   - **Rationale:** Learning is foundational - enhance base class
   - **Scope:**
     - Better pattern recognition
     - Long-term memory improvements
     - Cross-agent learning

2. **Performance Monitoring** → **Enhance SentinelAgent**
   - **Current:** Sentinel monitors drift and risks
   - **Recommendation:** ✅ ENHANCE_EXISTING
   - **Rationale:** Sentinel already monitors system health
   - **Scope:**
     - Add performance metrics
     - Resource usage tracking
     - Latency monitoring

---

## Agent Capabilities Detail

### ArchitectAgent

**Specialization:** System structure and design patterns

**Capabilities:**

- Analyzes coupling between components
- Evaluates cohesion within modules
- Checks system boundaries and isolation
- Enforces strategic optionality (P-CORE-01)
- Integrates repository map for context
- Recalls institutional memory (past ADRs, policies)

**LLM:** GPT-4 Turbo (temperature: 0.0, deterministic)

**Key Methods:**

- `_analyze()` - Main analysis logic
- `get_system_prompt()` - Generates repo map-enhanced prompts

---

### BuilderAgent **(Recently Enhanced)**

**Specialization:** Intelligent code generation with self-awareness

**Capabilities:**

- Generates code from decisions
- ✨ Learns patterns from existing codebase
- ✨ Self-verifies syntax before returning
- ✨ Retries on errors with feedback
- Creates/modifies files
- Reports verification metadata

**LLM:** GPT-4 Turbo (temperature: 0.0, JSON mode)

**Key Methods:**

- `_analyze()` - Main generation workflow
- `_learn_patterns()` - Extract coding conventions
- `_verify_output()` - AST-based validation

**Enhancement Date:** 2026-01-22  
**ADR:** fc9cef1f-938c-423b-b41b-bfa6ec58b235

---

### PolicyAgent

**Specialization:** Rule of law enforcement

**Capabilities:**

- Checks proposals against system policies
- Detects policy violations
- Recalls relevant policies from KB
- Flags critical compliance issues

**LLM:** Via `_ask_llm()` with policy-focused system prompt

---

### SentinelAgent

**Specialization:** Real-time risk and drift detection

**Capabilities:**

- Monitors system for drift
- Detects risk signals
- Real-time analysis
- Alert generation

---

### DocumentationAgent

**Specialization:** Professional documentation generation

**Capabilities:**

- Analyzes documentation quality
- Identifies gaps and issues
- Generates comprehensive docs
- Creates multiple files in one pass
- Enforces professional standards

**LLM:** GPT-4 Turbo (temperature: 0.2, JSON mode, max 4096 tokens)

**Key Methods:**

- `analyze_docs()` - Main entry point (not `_analyze()`)
- `_build_context()` - Smart content inclusion
- `_parse_and_validate()` - Output validation

---

## Before Creating New Agents

**Checklist:**

1. ✅ Check this registry for existing capabilities
2. ✅ Review "Identified Gaps" section
3. ✅ Determine: CREATE_NEW vs ENHANCE_EXISTING
4. ✅ Document rationale
5. ✅ Get human approval
6. ✅ Update this registry after creation

---

## Key Principles

> **Quality over Quantity**  
> Prefer enhancing existing agents over creating new ones

> **No Duplication**  
> Each capability should have a clear owner

> **Strategic Gaps Only**  
> Create new agents to fill real, identified gaps

> **Self-Documenting**  
> Keep this registry updated with all changes

---

## Updates

| Date | Change | ADR | Notes |
|------|--------|-----|-------|
| 2026-01-22 | Enhanced BuilderAgent | fc9cef1f | Added pattern learning, self-verification, retry logic |
| 2026-01-22 | Created Registry | N/A | Initial agent capability documentation |

---

## Next Steps

**Recommended Priority:**

1. **Create VerificationAgent** - Critical for code quality
2. **Create TestingAgent** - Essential for system reliability
3. **Enhance Base.Agent** - Improve learning capabilities
4. **Create RefactoringAgent** - Code quality improvement

---

## Maintenance

This registry should be updated:

- ✅ When new agents are created
- ✅ When agent capabilities are enhanced
- ✅ When gaps are identified
- ✅ When agents are deprecated

**Owner:** Development Team  
**Review Frequency:** After each significant agent change
