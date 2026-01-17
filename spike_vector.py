import asyncio
import sys
from pathlib import Path
from icgl.memory.qdrant_adapter import QdrantAdapter, Document

async def write_data(db_path):
    print("📝 Phase 1: Writing Data...")
    adapter = QdrantAdapter(path=db_path)
    # Ensure collection created
    await adapter.initialize() 
    
    doc1 = Document(
        id="c2db4b32-uuid-4444-5555-666677778888", 
        content="The Architect Agent is responsible for structural analysis.", 
        metadata={"role": "architect"}
    )
    doc2 = Document(
        id="d3ec5c43-uuid-4444-5555-666677778888", 
        content="The Sentinel Agent guards against authority leakage.", 
        metadata={"role": "sentinel"}
    )
    
    await adapter.add_document(doc1)
    await adapter.add_document(doc2)
    print("   ✅ Documents added.")
    # Force close if possible (client dependent)
    if hasattr(adapter.client, "close"):
        adapter.client.close()

async def verify_data(db_path):
    print("🔄 Phase 2: Verifying Persistence (New Instance)...")
    adapter = QdrantAdapter(path=db_path)
    
    # 3. Verify Persistence via Search
    print("🔍 Phase 3: Verifying Semantic Recall...")
    query = "Who checks for structural issues?"
    results = await adapter.search(query)
    
    found = False
    for res in results:
        print(f"   Hit: {res.document.content} (Score: {res.score:.4f})")
        if "Architect" in res.document.content:
            found = True
            
    if found:
        print("\n✅ SPIKE SUCCESS: Semantic Recall Verified & Data Persisted.")
    else:
        print("\n❌ SPIKE FAILED: Expected document not found or low score.")

async def run_spike():
    print("🧪 Starting Validation Spike: Qdrant Persistence & Adapter...")
    
    # Setup Paths
    db_path = "./data/qdrant_spike"
    
    # Only clean if arg provided, otherwise keep for persistence check across runs
    import shutil
    if Path(db_path).exists():
        shutil.rmtree(db_path)
    
    print(f"📂 Storage Path: {db_path}")

    # Write
    await write_data(db_path)
    
    # Verify in same process (simulating new instance via new object)
    await verify_data(db_path)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_spike())
