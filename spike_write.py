import asyncio
import sys
from pathlib import Path
from icgl.memory.qdrant_adapter import QdrantAdapter, Document
import shutil

async def write_data():
    db_path = "./data/qdrant_spike"
    if Path(db_path).exists():
        shutil.rmtree(db_path)
        
    print(f"📝 Writing Data to {db_path}...")
    adapter = QdrantAdapter(path=db_path)
    await adapter.initialize()
    
    doc1 = Document(
        id="c2db4b32-uuid-4444-5555-666677778888", 
        content="The Architect Agent is responsible for structural analysis.", 
        metadata={"role": "architect"}
    )
    
    await adapter.add_document(doc1)
    print("   ✅ Document added.")
    # Attempt clean close
    if hasattr(adapter.client, "close"):
        adapter.client.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(write_data())
