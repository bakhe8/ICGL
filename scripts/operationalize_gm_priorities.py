import asyncio
import sys
from pathlib import Path

# Add src to pythonpath
sys.path.append(str(Path.cwd() / "src"))

from icgl.kb import PersistentKnowledgeBase, Policy, uid, now
from icgl.memory.qdrant_adapter import QdrantAdapter, Document

async def operationalize_priorities():
    print("🚀 OPERATIONALIZING GM PRIORITIES")
    print("=================================")
    
    # 1. Connect to KB
    kb = PersistentKnowledgeBase()
    print(f"📦 Connected to KB. Current Policies: {len(kb.policies)}")
    
    # 2. Define the new 'Constitution' Policies based on GM_PRIORITIES.md
    new_policies = [
        Policy(
            id=uid(),
            code="P-GM-01",
            title="Active Memory Protocol",
            rule="Agents MUST query the Knowledge Base (kb) and Vector Memory before generating code to ensure consistency with past decisions.",
            severity="CRITICAL",
            enforced_by=["ArchitectAgent", "EngineerAgent"]
        ),
        Policy(
            id=uid(),
            code="P-GM-02",
            title="Proactive Governance Validation",
            rule="Sentinel MUST be invoked during the design phase (Proposal), not just at runtime. Architectural changes require an ADR.",
            severity="HIGH",
            enforced_by=["ICGL", "Sentinel"]
        ),
        Policy(
            id=uid(),
            code="P-GM-03",
            title="Docs-First Development",
            rule="All code changes MUST be preceded by a corresponding update to documentation or an ADR. Code follows intent, not the reverse.",
            severity="HIGH",
            enforced_by=["EngineerAgent", "PolicyAgent"]
        ),
        Policy(
            id=uid(),
            code="P-GM-04",
            title="Autonomous Execution Authority",
            rule="EngineerAgent is authorized to write files and run tests autonomously once an ADR is APPROVED by the Human.",
            severity="CRITICAL",
            enforced_by=["HDAL", "ICGL"]
        )
    ]
    
    # 3. Inject Policies into KB
    print("\n📝 Injecting Core Policies...")
    for p in new_policies:
        existing = kb.get_policy_by_code(p.code)
        if existing:
            print(f"   ⚠️ Policy {p.code} already exists. Updating...")
            # We preserve ID but update content
            p.id = existing.id
        
        kb.add_policy(p)
        print(f"   ✅ Enacted: {p.code} - {p.title}")
        
    # 4. Ingest 'Spirit of the Law' into Vector Memory
    # This allows agents to understand the *nuance* via semantic search, not just hard rules.
    print("\n🧠 Ingesting 'Priorities' into Semantic Memory...")
    try:
        memory = QdrantAdapter(path="data/qdrant_memory")
        await memory.initialize()
        
        # Read the explicit MD file
        priorities_path = Path("docs/GM_PRIORITIES.md")
        if priorities_path.exists():
            content = priorities_path.read_text(encoding="utf-8")
            
            doc = Document(
                id="doc-gm-priorities",
                content=content,
                metadata={
                    "type": "constitution",
                    "title": "General Manager Priorities",
                    "author": "Bakheet (GM)",
                    "priority": "highest"
                }
            )
            
            await memory.add_document(doc)
            print("   ✅ priorities.md ingested into Vector DB.")
        else:
            print("   ⚠️ docs/GM_PRIORITIES.md not found. Skipping vector ingestion.")
            
    except Exception as e:
        print(f"   ❌ Memory ingestion failed (is Qdrant running within process?): {e}")

    print("\n🎉 MISSION COMPLETE. The System is now aligned with new Leadership Priorities.")
    print("   Agents will now respect 'P-GM-XX' policies in all future cycles.")

if __name__ == "__main__":
    asyncio.run(operationalize_priorities())
