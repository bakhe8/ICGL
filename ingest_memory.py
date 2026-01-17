import asyncio
import sys
import os
from pathlib import Path
from icgl.kb.persistent import PersistentKnowledgeBase
from icgl.memory.qdrant_adapter import QdrantAdapter, Document
from icgl.llm.client import LLMClient

async def ingest_kb():
    print("🧠 Ingesting Knowledge Base into Semantic Memory...")
    
    # 1. Load KB
    kb = PersistentKnowledgeBase()
    stats = kb.get_stats()
    print(f"   Loaded KB with {stats['adrs']} ADRs and {stats['policies']} Policies.")
    
    # 2. Init Memory
    db_path = "data/kb.db" # Default
    mem_path = os.path.join(os.path.dirname(db_path), "qdrant_memory")
    print(f"   Target Memory Path: {mem_path}")
    
    memory = QdrantAdapter(path=mem_path)
    await memory.initialize()
    
    # 3. Ingest Policies
    print("   Processing Policies...")
    for policy in kb.policies.values():
        doc = Document(
            id=str(policy.id), # UUID
            content=f"Policy {policy.code}: {policy.title}. Rule: {policy.rule}. Severity: {policy.severity}.",
            metadata={"type": "policy", "code": policy.code}
        )
        await memory.add_document(doc)
        print(f"     + Indexed: {policy.code}")
        
    # 4. Ingest ADRs
    print("   Processing ADRs...")
    for adr in kb.adrs.values():
        doc = Document(
            id=str(adr.id),
            content=f"ADR {adr.title}. Status: {adr.status}. Decision: {adr.decision}. Context: {adr.context}.",
            metadata={"type": "adr", "status": adr.status}
        )
        await memory.add_document(doc)
        print(f"     + Indexed: {adr.title}")

    # 5. Ingest Lessons (Intervention Logs)
    print("   Processing Lessons (Interventions)...")
    interventions_path = Path("data/logs/interventions.jsonl")
    if interventions_path.exists():
        import json
        with open(interventions_path, "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                try:
                    data = json.loads(line)
                    # We store the 'mistake' (original_recommendation) so we can find it later 
                    # when a similar proposal is made.
                    idx = data.get("id") or str(count)
                    doc = Document(
                        id=f"lesson-{idx}", 
                        content=f"Human REJECTED/MODIFIED this proposal: {data.get('original_recommendation')}. REASON: {data.get('reason')}",
                        metadata={
                            "type": "lesson", 
                            "action": data.get("human_action"),
                            "reason": data.get("reason"),
                            "adr_id": data.get("adr_id")
                        }
                    )
                    await memory.add_document(doc)
                    count += 1
                except Exception as e:
                    print(f"     ⚠️ Failed to parse log line: {e}")
            print(f"     + Indexed {count} Lessons.")
    else:
        print("   No Intervention Logs found (Skipping).")
        
    print("\n✅ Ingestion Complete. Agents can now recall this knowledge.")
    
    # Close memory safely if needed
    if hasattr(memory.client, "close"):
        memory.client.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(ingest_kb())
