import asyncio
import sys
from icgl.memory.qdrant_adapter import QdrantAdapter

async def verify_data():
    db_path = "./data/qdrant_spike"
    print(f"🔍 Verifying Data in {db_path}...")
    
    adapter = QdrantAdapter(path=db_path)
    # verify persistence explicitly
    
    query = "Who checks for structural issues?"
    results = await adapter.search(query)
    
    found = False
    for res in results:
        print(f"   Hit: {res.document.content} (Score: {res.score:.4f})")
        if "Architect" in res.document.content:
            found = True
            
    with open("spike_result.txt", "w") as f:
        if found:
            print("\n✅ SPIKE SUCCESS: Data Persisted across processes.")
            f.write("SUCCESS")
        else:
            print("\n❌ SPIKE FAILED: Document not found.")
            f.write("FAILURE")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_data())
