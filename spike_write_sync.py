import shutil
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

def write_data_sync():
    db_path = "./data/qdrant_spike"
    if Path(db_path).exists():
        shutil.rmtree(db_path)
        
    print(f"📝 Writing Data (Sync) to {db_path}...")
    
    client = QdrantClient(path=db_path)
    
    # Initialize
    client.recreate_collection(
        collection_name="icgl_memory",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    
    # Add Data
    print("   Upserting documents...")
    client.upsert(
        collection_name="icgl_memory",
        points=[
            PointStruct(
                id="c2db4b32-1111-4444-5555-666677778888",
                vector=[0.1] * 1536, # Mock vector
                payload={"content": "The Architect Agent is responsible for structural analysis."}
            )
        ]
    )
    print("   ✅ Document added.")
    client.close()

if __name__ == "__main__":
    write_data_sync()
