"""
Consensus AI — ICGL (Iterative Co-Governance Loop)
===================================================

The ICGL is the evolution engine of Consensus AI.
Orchestrates the interplay between Agents, Sentinel, Policies, and Human Authority.

Manifesto Reference:
- "ICGL: Every important decision flows through governance before execution."
"""

from typing import Optional

from ..agents import (
    ArchitectAgent,
    BuilderAgent,
    CatalystAgent,
    CodeSpecialist,
    ConceptGuardian,
    FailureAgent,
    HRAgent,
    PolicyAgent,
    Problem,
    SynthesizedResult,
    TestingAgent,
    VerificationAgent,
)
from ..agents.registry import AgentRegistry
from ..core.runtime_guard import RuntimeIntegrityGuard
from ..hdal import HDAL
from ..kb import PersistentKnowledgeBase
from ..kb.schemas import ADR, HumanDecision, LearningLog, now, uid
from ..memory.interface import Document
from ..policies import PolicyEnforcer
from ..sentinel import Sentinel


class ICGL:
    """
    ICGL: Iterative Co-Governance Loop.

    Orchestrates the full governance lifecycle:
    Proposal -> Policy Gate -> Sentinel Scan -> Agent Analysis -> Human Decision -> Knowledge Update
    """

    def __init__(
        self,
        db_path: str = "data/kb.db",
        runtime_guard: Optional[RuntimeIntegrityGuard] = None,
        enforce_runtime_guard: bool = True,
    ):
        # Enforce runtime integrity unless explicitly disabled (e.g., specialized harnesses)
        self.runtime_guard = runtime_guard
        if enforce_runtime_guard:
            self.runtime_guard = self.runtime_guard or RuntimeIntegrityGuard(
                db_path=db_path
            )
            self.runtime_guard.check()

        # 1. Initialize Kernel
        self.kb = PersistentKnowledgeBase(db_path)

        # 1.5 Initialize Sovereign Evaluator (Phase 12)
        from .evaluator import SovereignEvaluator

        self.evaluator = SovereignEvaluator()

        # 2. Initialize Memory (Cycle 2) early so Sentinel gets semantic drift context
        import os

        self.memory = None
        self._memory_bootstrapped = False
        try:
            from ..memory.lancedb_adapter import LanceDBAdapter

            mem_path = os.path.join(os.path.dirname(db_path), "lancedb")
            self.memory = LanceDBAdapter(uri=mem_path)
        except Exception as e:
            print(
                f"[ICGL] ⚠️ LanceDB not available ({e}); running without vector memory."
            )

        # 3. Initialize Guardians
        self.sentinel = Sentinel(vector_store=self.memory)
        self.enforcer = PolicyEnforcer(self.kb)
        self.hdal = HDAL()

        # 3.1 Initialize Engineer (New in Cycle 5) - with default repo
        from typing import Any

        self.engineer: Optional[Any] = None
        if os.getenv("ICGL_DISABLE_ENGINEER", "").lower() not in {"1", "true", "yes"}:
            try:
                from ..agents.engineer import EngineerAgent

                # Use current directory as default repo path
                self.engineer = EngineerAgent(repo_path=".")
            except Exception:
                self.engineer = None

        # 4. Initialize Agent Pool
        self.registry = AgentRegistry()
        self._register_internal_agents()
        # Verify decision chain integrity
        if hasattr(self.hdal, "observer"):
            ok, broken_at = self.hdal.observer.verify_merkle_chain()
            if not ok:
                print(
                    f"[WARN] Merkle chain integrity check failed at index {broken_at}"
                )

    def _register_internal_agents(self):
        """Registers the standard agent pool."""
        from ..agents.chaos import (
            ChaosAgent,  # Phase 13.4 Red Team (Safety Lock Active)
        )
        from ..agents.database_architect import (
            DatabaseArchitectAgent,  # Phase 13 Data Sovereign
        )
        from ..agents.devops import DevOpsAgent  # Sovereign Demand
        from ..agents.efficiency import EfficiencyAgent  # Phase 13.3
        from ..agents.guardian_sentinel import GuardianSentinelAgent  # Added import
        from ..agents.hdal_agent import HDALAgent
        from ..agents.knowledge_steward import KnowledgeStewardAgent  # Added import
        from ..agents.mediator import MediatorAgent
        from ..agents.refactoring import RefactoringAgent  # Added import
        from ..agents.secretary import SecretaryAgent
        from ..agents.ui_ux import UIUXAgent  # Sovereign Demand

        agents = [
            ArchitectAgent(),
            DatabaseArchitectAgent(),
            EfficiencyAgent(),
            ChaosAgent(),
            BuilderAgent(),
            FailureAgent(),
            PolicyAgent(),
            ConceptGuardian(),
            GuardianSentinelAgent(),  # Consolidated Risk & health
            CodeSpecialist(),
            TestingAgent(),
            VerificationAgent(),
            MediatorAgent(),
            HRAgent(),
            KnowledgeStewardAgent(),  # Consolidated Docs & Records
            SecretaryAgent(),
            HDALAgent(),
            RefactoringAgent(),  # New Gap Fulfillment
            CatalystAgent(),
            DevOpsAgent(),  # Phase 5 Fulfillment
            UIUXAgent(),  # Phase 5 Fulfillment
        ]
        # Add EngineerAgent if not disabled
        if self.engineer:
            agents.append(self.engineer)

        # Attach key agents for direct access
        self.architect = next(
            (a for a in agents if isinstance(a, ArchitectAgent)), None
        )
        self.builder = next((a for a in agents if isinstance(a, BuilderAgent)), None)
        self.failure = next((a for a in agents if isinstance(a, FailureAgent)), None)
        self.policy_agent = next(
            (a for a in agents if isinstance(a, PolicyAgent)), None
        )
        self.sentinel_agent = next(
            (a for a in agents if isinstance(a, GuardianSentinelAgent)), None
        )
        self.concept_guardian = next(
            (a for a in agents if isinstance(a, ConceptGuardian)), None
        )
        self.steward = next(
            (a for a in agents if isinstance(a, KnowledgeStewardAgent)), None
        )

        for agent in agents:
            # Inject Memory & Observer
            agent.memory = self.memory
            # Observer is owned by HDAL currently, maybe move to ICGL?
            # Or just access hdal.observer.
            # Let's attach it.
            if hasattr(self.hdal, "observer"):
                agent.observer = self.hdal.observer

            self.registry.register(agent)

        # Ensure memory is initialized asynchronously?
        # ICGL.run_governance_cycle is async, so we can ensure init there or assume it's lazy/fast.
        # Qdrant local init is synchronous usually (file check), but adapter has async .initialize()
        # We should call initialize() somewhere. Best in the first run or async init method.

    async def run_governance_cycle(
        self, adr: ADR, human_id: str
    ) -> Optional[HumanDecision]:
        """
        Executes a complete governance cycle for a proposed ADR.

        Lifecycle:
        1. Policy Gate (Hard Stop)
        2. Sentinel Scan (Risk Detection)
        3. Agent Analysis (Multi-perspective reasoning)
        4. Human Sovereign Decision (HDAL)
        5. Knowledge Base Update
        """
        # Ensure memory is ready
        if self.memory:
            try:
                await self.memory.initialize()
                await self._bootstrap_memory()
            except Exception as e:
                print(
                    f"[ICGL] ⚠️ Memory init failed ({e}); continuing without vector memory."
                )

        print(f"\n[ICGL] 🔁 Starting Governance Cycle for: {adr.title}")

        # ---------------------------------------------------------
        # Phase 1: Policy Gate
        # ---------------------------------------------------------
        print("[ICGL] 🔒 Phase 1: Policy Enforcement Gate...")
        policy_report = self.enforcer.check_adr_compliance(adr)

        if policy_report.status == "FAIL":
            print("   ⛔ CRITICAL POLICY VIOLATION. Stopping.")
            return None
        elif policy_report.status == "ESCALATE":
            print("   ⚠️ Policy Violation Detected (ESCALATING to HDAL).")
        else:
            print("   ✅ Policy Check Passed.")

        # ---------------------------------------------------------
        # Phase 2 & 3: Dynamic Council Assembly (Cycle 15)
        # ---------------------------------------------------------
        print("[ICGL] 🧠 Phase 2: Dynamic Council Assembly...")

        # Create a "Problem" definition from the ADR
        problem = Problem(
            title=adr.title,
            context=adr.context,
            metadata={"adr_id": adr.id, "decision": adr.decision},
        )

        sentinel_alerts = await self.sentinel.scan_adr_detailed_async(adr, self.kb)

        # 2a. Run Architect & Secretary First (The "Core")
        # Note: Secretary has already "spoken" if this came from the idea-run API, but here we synthesize.
        # Ideally, we run the "Registry" in two passes.

        # Pass 1: Architect (to determine required agents)
        # We manually invoke Architect from the registry
        architect_result = await self.registry.run_single_agent(
            "agent-architect", problem, self.kb
        )
        secretary_result = await self.registry.run_single_agent(
            "secretary", problem, self.kb
        )  # for context

        if not architect_result:
            print("⚠️ Architect failed to run. Falling back to Full Council.")
            council_agents = None  # All
        else:
            # Extract Required Agents
            required_agents = getattr(architect_result, "required_agents", [])
            rationale = getattr(architect_result, "summoning_rationale", "No rationale")

            if not required_agents:
                print(
                    "⚠️ Architect requested NO agents. Defaulting to Core (Sentinel/Failure)."
                )
                required_agents = ["sentinel", "failure", "policy"]

            print(f"   🏛️  Architect Summons Council: {required_agents}")
            print(f"   📜  Rationale: {rationale}")

            # Convert to registry filters (agent_id or role)
            # We assume Architect returns roles or IDs. We map broadly.
            council_agents = required_agents

        # Pass 2: The Council (Filtered)
        # We always verify Sentinel/Policy/Guardian exist in the loop for safety,
        # but Cycle 15 says Architect has power. We trust the Architect, but trigger Sentinel if risky.

        synthesis: SynthesizedResult = await self.registry.run_and_synthesize_dynamic(
            problem,
            self.kb,
            allowed_agents=council_agents,
            precomputed_results=[r for r in [architect_result, secretary_result] if r],
        )

        print(
            f"   ✅ Council Analysis Complete. Confidence: {synthesis.overall_confidence:.0%}"
        )

        # ---------------------------------------------------------
        # Phase 4: Human Sovereign Decision
        # ---------------------------------------------------------
        print("[ICGL] 🏛️  Phase 3: Human Sovereign Authority (HDAL)...")

        # Pass reports to UI
        decision = self.hdal.review_and_sign(
            adr,
            synthesis,
            human_id,
            policy_report=policy_report,
            sentinel_alerts=sentinel_alerts,
        )

        if not decision:
            print("[ICGL] ⏹️  Cycle Terminated (No Decision Signed).")
            return None

        # ---------------------------------------------------------
        # Phase 5: Knowledge Base Update
        # ---------------------------------------------------------
        print(f"[ICGL] 💾 Phase 4: Knowledge Persistence ({decision.action})...")

        # Update ADR status
        if decision.action == "APPROVE":
            adr.status = "ACCEPTED"
        elif decision.action == "REJECT":
            adr.status = "REJECTED"
        elif decision.action == "EXPERIMENT":
            adr.status = "EXPERIMENTAL"

        adr.human_decision_id = decision.id

        # Persist everything
        self.kb.add_adr(adr)  # Updates status
        self.kb.add_human_decision(decision)
        # Record decision chain
        self.hdal.observer.record_decision(
            {
                "adr_id": adr.id,
                "decision_id": decision.id,
                "action": decision.action,
                "rationale": decision.rationale,
                "signed_by": decision.signed_by,
                "timestamp": decision.timestamp,
                "signature_hash": decision.signature_hash,
            }
        )

        # 🧠 Synchronize Memory (Cycle 2/3/8)
        # We index the ADR content and the Decision Rationale
        from ..memory.interface import Document

        memory_content = f"ADR: {adr.title}\nContext: {adr.context}\nDecision: {decision.action}\nRationale: {decision.rationale}"
        mem = getattr(self, "memory", None)
        if mem is not None and hasattr(mem, "add_document"):
            await mem.add_document(
                Document(
                    id=f"adr-{adr.id}",
                    content=memory_content,
                    metadata={
                        "type": "adr",
                        "status": adr.status,
                        "action": decision.action,
                    },
                )
            )

        # Create Learning Log
        log = LearningLog(
            cycle=len(self.kb.learning_log) + 1,
            summary=f"Processed ADR {adr.id}: {adr.title}",
            new_policies=adr.related_policies,  # Simplified logic
            new_signals=[],
            new_concepts=[],
            notes=f"Decision: {decision.action}. Rationale: {decision.rationale}",
        )
        self.kb.add_learning_log(log)

        # Phase 12: Unified Schema (Lessons -> Kernel)
        if self.steward and hasattr(self.steward, "generate_structured_lesson"):
            await self.steward.generate_structured_lesson(log)

        # ---------------------------------------------------------
        # Phase 6: Run Logging (JSON)
        # ---------------------------------------------------------
        self._log_run_json(adr, synthesis, decision, log)

        # ---------------------------------------------------------
        # Phase 7: Engineer (GitOps)
        # ---------------------------------------------------------
        if decision.action == "APPROVE" and getattr(self, "engineer", None):
            print("[DEBUG] Engineer detected. checking results...")
            all_changes = []
            for res in synthesis.individual_results:
                if hasattr(res, "file_changes") and res.file_changes:
                    print(
                        f"[DEBUG] Found {len(res.file_changes)} changes in agent {res.agent_id}"
                    )
                    all_changes.extend(res.file_changes)

            if all_changes:
                print(f"[ICGL] 👷 Executing {len(all_changes)} Runtime Changes...")
                eng = getattr(self, "engineer", None)
                if eng is not None:
                    for change in all_changes:
                        write = getattr(eng, "write_file", None)
                        if callable(write):
                            write(change.path, change.content)

                    commit = getattr(eng, "commit_decision", None)
                    if callable(commit):
                        commit_hash = commit(adr, decision)
                        if commit_hash and hasattr(self.hdal, "observer"):
                            self.hdal.observer.record_decision(
                                {
                                    "adr_id": adr.id,
                                    "decision_id": decision.id,
                                    "action": decision.action,
                                    "rationale": decision.rationale,
                                    "signed_by": decision.signed_by,
                                    "timestamp": decision.timestamp,
                                    "signature_hash": decision.signature_hash,
                                    "commit_hash": commit_hash,
                                }
                            )

        print(f"[ICGL] ✅ Cycle #{log.cycle} Completed Successfully.")
        return decision

    async def _bootstrap_memory(self):
        """Ingest KB and lessons into memory once per engine lifecycle."""
        if (
            self._memory_bootstrapped
            or not self.memory
            or getattr(self.memory, "mock_mode", False)
        ):
            self._memory_bootstrapped = True
            return
        # Index policies and ADRs
        mem = getattr(self, "memory", None)
        # Index policies
        for policy in self.kb.policies.values():
            if mem is not None and hasattr(mem, "add_document"):
                await mem.add_document(
                    Document(
                        id=policy.id,
                        content=f"Policy {policy.code}: {policy.title}. Rule: {policy.rule}. Severity: {policy.severity}",
                        metadata={"type": "policy", "code": policy.code},
                    )
                )

        # Index ADRs
        for adr in self.kb.adrs.values():
            if mem is not None and hasattr(mem, "add_document"):
                await mem.add_document(
                    Document(
                        id=adr.id,
                        content=f"ADR {adr.title}. Status: {adr.status}. Decision: {adr.decision}. Context: {adr.context}",
                        metadata={"type": "adr", "status": adr.status},
                    )
                )
        # Index lessons/interventions
        import json
        from pathlib import Path

        lessons_path = Path("data/logs/interventions.jsonl")
        if lessons_path.exists():
            with open(lessons_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if mem is not None and hasattr(mem, "add_document"):
                            await mem.add_document(
                                Document(
                                    id=f"lesson-{data.get('id', uid())}",
                                    content=f"Human {data.get('human_action')} proposal: {data.get('original_recommendation')} Reason: {data.get('reason')}",
                                    metadata={
                                        "type": "lesson",
                                        "adr_id": data.get("adr_id"),
                                    },
                                )
                            )
                    except Exception:
                        continue
        self._memory_bootstrapped = True

    def _log_run_json(self, adr, synthesis, decision, log):
        """Saves detailed run artifacts to JSON."""
        import json
        from dataclasses import asdict
        from pathlib import Path

        run_data = {
            "timestamp": now(),
            "cycle_id": log.cycle,
            "human_id": decision.signed_by,
            "adr": asdict(adr),
            "synthesis": {
                "overall_confidence": synthesis.overall_confidence,
                "consensus_recommendations": synthesis.consensus_recommendations,
                "all_concerns": synthesis.all_concerns,
                "agent_results": [asdict(r) for r in synthesis.individual_results],
            },
            "decision": asdict(decision),
        }

        # Ensure 'role' Enum is serialized correctly
        # Simple recursion to fix Enums isn't robust, so explicit fix for AgentRole
        for result in run_data["synthesis"]["agent_results"]:
            if hasattr(result["role"], "value"):
                result["role"] = result["role"].value

        file_name = f"run_{log.cycle:04d}_{adr.id}.json"
        path = Path("runs") / file_name
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(run_data, f, indent=2, ensure_ascii=False)

        print(f"[ICGL] 📝 Run log saved to: {path}")
